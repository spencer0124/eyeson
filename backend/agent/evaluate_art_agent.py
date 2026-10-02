import argparse
import json
import os
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.errors import GraphRecursionError
from langgraph.prebuilt import create_react_agent
from openai import OpenAI

if __package__ in (None, ""):
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from agent import art_agent, artwork_data, persona_store  # type: ignore
    from agent.art_agent import BASE_SYSTEM_PROMPT, _resolve_api_key, system_message_content  # type: ignore
    from agent.art_agent_lc import _build_tools  # type: ignore
    from agent.art_agent_split import ArtAgentSplit  # type: ignore
    from agent.tools import ToolExecutor  # type: ignore
else:
    from . import art_agent, artwork_data, persona_store
    from .art_agent import BASE_SYSTEM_PROMPT, _resolve_api_key, system_message_content
    from .art_agent_lc import _build_tools
    from .art_agent_split import ArtAgentSplit
    from .tools import ToolExecutor


ARTWORK_IDS = {
    "The Stages of Life": "the-stage-of-life.jpg",
    "Two Men Contemplating the Moon": "two-men-contemplating-the-moon.jpg",
    "Wanderer above the Sea of Fog": "wanderer-above-the-sea-of-fog.jpg",
}

TOOL_MAP = {
    "visual_description": "describe_artwork_region",
    "official_content": "get_artwork_metadata",
}

RULE_BASED_GUIDANCE = """### 답변 판단 기준
사용자 질문은 아래 순서로 판단하고 답하세요.
1. 시각 정보를 요청할 경우에는 describe_artwork_region이 반환한 작품 시각 묘사를 사용하세요.
   이미지 속 인물/사물/색/구도/공간/분위기처럼 눈에 보이는 내용은 자연스럽고 자신 있게 설명하세요.
   이 경우 "공식 자료에는 없습니다", "확인할 수 없습니다" 같은 방어적 문장을 붙이지 마세요.
2. 공식 자료를 필요로 하는 질문일 경우에는 get_artwork_metadata의
   title/artist/style/official_description/curator_comment를 참고해서 응답하세요.
   작품 외적 배경, 외부 미술사, 작가 정보, 제작 맥락, 작품의 공식 해설이 여기에 해당합니다.
3. 공식 자료를 참고했는데 관련 내용이 하나도 없는 경우에만 답변할 수 없다고 말하세요.
4. 객관적 사실이 아닌 주관적 해석을 요구하는 경우에는 단정적으로 해석하지 말고 인간 해설자의 도움으로
   연계하세요. 대신 이미지에서 보이는 요소나 공식 자료에 있는 설명은 객관적으로 제공할 수 있습니다.
- 이미 도구 호출 결과가 대화 히스토리에 있으면 재호출하지 말고 그 내용을 바탕으로 답하세요."""

