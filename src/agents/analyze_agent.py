import os

from langchain.chat_models import init_chat_model

# def get_env_model():
#     model = os.getenv("ANTHROPIC_MODEL")
#     if not model:
#         raise ValueError("Model is not set")
#     return model

# class LLMClient:
#     def __init__(self, temperature: float = 0, tools: list | None = None) -> None:
#         self.llm = init_chat_model(
#             model=get_env_model(),
#             temperature=temperature,
#             model_kwargs={
#                 "cache_control": {"type": "ephemeral"}
#             },
#         ).bind_tools(tools if tools else [])