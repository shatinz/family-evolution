"""
Core Configuration Module for Scalable Family Evolution System
"""
import os
import json
from pathlib import Path
from dataclasses import dataclass, asdict, field

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CONFIG_FILE = DATA_DIR / "config.json"

@dataclass
class AppConfig:
    # Telegram Bot Settings (Read from env or config.json)
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_proxy: str = os.getenv("TELEGRAM_PROXY", "socks5h://127.0.0.1:10808")
    use_proxy: bool = False
    
    # LLM Settings (OpenAI format or Gemini)
    llm_provider: str = os.getenv("LLM_PROVIDER", "gemini_native")  # 'openai_compatible' or 'gemini_native'
    llm_base_url: str = os.getenv("LLM_BASE_URL", "http://localhost:20128/v1")
    llm_model: str = os.getenv("LLM_MODEL", "gemini-2.5-flash")
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    
    # Web Dashboard Settings
    web_host: str = "127.0.0.1"
    web_port: int = 5055
    language: str = "fa"  # 'fa' or 'en'
    
    # Scheduling Timers (24h format)
    morning_checkin_time: str = "09:00"
    evening_checkin_time: str = "20:00"
    weekly_meeting_day: str = "Sunday"
    weekly_meeting_time: str = "19:30"
    
    # Storage
    db_path: str = str(DATA_DIR / "family.db")

    @property
    def BASE_DIR(self) -> Path:
        return BASE_DIR

    def save(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        data_to_save = {k: v for k, v in asdict(self).items() if not k.startswith("_")}
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls) -> "AppConfig":
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return cls(**data)
            except Exception:
                pass
        config = cls()
        config.save()
        return config

config = AppConfig.load()
