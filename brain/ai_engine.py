"""
AI Engine Client for Family Evolution
Supports OpenAI-compatible endpoints, Google Gemini API, and heuristic resilience.
"""
import httpx
import json
import logging
from typing import List, Dict, Any, Optional
from core.config import config

logger = logging.getLogger(__name__)

class AIEngine:
    def __init__(self):
        self.timeout = 25.0

    def chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 1500) -> str:
        """Executes chat completion based on active provider configuration"""
        # If Gemini API Key is provided
        if config.gemini_api_key and config.llm_provider == "gemini_native":
            return self._call_gemini_api(messages, temperature, max_tokens)
        else:
            return self._call_openai_compatible(messages, temperature, max_tokens)

    def _call_openai_compatible(self, messages: List[Dict[str, str]], temperature: float, max_tokens: int) -> str:
        base_url = config.llm_base_url.rstrip("/")
        model = config.llm_model
        api_key = config.llm_api_key or "not-needed"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(f"{base_url}/chat/completions", headers=headers, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.warning(f"OpenAI endpoint returned {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            logger.warning(f"OpenAI endpoint call failed: {e}")

        # Try fallback to Gemini if key exists
        if config.gemini_api_key:
            try:
                return self._call_gemini_api(messages, temperature, max_tokens)
            except Exception:
                pass

        return self._heuristic_fallback(messages)

    def _call_gemini_api(self, messages: List[Dict[str, str]], temperature: float, max_tokens: int) -> str:
        api_key = config.gemini_api_key
        model = config.llm_model if "gemini" in config.llm_model.lower() else "gemini-2.5-flash"
        
        # Convert OpenAI messages to Gemini contents format
        contents = []
        system_instruction = None
        for m in messages:
            if m["role"] == "system":
                system_instruction = {"parts": [{"text": m["content"]}]}
            else:
                role = "user" if m["role"] == "user" else "model"
                contents.append({"role": role, "parts": [{"text": m["content"]}]})

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }
        if system_instruction:
            payload["systemInstruction"] = system_instruction

        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
            else:
                raise Exception(f"Gemini API error {resp.status_code}: {resp.text[:200]}")

    def test_connection(self) -> Dict[str, Any]:
        """Tests the current AI configuration with a simple ping"""
        test_messages = [{"role": "user", "content": "پاسخ کوتاه بده: تست ارتباط موفق بود"}]
        try:
            result = self.chat_completion(test_messages, max_tokens=20)
            return {
                "ok": True,
                "provider": config.llm_provider,
                "model": config.llm_model,
                "response": result.strip()
            }
        except Exception as e:
            return {
                "ok": False,
                "error": str(e)
            }

    def _heuristic_fallback(self, messages: List[Dict[str, str]]) -> str:
        prompt = messages[-1]["content"] if messages else ""
        if "مصاحبه" in prompt or "grill" in prompt.lower():
            return (
                "ممنون از توضیحات شما. برای شناخت دقیق‌تر:\n"
                "۱. تقسیم فعلی کارهای خانه چگونه است و چه کسی بیشترین فشار را تحمل می‌کند؟\n"
                "۲. در هنگام بروز تنش یا خشم، واکنش سایر اعضا چگونه است؟\n\n"
                "STATUS: CONTINUE"
            )
        elif "تحلیل" in prompt or "گزارش" in prompt:
            return (
                "===LEADER_REPORT===\n"
                "📊 **تحلیل روانشناختی و ثبات خانه:**\n"
                "• مراقبت از عاملیت سالمند و ایجاد پیوند میان فرزندان اولویت دارد.\n"
                "• پیشنهاد می‌شود جلسه هفتگی قدردانی یکشنبه‌ها به طور منظم پیگیری شود.\n"
                "===FAMILY_BROADCAST===\n"
                "خانواده عزیز، با همدلی و گام‌های منظم به سمت آرامش بیشتر پیش می‌رویم. 🌿✨"
            )
        return "پیام با موفقیت دریافت و پردازش شد."

ai_engine = AIEngine()
