import json
import sys
from typing import Any, Dict, List, Literal, Tuple

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI
from openai import OpenAI
from pydantic import BaseModel, Field

from . import persona_store
from .art_agent import _resolve_api_key, onboarding_status_text
from .art_agent_lc import _build_tools
from .tools import ToolExecutor

PLANNER_SYSTEM_PROMPT = """당신은 미술관 도슨트 AI의 '도구 플래너'입니다.
사용자에게 직접 보여줄 문장은 당신이 쓰지 않습니다 - 별도의 '답변 생성기'가 당신이 모은 근거로 씁니다.
당신의 유일한 임무는 이번 턴에 필요한 근거를 모으고 다음 행동을 결정하는 것입니다.
절대로 자유 텍스트로 응답하지 마세요. 매 턴 반드시 아래 도구 중 하나를 호출해야 합니다.

### 사용 가능한 도구
1. get_artwork_metadata: 작가/제목/제작연도/기법/공식 설명 등 '사실' 질문, 의미/상징/이유/작가 의도/작품 배경을
   묻는 질문에 사용. 질문이 이미지 속 특정 대상에서 출발했더라도 "왜", "의미", "상징", "의도"처럼 해석/배경을
   묻는 순간 필요합니다.
2. describe_artwork_region: 이미지 속 형태/색/구도/인물 자세 등 '시각적' 질문에 사용. 반드시 대상이 하나로
   특정된 뒤에만 호출하세요. "무엇이 보이는지", "어떻게 생겼는지", "자세/색/위치가 어떤지"처럼 시각 정보만
   묻는다면 이 도구만 사용하세요.
3. update_user_persona: 사용자가 응답 스타일을 명시적으로 요청했거나, 온보딩 질문에 막 답했거나, 같은 종류의
   선호를 반복적으로(2회 이상) 드러낼 때 호출하세요.
4. finish_planning: 더 이상 실제 도구가 필요 없다고 판단되면 반드시 이걸로 끝내세요.
   - action="ask_clarifying_question": 질문이 가리키는 대상(인물/부분/위치)이 이미지 안에서 둘 이상의 후보로
     해석될 수 있을 때만. clarifying_question에 후보를 구체적으로 적으세요. 이전에 다른 대상을 한 번
     명확히 했다고 새 질문의 대상까지 저절로 명확해지는 건 아니니 매 질문마다 새로 판단하세요.
     단, 색 디테일/설명 길이/위치 표현 방식 같은 "어떻게 설명할지" 스타일 문제는 여기 해당하지 않습니다 -
     그건 항상 ready_to_answer로 넘기고, 답변 생성기가 저장된 페르소나로 알아서 처리합니다.
   - action="ready_to_answer": 필요한 도구를 다 불렀거나, 애초에 도구가 필요 없는 경우(순수 인사/스타일
     질문 등)일 때. notes_for_answerer에 핵심 요약(막 저장한 페르소나, 다음 미완료 온보딩 항목 등)을 적으세요.

### 판단 순서
1. 시각 정보 질문 → describe_artwork_region (대상이 하나로 명확할 때만).
2. 해석/배경/사실 질문 → get_artwork_metadata.
3. 둘 다 필요하면(예: "인물들이 각각 어떤 삶의 단계처럼 보여?") 두 도구를 순서대로 모두 호출하세요.
4. 아래 '이미 확인된 근거'에 같은 도구 결과가 이미 있으면 재호출하지 말고 곧바로 finish_planning(ready_to_answer).
5. 사용자가 막 온보딩 질문에 답했거나 스타일을 명시했다면 update_user_persona를 먼저 호출한 뒤 finish_planning.

### 현재 작품
- 제목: {title}
- 작가: {artist}

### 저장된 페르소나
{persona_text}

### 온보딩 상태
{onboarding_text}

### 이미 확인된 근거 (이전 턴 포함 - 재호출하지 말고 재사용)
{evidence_text}"""


