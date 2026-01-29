from abc import ABC, abstractmethod
from typing import Optional
import requests
from config import settings


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None, 
                 temperature: float = 0.7, max_tokens: int = 1000) -> str:
        pass


class OpenAIProvider(LLMProvider):
    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None):
        from openai import OpenAI
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL
        self.client = OpenAI(api_key=self.api_key)
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None,
                 temperature: float = 0.7, max_tokens: int = 1000) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content


class AnthropicProvider(LLMProvider):
    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None):
        from anthropic import Anthropic
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.model = model or settings.ANTHROPIC_MODEL
        self.client = Anthropic(api_key=self.api_key)
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None,
                 temperature: float = 0.7, max_tokens: int = 1000) -> str:
        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt or "",
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text


class MistralProvider(LLMProvider):
    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None):
        from mistralai import Mistral
        self.api_key = api_key or settings.MISTRAL_API_KEY
        self.model = model or settings.MISTRAL_MODEL
        self.client = Mistral(api_key=self.api_key)
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None,
                 temperature: float = 0.7, max_tokens: int = 1000) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.complete(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content


class OpenRouterProvider(LLMProvider):
    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OPENROUTER_API_KEY
        self.model = model or settings.OPENROUTER_MODEL
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None,
                 temperature: float = 0.7, max_tokens: int = 1000) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if "choices" not in result or not result["choices"]:
                print(f"OpenRouter API Error: {result}")
                return "Извините, произошла техническая ошибка. Попробуйте еще раз."
            
            message = result["choices"][0]["message"]
            content = message.get("content", "")
            
            # Некоторые модели (например, reasoning models) возвращают текст в поле reasoning
            if not content or not content.strip():
                reasoning = message.get("reasoning", "")
                if reasoning and reasoning.strip():
                    # Reasoning модели пишут размышления на английском, а финальный ответ в конце
                    # Ищем финальный русский текст после фраз типа "Let's produce:", "Better:", "Ok."
                    
                    # Разбиваем на абзацы
                    lines = reasoning.split('\n')
                    
                    # Ищем последние строки на русском (после английских рассуждений)
                    russian_lines = []
                    for line in reversed(lines):
                        line = line.strip()
                        if not line:
                            continue
                        # Проверяем, есть ли кириллица
                        if any('\u0400' <= char <= '\u04FF' for char in line):
                            russian_lines.insert(0, line)
                        elif russian_lines:  # Если уже нашли русский текст, останавливаемся
                            break
                    
                    if russian_lines:
                        content = ' '.join(russian_lines)
                    else:
                        # Если русского не нашли, берем последнее предложение
                        sentences = [s.strip() for s in reasoning.split('.') if s.strip()]
                        if sentences:
                            content = sentences[-1] + '.'
                        else:
                            content = reasoning[:200]  # Первые 200 символов
            
            if not content or not content.strip():
                print(f"OpenRouter returned empty response: {result}")
                return "Извините, получен пустой ответ. Попробуйте еще раз."
            
            return content.strip()
        except requests.exceptions.RequestException as e:
            print(f"OpenRouter Request Error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return "Извините, не удалось связаться с сервером. Проверьте интернет-соединение."


class LLMFactory:
    @staticmethod
    def create_provider(provider_type: Optional[str] = None, 
                       use_cheap: bool = False) -> LLMProvider:
        provider_type = provider_type or settings.LLM_PROVIDER
        
        if provider_type == "openai":
            model = settings.OPENAI_CHEAP_MODEL if use_cheap else settings.OPENAI_MODEL
            return OpenAIProvider(model=model)
        elif provider_type == "anthropic":
            model = settings.ANTHROPIC_CHEAP_MODEL if use_cheap else settings.ANTHROPIC_MODEL
            return AnthropicProvider(model=model)
        elif provider_type == "mistral":
            model = settings.MISTRAL_CHEAP_MODEL if use_cheap else settings.MISTRAL_MODEL
            return MistralProvider(model=model)
        elif provider_type == "openrouter":
            model = settings.OPENROUTER_CHEAP_MODEL if use_cheap else settings.OPENROUTER_MODEL
            return OpenRouterProvider(model=model)
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")
    
    @staticmethod
    def create_cheap_provider(provider_type: Optional[str] = None) -> LLMProvider:
        return LLMFactory.create_provider(provider_type, use_cheap=True)
