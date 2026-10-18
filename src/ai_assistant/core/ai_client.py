import asyncio
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[3] / ".env")

OLLAMA_URL = os.getenv("OLLAMA_URL")
MODEL_FOR_CODE_OLLAMA = os.getenv("MODEL_FOR_CODE_OLLAMA")
MODEL_FOR_REFLECTION_OLLAMA = os.getenv("MODEL_FOR_REFLECTION_OLLAMA")
TEMPERATURE_FOR_CODE = os.getenv("TEMPERATURE_FOR_CODE", "0.0")
TEMPERATURE_FOR_REFLECTION = os.getenv("TEMPERATURE_FOR_REFLECTION", "0.7")


class BaseAIClient:
    """Базовый клиент, содержащий общую логику отправки POST-запросов."""

    def __init__(self, base_url: str, headers: dict):
        self.base_url = base_url
        self.headers = headers

    async def _send_request(self, payload: dict) -> str:
        """Внутренний метод для отправки асинхронного запроса через httpx."""
        last_error = ""
        async with httpx.AsyncClient() as client:
            for attempt in range(3):
                if attempt > 0:
                    await asyncio.sleep(2**attempt)
                try:
                    response = await client.post(
                        self.base_url, headers=self.headers, json=payload, timeout=90.0
                    )
                    response.raise_for_status()

                    result_json = response.json()
                    return result_json["choices"][0]["message"]["content"]

                except httpx.HTTPStatusError as e:
                    last_error = (
                        f"Ошибка API: {e.response.status_code} - {e.response.text}"
                    )
                    if e.response.status_code < 500:
                        raise RuntimeError(last_error)
                except httpx.RequestError as e:
                    last_error = f"Ошибка сети: {e}"
        raise RuntimeError(f"После 3 попыток: {last_error}")


class OllamaClient(BaseAIClient):
    """Клиент для работы с локальной Ollama (поддерживает любые локальные модели)."""

    def __init__(self):
        super().__init__(
            base_url=OLLAMA_URL + "/v1/chat/completions",
            headers={"Content-Type": "application/json"},
        )

    MODES = {
        "code": (MODEL_FOR_CODE_OLLAMA, float(TEMPERATURE_FOR_CODE)),
        "reflection": (MODEL_FOR_REFLECTION_OLLAMA, float(TEMPERATURE_FOR_REFLECTION)),
    }

    async def ask(self, prompt: str, mode: str = "code") -> str:
        if mode not in self.MODES:
            return f"Неизвестный режим: {mode}"
        model, temperature = self.MODES[mode]
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "stream": False,
        }
        return await self._send_request(payload)

    async def healthcheck(self) -> bool:
        """Метод для проверки доступности Ollama"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{OLLAMA_URL}/api/tags", timeout=3.0)
                return response.status_code == 200
            except httpx.RequestError:
                return False


def get_ai_client(provider: str):
    """Фабричная функция, которая возвращает готовый объект нужного клиента."""
    provider = provider.lower()

    if provider == "ollama":
        return OllamaClient()
    # elif provider == "openai":
    #     return OpenAIClient()
    # elif provider == "anthropic":
    #     return AnthropicClient()
    else:
        raise ValueError(f"Неизвестный провайдер: {provider}")
