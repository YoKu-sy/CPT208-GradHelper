from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

from openai import OpenAI
from ragflow_sdk.modules.chat import Chat

from app.core.config import get_settings
from app.core.errors import AppError
from app.core.logging import get_logger
from app.services.ragflow_client import RAGFlowClient, get_ragflow_client

logger = get_logger(__name__)


class LLMService:
    def __init__(self, ragflow_client: RAGFlowClient | None = None) -> None:
        self._settings = get_settings()
        self._ragflow_client = ragflow_client or get_ragflow_client()

    def generate_answer(self, system_prompt: str, user_prompt: str) -> str:
        provider = self._settings.llm_provider.strip().lower()
        if provider == "openai_compatible":
            return self._generate_via_openai_compatible(system_prompt=system_prompt, user_prompt=user_prompt)
        return self._run_with_timeout(
            lambda: self._generate_via_ragflow_chat(system_prompt=system_prompt, user_prompt=user_prompt)
        )

    def _run_with_timeout(self, operation):
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(operation)
            try:
                return future.result(timeout=self._settings.llm_timeout_seconds)
            except FutureTimeoutError as exc:
                future.cancel()
                raise AppError(
                    message=f"LLM call exceeded timeout of {self._settings.llm_timeout_seconds} seconds.",
                    status_code=504,
                    code="LLM_TIMEOUT",
                ) from exc

    def _generate_via_openai_compatible(self, system_prompt: str, user_prompt: str) -> str:
        if not self._settings.llm_api_key or not self._settings.llm_base_url:
            raise AppError(
                message="LLM_PROVIDER=openai_compatible requires both LLM_API_KEY and LLM_BASE_URL.",
                status_code=500,
                code="LLM_CONFIG_INVALID",
            )

        try:
            client = OpenAI(api_key=self._settings.llm_api_key, base_url=self._settings.llm_base_url)
            response = client.chat.completions.create(
                model=self._settings.llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self._settings.llm_temperature,
                top_p=self._settings.llm_top_p,
                max_tokens=self._settings.llm_max_tokens,
            )
        except Exception as exc:
            raise AppError(
                message=f"OpenAI-compatible LLM call failed: {exc}",
                status_code=502,
                code="LLM_CALL_FAILED",
            ) from exc

        answer = response.choices[0].message.content if response.choices else None
        if not answer:
            raise AppError(
                message="LLM returned an empty response.",
                status_code=502,
                code="LLM_EMPTY_RESPONSE",
            )
        logger.info("Generated answer via openai_compatible model=%s", self._settings.llm_model)
        return answer.strip()

    def _generate_via_ragflow_chat(self, system_prompt: str, user_prompt: str) -> str:
        rag = self._ragflow_client.sdk
        llm = Chat.LLM(
            rag,
            {
                "model_name": self._settings.llm_model,
                "temperature": self._settings.llm_temperature,
                "top_p": self._settings.llm_top_p,
                "presence_penalty": 0.0,
                "frequency_penalty": 0.0,
                "max_tokens": self._settings.llm_max_tokens,
            },
        )
        prompt = Chat.Prompt(
            rag,
            {
                "prompt": system_prompt,
                "opener": "RAG session",
                "show_quote": False,
            },
        )

        chat = None
        try:
            chat = rag.create_chat(name="cpt208-rag-chat", dataset_ids=[], llm=llm, prompt=prompt)
            session = chat.create_session(name="cpt208-rag-session")
            message = next(session.ask(user_prompt, stream=False))
            answer = (message.content or "").strip()
        except Exception as exc:
            raise AppError(
                message=f"RAGFlow chat LLM call failed: {exc}",
                status_code=502,
                code="LLM_CALL_FAILED",
            ) from exc
        finally:
            if chat is not None:
                try:
                    rag.delete_chats(ids=[chat.id])
                except Exception:
                    pass

        if not answer:
            raise AppError(
                message="LLM returned an empty response.",
                status_code=502,
                code="LLM_EMPTY_RESPONSE",
            )
        logger.info("Generated answer via ragflow_chat model=%s", self._settings.llm_model)
        return answer