FEW_SHOT_GUIDANCE = """### 답변 판단 기준
사용자 질문은 아래 순서로 판단하고 답하세요.
1. 시각 정보를 요청할 경우에는 describe_artwork_region이 반환한 작품 시각 묘사를 사용하세요.
2. 작품 외적 배경, 외부 미술사, 작가 정보 등 공식 자료가 필요한 질문에는 get_artwork_metadata의
   정보를 참고해서 응답하세요.
3. 한 질문 안에 공식 해석과 시각 관찰이 섞여 있으면 두 정보를 함께 사용하세요.
4. 공식 자료를 참고했는데 관련 내용이 하나도 없고, 이미지로도 관찰할 수 없는 경우에만 "답변할 수 없다"고 말하세요.
5. 객관적 사실이 아닌 주관적 해석을 요구하는 경우에는 단정하지 말고 인간 해설자의 도움으로 연계하세요.
- 이미 도구 호출 결과가 대화 히스토리에 있으면 재호출하지 말고 그 내용을 바탕으로 답하세요.

### 답변 예시 (few-shot)
아래 예시의 판단 방식과 말투를 따르세요. 특히 공식 자료에 관련 표현이 있는데도
"공식 자료에는 명확한 설명이 없다"고 말하지 마세요.

예시 1 - 공식 자료에 관련 내용이 있는 상징 질문
- 사용자: "왜 인물들의 나이가 다양할까? 다 다르잖아"
- 도구 결과: curator_comment에 "다섯 척의 배와 인물들은 인생의 여러 단계를 상징하는 듯 보이며,
  인생의 순환과 세대 교체를 암시하는 은유로 보는 것이 더 의미가 있다"는 내용이 있음.
- 좋은 답변: "공식 자료에서는 이 작품의 배와 인물들이 인생의 여러 단계를 상징하는 듯 보인다고 설명해요.
  그래서 다양한 나이대의 인물은 어린 시절부터 노년까지 이어지는 삶의 흐름과, 세대가 이어지는 느낌을
  보여주는 장치로 이해할 수 있어요. 다만 상징을 하나하나 고정해서 해석하기보다는 인생의 순환과
  세대 교체를 암시하는 은유로 보는 쪽이 더 적절해요."
- 나쁜 답변: "공식 자료에는 인물들의 나이가 다양한 이유가 명확히 설명되어 있지 않지만..."

예시 2 - 순수 시각 묘사 질문
- 사용자: "노란 머리 소년은 어떻게 생겼어?"
- 도구 결과: describe_artwork_region이 노란 머리 소년의 자세, 옷, 위치, 색을 설명함.
- 좋은 답변: "노란 머리의 소년은 화면 아래쪽에 있고, 몸은 작게 표현되어 있어요. 밝은 머리색 때문에
  주변 인물들 사이에서 비교적 눈에 잘 띄며, 자세는 안정적으로 앉아 있는 모습에 가까워요."
- 나쁜 답변: "공식 자료에는 노란 머리 소년에 대한 설명이 없어 확인할 수 없어요."

예시 3 - 공식 해석과 시각 관찰이 함께 필요한 질문
- 사용자: "그럼 인물들이 각각 어떤 시기를 나타내는 것 같아? 노인, 어린이, 성인 이런 식으로 보여?"
- 도구 결과: 공식 자료에는 인생의 여러 단계와 세대 교체 설명이 있고, 시각 묘사에는 어린아이,
  성인, 장년 또는 노년으로 보이는 인물이 함께 나타난다는 내용이 있음.
- 좋은 답변: "공식 자료는 각 인물을 특정 시기에 일대일로 고정하지는 않고, 전체적으로 인생의 여러 단계와
  세대 교체를 암시한다고 설명해요. 다만 화면에서 보이는 모습만 놓고 보면 어린아이처럼 작은 인물,
  젊은 성인처럼 보이는 인물, 장년이나 노년에 가까워 보이는 인물들이 함께 배치돼 있어요."
- 나쁜 답변: "공식 자료가 각 인물의 시기를 설명하지 않으므로 답변할 수 없어요."

예시 4 - 공식 자료에 관련 내용이 전혀 없는 질문
- 사용자: "작가가 이 작품을 그린 날 누구에게 편지를 썼어?"
- 도구 결과: 공식 자료에 관련 내용이 없음.
- 좋은 답변: "제공된 공식 자료 안에서는 그 내용을 확인할 수 없어 답변하기 어려워요."
"""


def _replace_guidance(prompt: str, guidance: str) -> str:
    start = prompt.index("### 답변 판단 기준")
    end = prompt.index("### 질문에서 정해지지 않은 부분 처리")
    return prompt[:start] + guidance.rstrip() + "\n\n" + prompt[end:]


