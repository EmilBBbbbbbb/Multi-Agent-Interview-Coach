import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    BASE_DIR = Path(__file__).parent.parent
    LOGS_DIR = BASE_DIR / "logs"
    
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openrouter")
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_CHEAP_MODEL = os.getenv("OPENAI_CHEAP_MODEL", "gpt-3.5-turbo")
    
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    ANTHROPIC_CHEAP_MODEL = os.getenv("ANTHROPIC_CHEAP_MODEL", "claude-3-haiku-20240307")
    
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-120b:free")
    OPENROUTER_CHEAP_MODEL = os.getenv("OPENROUTER_CHEAP_MODEL", "openai/gpt-oss-120b:free")
    
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
    MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-small-latest")
    MISTRAL_CHEAP_MODEL = os.getenv("MISTRAL_CHEAP_MODEL", "mistral-small-latest")
    
    LOG_INTERNAL_THOUGHTS = os.getenv("LOG_INTERNAL_THOUGHTS", "true").lower() == "true"
    MAX_INTERVIEW_TURNS = int(os.getenv("MAX_INTERVIEW_TURNS", "20"))
    DIFFICULTY_MIN = int(os.getenv("DIFFICULTY_MIN", "1"))
    DIFFICULTY_MAX = int(os.getenv("DIFFICULTY_MAX", "5"))
    
    PERFORMANCE_THRESHOLD_HIGH = 0.8
    PERFORMANCE_THRESHOLD_LOW = 0.4
    CONTEXT_WINDOW_SIZE = 5

settings = Settings()
