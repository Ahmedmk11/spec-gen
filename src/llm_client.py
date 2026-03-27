import os
from langchain.chat_models import init_chat_model

def get_env_model():
    model = os.getenv("ANTHROPIC_MODEL")
    if not model:
        raise ValueError("Model is not set")
    return model

class LLMClient:
    def __init__(self, tools: list | None = None, schema=None) -> None:
        base = init_chat_model(
            model=get_env_model(),
            model_kwargs={"cache_control": {"type": "ephemeral"}},
        )

        if schema:
            self.llm = base.with_structured_output(schema)
        else:
            self.llm = base.bind_tools(tools if tools else [])

    async def ainvoke(self, messages):
        return await self.llm.ainvoke(messages)