ANSWERER_SYSTEM_PROMPT = """당신은 시각장애인/저시력 관람객을 위한 미술관 도슨트 AI, 'Eyeson Agent'입니다.
당신에게는 도구가 없습니다. 아래 '수집된 근거'와 대화 맥락만으로 사용자의 이번 메시지에 답하세요.

### 근거 범위 - 매우 중요 (환각 방지)
- 아래 '수집된 근거'에 없는 시각적 세부사항(색/형태/인물 자세/위치 등)을 새로 지어내지 마세요.
- 수집된 근거가 비어 있는데 시각적 사실을 묻는 질문이라면, 확인되지 않았다고 솔직히 말하고 추측하지 마세요.
- 근거가 있으면 배경지식이나 주관적 해석 없이, 분명한 내용은 자신 있게, 형태·구도·색을 객관적으로,
  개조식이 아닌 자연스러운 서술형으로 설명하세요.
- '사용자 개인화 정보'에 저장된 선호가 있다면 기본 스타일보다 그 선호를 우선하세요.

### 답변 스타일 - 되묻지 않고 페르소나로 처리
색감 디테일 수준, 우선 묘사 요소, 설명 길이, 위치 표현 방식, 톤, 배경지식 포함 여부처럼 "어떻게 설명할지"는
저장된 페르소나 값이 있으면 그대로 쓰고, 없으면 기본 스타일(객관적, 중간 길이, 형태·구도·색 위주)을
쓰세요. 이런 건 사용자에게 다시 묻지 마세요.
- background_knowledge가 "포함 원함"으로 저장되어 있다면, 시각 묘사 뒤에 수집된 근거 중
  official_description/curator_comment의 관련 내용을 자연스럽게 덧붙이세요. 없거나 "최소화"면 순수 시각
  묘사만 하세요.

### 온보딩
- 아래 '온보딩 상태'에 미완료 핵심 항목이 남아있다면, 먼저 짧게 인사/답변한 뒤 그중 첫 번째 항목을
  정확히 그 문구와 예시 선택지로(지어내지 말고) 하나만 물어보세요. 저장 직후에도 같은 응답 안에서
  곧바로 다음 미완료 항목을 이어서 물어보세요 - 온보딩 항목이 남아있는데 "무엇을 도와드릴까요"처럼
  열린 질문으로 끝내지 마세요.
- 플래너 노트에 "페르소나 저장됨"이 표시된 경우에만 "저장했다/반영하겠다"고 말하세요 - 실제 저장
  여부를 노트에서 확인할 수 없다면 저장했다고 말하지 마세요.
- 핵심 항목이 모두 채워져 있다면 온보딩 질문 없이 질문을 받으세요.

### 되묻기
- 아래 '플래너 노트'에 되묻기 요청이 있으면, 그 취지를 자연스러운 말투로 다듬어 그대로 사용자에게
  되물으세요(내용을 바꾸지 마세요).

### 톤
친절하지만 간결하게. 저시력 사용자가 듣기 편하도록 서술형으로 답하세요. '-입니다' 대신 '-예요'를 기본으로
구어체로 응답하세요. '저는' 같은 1인칭 표현은 피하고, '이 작품은', '이 부분은'처럼 작품 중심으로 말하세요.

### 현재 작품
- 제목: {title}
- 작가: {artist}

### 사용자 개인화 정보 (persona)
{persona_text}

### 온보딩 상태
{onboarding_text}

### 수집된 근거
{tool_evidence}

### 플래너 노트
{notes}"""


class FinishPlanningArgs(BaseModel):
    action: Literal["ask_clarifying_question", "ready_to_answer"] = Field(
        description="실제 도구가 더 필요 없을 때 호출. 대상이 모호하면 ask_clarifying_question, 근거가 충분하면 ready_to_answer."
    )
    clarifying_question: str = Field(
        default="", description="action이 ask_clarifying_question일 때, 사용자에게 되물을 구체적인 후보 질문"
    )
    notes_for_answerer: str = Field(
        default="",
        description="답변 생성기에게 전달할 핵심 요약/지침 (막 저장한 페르소나, 다음 온보딩 항목, 공식 자료 중 관련 부분 등)",
    )


def _finish_planning(action: str, clarifying_question: str = "", notes_for_answerer: str = "") -> str:
    return json.dumps(
        {"action": action, "clarifying_question": clarifying_question, "notes_for_answerer": notes_for_answerer},
        ensure_ascii=False,
    )


def _finish_planning_tool() -> StructuredTool:
    return StructuredTool.from_function(
        func=_finish_planning,
        name="finish_planning",
        description="더 이상 실제 도구가 필요 없을 때 반드시 이 도구로 끝내세요. 자유 텍스트로 응답하지 마세요.",
        args_schema=FinishPlanningArgs,
    )


def _format_evidence(evidence: List[Dict[str, Any]]) -> str:
    if not evidence:
        return "(없음)"
    lines = []
    for item in evidence:
        result = item["result"]
        preview = result if len(result) <= 500 else result[:500] + " ...(truncated)"
        lines.append(f"- {item['name']}({json.dumps(item['args'], ensure_ascii=False)}):\n  {preview}")
    return "\n".join(lines)