def _prompt_for_variant(variant: str) -> str:
    if variant == "rule_based":
        return _replace_guidance(BASE_SYSTEM_PROMPT, RULE_BASED_GUIDANCE)
    if variant == "few_shot":
        return _replace_guidance(BASE_SYSTEM_PROMPT, FEW_SHOT_GUIDANCE)
    if variant == "tool_calling_few_shot":
        return BASE_SYSTEM_PROMPT
    raise ValueError(f"Unknown variant: {variant}")


def _required_actual_tools(item: Dict[str, Any]) -> List[str]:
    return [TOOL_MAP[t] for t in item.get("required_tools", []) if t in TOOL_MAP]


def _optional_actual_tools(item: Dict[str, Any]) -> List[str]:
    return [TOOL_MAP[t] for t in item.get("optional_tools", []) if t in TOOL_MAP]


def _ensure_persona(user_id: str) -> None:
    defaults = {
        "color_description": "세밀하게 - 색조와 뉘앙스까지",
        "priority_focus": "인물이나 주요 소재 위주",
        "detail_level": "상세하게 - 형태와 질감까지 풍부하게",
        "spatial_reference_style": "상하좌우",
    }
    for key, value in defaults.items():
        persona_store.upsert_preference(user_id, key, value, "explicit", "eval default")


def _extract_trace(messages: List[Any]) -> Dict[str, Any]:
    calls: List[Dict[str, Any]] = []
    by_id: Dict[str, Dict[str, Any]] = {}
    for message in messages:
        if isinstance(message, AIMessage):
            for call in getattr(message, "tool_calls", []) or []:
                row = {
                    "id": call.get("id", ""),
                    "name": call.get("name", ""),
                    "args": call.get("args", {}),
                    "result": "",
                }
                calls.append(row)
                by_id[row["id"]] = row
        elif isinstance(message, ToolMessage):
            row = by_id.get(getattr(message, "tool_call_id", ""))
            if row is not None:
                row["result"] = message.content if isinstance(message.content, str) else str(message.content)
    return {"tool_calls": calls, "called_tool_names": [c["name"] for c in calls]}


def _run_one(item: Dict[str, Any], variant: str, agent_model: str, run_id: str) -> Dict[str, Any]:
    artwork_id = ARTWORK_IDS[item["artwork"]]
    user_id = f"eval_{variant}_{item['id']}_{run_id}"
    _ensure_persona(user_id)

    old_prompt = art_agent.BASE_SYSTEM_PROMPT
    art_agent.BASE_SYSTEM_PROMPT = _prompt_for_variant(variant)
    try:
        api_key = _resolve_api_key()
        llm = ChatOpenAI(model=agent_model, api_key=api_key)
        executor = ToolExecutor(OpenAI(api_key=api_key), user_id, artwork_id)
        graph = create_react_agent(
            model=llm,
            tools=_build_tools(executor),
            prompt=system_message_content(user_id, executor.artwork),
        )
        try:
            result = graph.invoke(
                {"messages": [HumanMessage(content=item["question"])]},
                config={"recursion_limit": 12},
            )
            messages = result["messages"]
            final = messages[-1].content if messages else ""
            if not isinstance(final, str):
                final = str(final)
            error = ""
        except GraphRecursionError as exc:
            messages = []
            final = "(도구 호출이 너무 많아 응답을 생성하지 못했습니다.)"
            error = str(exc)
    finally:
        art_agent.BASE_SYSTEM_PROMPT = old_prompt

    trace = _extract_trace(messages)
    required = _required_actual_tools(item)
    optional = _optional_actual_tools(item)
    called = trace["called_tool_names"]
    return {
        "id": item["id"],
        "variant": variant,
        "artwork": item["artwork"],
        "artwork_id": artwork_id,
        "category": item.get("category", ""),
        "question": item["question"],
        "required_tools": required,
        "optional_tools": optional,
        "called_tools": called,
        "tool_calls": trace["tool_calls"],
        "missing_required_tools": [t for t in required if t not in called],
        "unnecessary_tools": [t for t in called if t not in required and t not in optional],
        "final_answer": final,
        "error": error,
        "expected_action": item.get("expected_action", ""),
        "fallback_action": item.get("fallback_action", ""),
        "evaluation_points": item.get("evaluation_points", []),
        "forbidden_behaviors": item.get("forbidden_behaviors", []),
    }


