import sys
from typing import Any, Dict, List, Literal

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.errors import GraphRecursionError
from langgraph.prebuilt import create_react_agent
from openai import OpenAI
from pydantic import BaseModel, Field

from .art_agent import _resolve_api_key, system_message_content
from .tools import TOOL_SCHEMAS, ToolExecutor

_CHECKPOINTER = InMemorySaver()


def _schema_for(name: str) -> Dict[str, Any]:
    return next(s["function"] for s in TOOL_SCHEMAS if s["function"]["name"] == name)


def _build_tools(executor: ToolExecutor) -> List[StructuredTool]:
    schema_get_metadata = _schema_for("get_artwork_metadata")
    schema_describe = _schema_for("describe_artwork_region")
    schema_update = _schema_for("update_user_persona")
    describe_props = schema_describe["parameters"]["properties"]
    update_props = schema_update["parameters"]["properties"]

    class DescribeRegionArgs(BaseModel):
        region: str = Field(description=describe_props["region"]["description"])
        user_question: str = Field(default="", description=describe_props["user_question"]["description"])

    class UpdatePersonaArgs(BaseModel):
        key: str = Field(description=update_props["key"]["description"])
        value: str = Field(description=update_props["value"]["description"])
        source: Literal["explicit", "inferred"] = Field(description=schema_update["description"])
        reason: str = Field(default="", description=update_props["reason"]["description"])

    def get_artwork_metadata() -> str:
        return executor._get_metadata()

    def describe_artwork_region(region: str, user_question: str = "") -> str:
        return executor._describe_region(region, user_question)

    def update_user_persona(key: str, value: str, source: str, reason: str = "") -> str:
        return executor._update_persona({"key": key, "value": value, "source": source, "reason": reason})

    return [
        StructuredTool.from_function(
            func=get_artwork_metadata,
            name="get_artwork_metadata",
            description=schema_get_metadata["description"],
        ),
        StructuredTool.from_function(
            func=describe_artwork_region,
            name="describe_artwork_region",
            description=schema_describe["description"],
            args_schema=DescribeRegionArgs,
        ),
        StructuredTool.from_function(
            func=update_user_persona,
            name="update_user_persona",
            description=schema_update["description"],
            args_schema=UpdatePersonaArgs,
        ),
    ]


class _DebugCallbackHandler(BaseCallbackHandler):
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> None:
        name = serialized.get("name", "?")
        print(f"[debug] tool_call -> {name}({input_str})", file=sys.stderr)

    def on_tool_end(self, output: Any, **kwargs: Any) -> None:
        text = str(output)
        preview = text if len(text) <= 300 else text[:300] + " ...(truncated)"
        print(f"[debug] tool_result <- {preview}", file=sys.stderr)


class ArtAgentLC:
    """LangGraph(create_react_agent) 기반으로 재구현한 ArtAgent. 인터페이스는 ArtAgent와 동일."""

    def __init__(
        self,
        user_id: str,
        artwork_id: str,
        model: str = "gpt-4o",
        debug: bool = False,
        thread_id: str | None = None,
    ):
        api_key = _resolve_api_key()
        self.user_id = user_id
        self.artwork_id = artwork_id
        self.thread_id = thread_id or f"{user_id}:{artwork_id}"
        self.debug = debug
        self.llm = ChatOpenAI(model=model, api_key=api_key)
        self.tools_executor = ToolExecutor(OpenAI(api_key=api_key), user_id, artwork_id)
        self.tools = _build_tools(self.tools_executor)
        self.history: List[BaseMessage] = []

    def _current_system_content(self) -> str:
        return system_message_content(self.user_id, self.tools_executor.artwork)

    def _config(self, max_tool_rounds: int = 5) -> Dict[str, Any]:
        callbacks = [_DebugCallbackHandler()] if self.debug else []
        return {
            "configurable": {"thread_id": self.thread_id},
            "recursion_limit": max_tool_rounds * 2 + 2,
            "callbacks": callbacks,
        }

    def _agent(self):
        return create_react_agent(
            model=self.llm,
            tools=self.tools,
            prompt=self._current_system_content(),
            checkpointer=_CHECKPOINTER,
        )

    def has_checkpoint(self) -> bool:
        state = self._agent().get_state(self._config())
        return bool(state.values.get("messages"))

    def checkpoint_messages(self) -> List[BaseMessage]:
        state = self._agent().get_state(self._config())
        return list(state.values.get("messages", []))

    def start_conversation(self) -> str:
        if self.has_checkpoint():
            messages = self.checkpoint_messages()
            for message in reversed(messages):
                if isinstance(message, AIMessage):
                    text = message.content if isinstance(message.content, str) else str(message.content)
                    return text
            return ""

        kickoff = HumanMessage(
            content=(
                "(system trigger: 대화가 막 시작되었고 사용자는 아직 아무 말도 하지 않았습니다. "
                "시스템 프롬프트의 '대화 시작 시 온보딩' 규칙에 따라 먼저 인사하고, "
                "필요하다면 온보딩 질문을 건네세요. 이 트리거 메시지 자체는 언급하지 마세요.)"
            )
        )
        result = self._agent().invoke({"messages": [kickoff]}, config=self._config(max_tool_rounds=1))
        final_message = result["messages"][-1]
        text = final_message.content if isinstance(final_message.content, str) else str(final_message.content)
        return text

    def chat(self, user_message: str, max_tool_rounds: int = 5) -> str:
        try:
            result = self._agent().invoke(
                {"messages": [HumanMessage(content=user_message)]},
                config=self._config(max_tool_rounds=max_tool_rounds),
            )
            final_message = result["messages"][-1]
            final_text = final_message.content if isinstance(final_message.content, str) else str(final_message.content)
        except GraphRecursionError:
            final_text = "(도구 호출이 너무 많아 응답을 생성하지 못했습니다.)"

        return final_text