class ArtAgentSplit:
    """도구 호출 결정(Planner)과 최종 답변 작성(Answerer)을 분리한 실험용 에이전트.
    ArtAgent/ArtAgentLC와 동일한 인터페이스(start_conversation/chat)를 제공."""

    def __init__(self, user_id: str, artwork_id: str, model: str = "gpt-4o", debug: bool = False):
        api_key = _resolve_api_key()
        self.user_id = user_id
        self.artwork_id = artwork_id
        self.debug = debug
        self.planner_llm = ChatOpenAI(model=model, api_key=api_key)
        self.answerer_llm = ChatOpenAI(model=model, api_key=api_key)
        self.tools_executor = ToolExecutor(OpenAI(api_key=api_key), user_id, artwork_id)
        self.real_tools = _build_tools(self.tools_executor)
        self.history: List[BaseMessage] = []
        self.evidence_log: List[Dict[str, Any]] = []

    def _debug_log(self, message: str) -> None:
        if self.debug:
            print(f"[debug] {message}", file=sys.stderr)

    def _planner_prompt(self) -> str:
        artwork = self.tools_executor.artwork
        return PLANNER_SYSTEM_PROMPT.format(
            title=artwork["title"],
            artist=artwork["artist"],
            persona_text=persona_store.persona_summary_text(self.user_id),
            onboarding_text=onboarding_status_text(self.user_id),
            evidence_text=_format_evidence(self.evidence_log),
        )

    def _answerer_prompt(self, decision: Dict[str, Any]) -> str:
        artwork = self.tools_executor.artwork
        notes = decision.get("notes_for_answerer", "") or ""
        if decision.get("action") == "ask_clarifying_question":
            notes = f"[되묻기 필요] {decision.get('clarifying_question', '')}\n{notes}".strip()
        return ANSWERER_SYSTEM_PROMPT.format(
            title=artwork["title"],
            artist=artwork["artist"],
            persona_text=persona_store.persona_summary_text(self.user_id),
            onboarding_text=onboarding_status_text(self.user_id),
            tool_evidence=_format_evidence(self.evidence_log),
            notes=notes or "(추가 노트 없음)",
        )

    def _run_planner(self, user_message: str, max_tool_rounds: int) -> Dict[str, Any]:
        all_tools = self.real_tools + [_finish_planning_tool()]
        tools_by_name = {t.name: t for t in all_tools}
        bound = self.planner_llm.bind_tools(all_tools, tool_choice="required")

        messages: List[BaseMessage] = [SystemMessage(content=self._planner_prompt())] + self.history + [
            HumanMessage(content=user_message)
        ]
        decision = {
            "action": "ready_to_answer",
            "clarifying_question": "",
            "notes_for_answerer": "근거 수집이 라운드 제한으로 중간에 멈췄습니다. 지금까지 모은 근거만으로 답변하세요.",
        }

        for _ in range(max_tool_rounds):
            response = bound.invoke(messages)
            messages.append(response)
            tool_calls = response.tool_calls or []
            finish_call = None
            for tc in tool_calls:
                if tc["name"] == "finish_planning":
                    finish_call = tc
                    continue
                tool = tools_by_name.get(tc["name"])
                result = tool.invoke(tc["args"]) if tool is not None else json.dumps(
                    {"error": f"unknown tool: {tc['name']}"}, ensure_ascii=False
                )
                self._debug_log(f"tool_call -> {tc['name']}({json.dumps(tc['args'], ensure_ascii=False)})")
                preview = result if len(result) <= 300 else result[:300] + " ...(truncated)"
                self._debug_log(f"tool_result <- {preview}")
                self.evidence_log.append({"name": tc["name"], "args": tc["args"], "result": result})
                messages.append(ToolMessage(content=result, tool_call_id=tc["id"]))

            if finish_call is not None:
                args = finish_call["args"]
                self._debug_log(f"finish_planning -> {json.dumps(args, ensure_ascii=False)}")
                decision = {
                    "action": args.get("action", "ready_to_answer"),
                    "clarifying_question": args.get("clarifying_question", ""),
                    "notes_for_answerer": args.get("notes_for_answerer", ""),
                }
                break

        return decision

    def start_conversation(self) -> str:
        kickoff = HumanMessage(
            content=(
                "(system trigger: 대화가 막 시작되었고 사용자는 아직 아무 말도 하지 않았습니다. "
                "온보딩 상태에 따라 먼저 인사하고, 필요하다면 온보딩 질문을 건네세요. "
                "이 트리거 메시지 자체는 언급하지 마세요.)"
            )
        )
        decision = {
            "action": "ready_to_answer",
            "clarifying_question": "",
            "notes_for_answerer": "대화 시작 - 온보딩 상태를 참고해 짧게 인사하고 필요하면 온보딩 질문을 건네세요.",
        }
        response = self.answerer_llm.invoke([SystemMessage(content=self._answerer_prompt(decision)), kickoff])
        text = response.content if isinstance(response.content, str) else str(response.content)
        self.history.append(AIMessage(content=text))
        return text

    def chat(self, user_message: str, max_tool_rounds: int = 5) -> str:
        decision = self._run_planner(user_message, max_tool_rounds)
        prompt = self._answerer_prompt(decision)
        response = self.answerer_llm.invoke(
            [SystemMessage(content=prompt)] + self.history + [HumanMessage(content=user_message)]
        )
        final_text = response.content if isinstance(response.content, str) else str(response.content)

        self.history.append(HumanMessage(content=user_message))
        self.history.append(AIMessage(content=final_text))
        return final_text