def _run_one_split(item: Dict[str, Any], agent_model: str, run_id: str) -> Dict[str, Any]:
    artwork_id = ARTWORK_IDS[item["artwork"]]
    user_id = f"eval_split_{item['id']}_{run_id}"
    _ensure_persona(user_id)

    error = ""
    try:
        agent = ArtAgentSplit(user_id=user_id, artwork_id=artwork_id, model=agent_model, debug=False)
        final = agent.chat(item["question"], max_tool_rounds=6)
        evidence = agent.evidence_log
    except Exception as exc:  # noqa: BLE001 - record any failure as a row instead of aborting the run
        final = "(에이전트 실행 중 오류가 발생했습니다.)"
        evidence = []
        error = str(exc)

    called = [e["name"] for e in evidence]
    required = _required_actual_tools(item)
    optional = _optional_actual_tools(item)
    return {
        "id": item["id"],
        "variant": "split",
        "artwork": item["artwork"],
        "artwork_id": artwork_id,
        "category": item.get("category", ""),
        "question": item["question"],
        "required_tools": required,
        "optional_tools": optional,
        "called_tools": called,
        "tool_calls": [{"id": "", "name": e["name"], "args": e["args"], "result": e["result"]} for e in evidence],
        "missing_required_tools": [t for t in required if t not in called],
        "unnecessary_tools": [t for t in called if t not in required and t not in optional],
        "final_answer": final,
        "error": error,
        "expected_action": item.get("expected_action", ""),
        "fallback_action": item.get("fallback_action", ""),
        "evaluation_points": item.get("evaluation_points", []),
        "forbidden_behaviors": item.get("forbidden_behaviors", []),
    }


JUDGE_SYSTEM = """You are an evaluation judge for a museum AI agent.
Return only valid JSON. Judge based on the provided expected tools, tool results, and final Korean answer.
Do not reward unsupported claims. Do not require exact wording."""


def _judge_one(client: OpenAI, row: Dict[str, Any], judge_model: str) -> Dict[str, Any]:
    tool_results = [
        {
            "name": call["name"],
            "args": call.get("args", {}),
            "result_excerpt": (call.get("result") or "")[:1200],
        }
        for call in row["tool_calls"]
    ]
    prompt = {
        "item_id": row["id"],
        "category": row["category"],
        "question": row["question"],
        "expected_action": row["expected_action"],
        "fallback_action": row["fallback_action"],
        "required_tools": row["required_tools"],
        "optional_tools": row["optional_tools"],
        "called_tools": row["called_tools"],
        "tool_results": tool_results,
        "final_answer": row["final_answer"],
        "evaluation_points": row["evaluation_points"],
        "forbidden_behaviors": row["forbidden_behaviors"],
        "rubric": {
            "tool_result_utilized": "True if the final answer substantively uses the relevant called tool result(s), not merely generic filler.",
            "unnecessary_refusal": "True if the agent refused, said it cannot answer, or handed off even though expected_action requires an answer from available visual/official evidence.",
            "appropriate_handoff": "True if a subjective or unsupported interpretation question is appropriately framed as personal interpretation or routed to a human interpreter. Null if not applicable.",
            "unsupported_claim": "True if the answer asserts a factual/official claim not supported by the tool results.",
        },
        "json_schema": {
            "tool_result_utilized": "boolean",
            "unnecessary_refusal": "boolean",
            "appropriate_handoff": "boolean or null",
            "unsupported_claim": "boolean",
            "notes": "short Korean explanation",
        },
    }
    response = client.chat.completions.create(
        model=judge_model,
        messages=[
            {"role": "system", "content": JUDGE_SYSTEM},
            {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
        ],
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content or "{}"
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "tool_result_utilized": False,
            "unnecessary_refusal": False,
            "appropriate_handoff": None,
            "unsupported_claim": True,
            "notes": f"judge JSON parse failed: {content[:200]}",
        }


@dataclass
class Summary:
    variant: str
    total: int = 0
    required_tool_recall_hits: int = 0
    no_unnecessary_tool_hits: int = 0
    utilization_hits: int = 0
    no_unnecessary_refusal_hits: int = 0
    no_unsupported_claim_hits: int = 0

    def as_dict(self) -> Dict[str, Any]:
        def pct(value: int) -> float:
            return round(value / self.total, 4) if self.total else 0.0

        return {
            "variant": self.variant,
            "total": self.total,
            "required_tool_recall": pct(self.required_tool_recall_hits),
            "no_unnecessary_tool_use": pct(self.no_unnecessary_tool_hits),
            "tool_result_utilization": pct(self.utilization_hits),
            "no_unnecessary_refusal": pct(self.no_unnecessary_refusal_hits),
            "no_unsupported_claim": pct(self.no_unsupported_claim_hits),
        }


def _summarize(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    summaries: Dict[str, Summary] = {}
    for row in rows:
        summary = summaries.setdefault(row["variant"], Summary(variant=row["variant"]))
        summary.total += 1
        if not row["missing_required_tools"]:
            summary.required_tool_recall_hits += 1
        if not row["unnecessary_tools"]:
            summary.no_unnecessary_tool_hits += 1
        if row.get("judge", {}).get("tool_result_utilized") is True:
            summary.utilization_hits += 1
        if row.get("judge", {}).get("unnecessary_refusal") is not True:
            summary.no_unnecessary_refusal_hits += 1
        if row.get("judge", {}).get("unsupported_claim") is not True:
            summary.no_unsupported_claim_hits += 1
    return [summaries[key].as_dict() for key in sorted(summaries)]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default=os.path.join(os.path.dirname(__file__), "art_agent_eval_30.json"))
    parser.add_argument("--out", default="")
    parser.add_argument("--agent-model", default=os.getenv("ART_AGENT_EVAL_MODEL", "gpt-4o"))
    parser.add_argument("--judge-model", default=os.getenv("ART_AGENT_EVAL_JUDGE_MODEL", "gpt-4o-mini"))
    parser.add_argument(
        "--variants",
        nargs="+",
        default=["rule_based", "few_shot", "tool_calling_few_shot"],
        choices=["rule_based", "few_shot", "tool_calling_few_shot", "split"],
    )
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--skip-judge", action="store_true")
    args = parser.parse_args()

    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"))
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

    with open(args.dataset, "r", encoding="utf-8") as f:
        dataset = json.load(f)
    items = dataset["items"][: args.limit or None]
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    rows: List[Dict[str, Any]] = []
    for variant in args.variants:
        for item in items:
            print(f"[eval] {variant} {item['id']} {item['artwork']}", flush=True)
            if variant == "split":
                row = _run_one_split(item, args.agent_model, run_id)
            else:
                row = _run_one(item, variant, args.agent_model, run_id)
            rows.append(row)

    if not args.skip_judge:
        judge_client = OpenAI(api_key=_resolve_api_key())
        for row in rows:
            print(f"[judge] {row['variant']} {row['id']}", flush=True)
            row["judge"] = _judge_one(judge_client, row, args.judge_model)
            time.sleep(0.1)

    result = {
        "run_id": run_id,
        "dataset": args.dataset,
        "agent_model": args.agent_model,
        "judge_model": None if args.skip_judge else args.judge_model,
        "summary": _summarize(rows),
        "rows": rows,
    }
    out = args.out or os.path.join(
        os.path.dirname(__file__),
        "eval_results",
        f"art_agent_eval_30_{run_id}.json",
    )
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps({"out": out, "summary": result["summary"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
