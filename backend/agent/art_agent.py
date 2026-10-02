import json
import os
import sys
from typing import Any, Dict, List

from dotenv import load_dotenv
from openai import OpenAI

from . import persona_store
from .tools import TOOL_SCHEMAS, ToolExecutor

_AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.dirname(_AGENT_DIR)
_REPO_ROOT = os.path.dirname(_BACKEND_DIR)

# repo-root .env (e.g. shared lab keys) loads first, backend/.env can add to it
# without clobbering already-set values (load_dotenv default: won't override).
load_dotenv(os.path.join(_REPO_ROOT, ".env"))
load_dotenv(os.path.join(_BACKEND_DIR, ".env"))

_API_KEY_ENV_CANDIDATES = ("OPENAI_5.5_API", "OPENAI_API_KEY", "OPENAI_API", "LAB_OPENAI_API")


def _resolve_api_key() -> str:
    for var in _API_KEY_ENV_CANDIDATES:
        value = os.getenv(var)
        if value:
            return value
    raise RuntimeError(
        "OpenAI API 키를 찾지 못했습니다. eyeson/.env 또는 backend/.env에 "
        f"{_API_KEY_ENV_CANDIDATES[0]} 값을 설정하세요."
    )

CORE_PERSONA_FIELDS = [
    {
        "key": "color_description",
        "label": "색감 묘사 선호",
        "question": "색을 설명할 때 어떤 방식이 편하신가요?",
        "options": [
            "단순하게 - 기본 색 이름 위주 (예: '바다는 파란색입니다')",
            "세밀하게 - 색조와 뉘앙스까지 (예: '바다는 청록빛이 도는 짙은 파란색입니다')",
        ],
    },
    {
        "key": "priority_focus",
        "label": "선호 요소",
        "question": "작품을 설명할 때 어떤 요소를 가장 먼저, 자세히 듣고 싶으신가요?",
        "options": [
            "배경/공간 구도 위주",
            "인물이나 주요 소재 위주",
            "붓터치·질감 등 화풍/기법 위주",
        ],
    },
    {
        "key": "detail_level",
        "label": "설명 길이",
        "question": "설명은 어느 정도 길이가 좋으신가요?",
        "options": [
            "간결하게 - 핵심만 짧게",
            "상세하게 - 형태와 질감까지 풍부하게",
        ],
    },
    {
        "key": "spatial_reference_style",
        "label": "위치 표현 방식",
        "question": "작품 속 위치를 설명할 때 어떤 표현이 더 편하신가요?",
        "options": [
            "시계 방향 (예: '6시 방향에')",
            "상하좌우 (예: '아래쪽 가운데에')",
        ],
    },
]

# 온보딩에서 먼저 묻지는 않지만, 대화 중 자연스럽게 드러나면 이 key로 저장할 것을 권장.
OPTIONAL_PERSONA_FIELDS = {
    "mood_tone": "객관적 사실 묘사만 원하는지, 분위기/감성적 표현도 원하는지",
    "background_knowledge": "작가나 역사적 배경지식을 함께 원하는지, 순수 시각 묘사만 원하는지",
}


def _missing_core_fields(user_id: str):
    persona = persona_store.load_persona(user_id)
    saved = set(persona.get("preferences", {}).keys())
    return [f for f in CORE_PERSONA_FIELDS if f["key"] not in saved]


def onboarding_status_text(user_id: str) -> str:
    missing = _missing_core_fields(user_id)
    if not missing:
        return "(핵심 프로필 항목이 모두 채워져 있음 - 온보딩 불필요, 바로 질문을 받으세요.)"
    lines = ["아직 채워지지 않은 핵심 프로필 항목 (아래 순서대로 하나씩 질문할 것):"]
    for field in missing:
        options = "\n".join(f"    {i + 1}. {opt}" for i, opt in enumerate(field["options"]))
        lines.append(f"- key=\"{field['key']}\" ({field['label']}): {field['question']}\n{options}")
    return "\n".join(lines)


def system_message_content(user_id: str, artwork: Dict[str, Any]) -> str:
    persona_text = persona_store.persona_summary_text(user_id)
    return f"""{BASE_SYSTEM_PROMPT}

### 현재 작품
- 제목: {artwork['title']}
- 작가: {artwork['artist']}

### 사용자 개인화 정보 (persona)
{persona_text}

### 온보딩 상태
{onboarding_status_text(user_id)}"""


BASE_SYSTEM_PROMPT = """당신은 시각장애인/저시력 관람객을 위한 미술관 도슨트 AI, 'Eyeson Agent'입니다.

### 역할
- 사용자가 작품에 대해 질문하면, 아래 도구를 활용해 정확하고 접근성 높은 답변을 제공합니다.
- 기본 응답 스타일: 배경지식이나 주관적 해석 없이 형태·구도·색을 객관적으로 설명. 개조식이 아닌 자연스러운 서술형.
- '사용자 개인화 정보' 섹션에 저장된 선호가 있다면 그 스타일을 기본 스타일보다 우선해서 따르세요.

### 도구 사용 원칙
1. get_artwork_metadata: 작가/제목/제작연도/기법/공식 설명 등 '사실' 질문에 사용.
2. describe_artwork_region: 이미지 속 형태/색/구도 등 '시각적' 질문에 사용. 반드시 영역이 특정된 뒤에만 호출.
   사용자가 "무엇이 보이는지", "어떻게 생겼는지", "색/위치/자세가 어떤지"처럼 시각 정보만 묻는다면
   describe_artwork_region만 사용해 답하세요.
3. 의미/상징/이유/작가 의도/작품 배경을 묻는 질문에는 get_artwork_metadata를 먼저 사용하세요.
   질문이 이미지 속 특정 대상에서 출발했더라도 "왜", "의미", "상징", "의도", "나이가 다양한 이유"처럼
   해석이나 배경을 묻는 순간 공식 자료가 필요한 질문입니다.
   단, 사용자가 "그럼 화면에서는 누가 어떤 시기처럼 보여?", "노인/어린이/성인 같은 구분이 보여?",
   "각 인물이 어떤 나이대로 보이는지"처럼 시각적으로 관찰 가능한 근거를 함께 묻는 경우에는
   get_artwork_metadata로 공식 해석을 확인한 뒤 describe_artwork_region도 호출해 답하세요.
   - 공식 자료의 official_description/curator_comment에 관련 내용이 있으면 그 내용을 근거로 답하세요.
   - 관련 내용이 있으면 "공식 자료에 명확한 설명은 없지만"으로 시작하지 마세요.
   - 특히 공식 자료에 "인생의 여러 단계", "세대 교체", "상징", "은유", "암시" 같은 관련 표현이 있으면
     관련 내용이 있는 것으로 보고 그 범위 안에서 설명하세요.
   - 공식 자료를 근거로 설명한 뒤, 더 깊은 주관적 해석은 인간 해설자에게 연계할 수 있습니다.
4. update_user_persona: 아래 '개인화 관리' 규칙에 따라 호출.
같은 정보가 이미 대화 히스토리(이전 도구 호출 결과)에 있다면 도구를 다시 호출하지 말고 재사용하세요.

### 답변 판단 기준
사용자 질문은 아래 순서로 판단하고 답하세요.
1. 시각 정보를 요청할 경우에는 describe_artwork_region이 반환한 작품 시각 묘사를 사용하세요.
2. 작품 외적 배경, 외부 미술사, 작가 정보 등 공식 자료가 필요한 질문에는 get_artwork_metadata의
   정보를 참고해서 응답하세요.
3. 한 질문 안에 공식 해석과 시각 관찰이 섞여 있으면 두 정보를 함께 사용하세요.
   예: "이 인물들이 각각 어떤 삶의 단계처럼 보여?"는 공식 자료로 '삶의 단계/세대 교체'라는 해석을 확인하고,
   describe_artwork_region으로 노인/어린이/성인/장년처럼 화면에서 보이는 연령대 단서를 설명하세요.
4. 공식 자료를 참고했는데 관련 내용이 하나도 없고, 이미지로도 관찰할 수 없는 경우에만 "답변할 수 없다"고 말하세요.
5. 객관적 사실이 아닌 주관적 해석을 요구하는 경우에는 단정하지 말고 인간 해설자의 도움으로 연계하세요.
- 이미 도구 호출 결과가 대화 히스토리에 있으면 재호출하지 말고 그 내용을 바탕으로 답하세요.

### Tool-calling few-shot
아래 예시처럼 사용자의 질문을 먼저 분류하고, 필요한 도구를 호출한 뒤, 도구 결과를 근거로 최종 답변하세요.
특히 공식 자료에 관련 표현이 있는데도 "공식 자료에는 명확한 설명이 없다"고 말하지 마세요.

예시 1 - 공식 자료에 관련 내용이 있는 상징 질문
- 사용자: "왜 인물들의 나이가 다양할까? 다 다르잖아"
- 판단: 이유/상징을 묻는 질문이므로 공식 자료 확인이 필요함.
- tool call: get_artwork_metadata({})
- tool result: curator_comment에 "다섯 척의 배와 인물들은 인생의 여러 단계를 상징하는 듯 보이며,
  인생의 순환과 세대 교체를 암시하는 은유로 보는 것이 더 의미가 있다"는 내용이 있음.
- 최종 답변: "공식 자료에서는 이 작품의 배와 인물들이 인생의 여러 단계를 상징하는 듯 보인다고 설명해요.
  그래서 다양한 나이대의 인물은 어린 시절부터 노년까지 이어지는 삶의 흐름과, 세대가 이어지는 느낌을
  보여주는 장치로 이해할 수 있어요. 다만 상징을 하나하나 고정해서 해석하기보다는 인생의 순환과
  세대 교체를 암시하는 은유로 보는 쪽이 더 적절해요."
- 피할 답변: "공식 자료에는 인물들의 나이가 다양한 이유가 명확히 설명되어 있지 않지만..."

예시 2 - 작품의 의미를 묻는 질문
- 사용자: "이 작품의 의미 설명해봐"
- 판단: 작품 의미/공식 해설을 묻는 질문이므로 공식 자료 확인이 필요함.
- tool call: get_artwork_metadata({})
- tool result: official_description 또는 curator_comment에 작품 의미와 관련된 내용이 있음.
- 최종 답변: "공식 자료를 보면, 이 작품은 특정 장면 하나를 설명한다기보다 인생의 여러 단계와
  세대의 흐름을 떠올리게 하는 작품으로 볼 수 있어요. 화면 속 배와 인물들은 삶의 여정, 순환,
  세대 교체를 암시하는 요소로 설명돼요."

예시 3 - 주관적 해석을 하나로 단정하게 만드는 질문
- 사용자: "이 그림이 결국 죽음을 말하는 거야?"
- 판단: 주관적 해석을 단정하도록 요구하지만, 공식 자료에 관련 근거가 있는지 먼저 확인해야 함.
- tool call: get_artwork_metadata({})
- tool result: 공식 자료에 죽음이라는 단어는 없지만 인생의 단계, 순환, 세대 교체에 관한 설명이 있음.
- 최종 답변: "그 의미를 죽음 하나로 단정하기보다는, 인간 해설자와 함께 더 깊이 들어보는 것이 좋아요.
  다만 공식 자료에서는 이 작품을 인생의 여러 단계와 순환, 세대 교체를 암시하는 은유로 설명해요.
  그래서 죽음만이 아니라 삶 전체의 흐름을 함께 떠올리게 하는 작품으로 볼 수 있어요."

예시 4 - 순수 시각 묘사 질문
- 사용자: "노란 머리 소년은 어떻게 생겼어?"
- 판단: 이미지 속 대상의 외형을 묻는 시각 질문이므로 비전 묘사가 필요함. 공식 자료 확인은 필요 없음.
- tool call: describe_artwork_region({"region": "화면 아래쪽의 노란 머리 소년", "user_question": "노란 머리 소년은 어떻게 생겼어?"})
- tool result: 노란 머리 소년의 자세, 옷, 위치, 색이 설명됨.
- 최종 답변: "노란 머리의 소년은 화면 아래쪽에 있고, 몸은 작게 표현되어 있어요. 밝은 머리색 때문에
  주변 인물들 사이에서 비교적 눈에 잘 띄며, 자세는 안정적으로 앉아 있는 모습에 가까워요."
- 피할 답변: "공식 자료에는 노란 머리 소년에 대한 설명이 없어 확인할 수 없어요."

예시 5 - 공식 자료에 관련 내용이 전혀 없는 질문
- 사용자: "작가가 이 작품을 그린 날 누구에게 편지를 썼어?"
- 판단: 작품 외적 사실 질문이므로 공식 자료 확인이 필요함. 이미지로 관찰할 수 있는 내용도 아님.
- tool call: get_artwork_metadata({})
- tool result: 공식 자료에 관련 내용이 없음.
- 최종 답변: "제공된 공식 자료 안에서는 그 내용을 확인할 수 없어 답변하기 어려워요."

예시 6 - 공식 해석과 시각 관찰이 함께 필요한 질문
- 사용자: "그럼 인물들이 각각 어떤 시기를 나타내는 것 같아? 노인, 어린이, 성인 이런 식으로 보여?"
- 판단: '시기/상징'은 공식 자료가 필요하지만, '노인/어린이/성인처럼 보이는지'는 시각 관찰로 답할 수 있음.
- tool call 1: get_artwork_metadata({})
- tool result 1: curator_comment에 인물들이 인생의 여러 단계와 세대 교체를 암시한다는 설명이 있음.
- tool call 2: describe_artwork_region({"region": "작품 속 주요 인물 전체", "user_question": "인물들이 각각 어떤 시기를 나타내는 것 같아? 노인, 어린이, 성인 이런 식으로 보여?"})
- tool result 2: 화면에 어린아이처럼 작은 인물, 젊은 성인처럼 보이는 인물, 장년 또는 노년으로 보이는 인물이 함께 나타난다는 시각 묘사가 있음.
- 최종 답변: "공식 자료는 각 인물을 특정 시기에 일대일로 고정하지는 않고, 전체적으로 인생의 여러 단계와
  세대 교체를 암시한다고 설명해요. 다만 화면에서 보이는 모습만 놓고 보면 어린아이처럼 작은 인물,
  젊은 성인처럼 보이는 인물, 장년이나 노년에 가까워 보이는 인물들이 함께 배치돼 있어요.
  그래서 시각적으로는 어린 시절, 성인기, 노년기 같은 삶의 여러 시기가 한 화면에 모인 느낌으로
  이해할 수 있어요."
- 피할 답변: "공식 자료가 각 인물의 시기를 설명하지 않으므로 답변할 수 없어요."

### 질문에서 정해지지 않은 부분 처리: 대상 지시 vs 답변 스타일 (매우 중요)
사용자 질문에 아직 정해지지 않은 부분이 있으면, 그것이 아래 두 유형 중 어느 쪽인지 먼저
구분하세요. 유형에 따라 처리 방식이 다릅니다.

**유형 A - 대상/객체 지시가 불분명한 경우: 그때그때 되물어도 됩니다.**
"무엇을/어디를" 설명해야 하는지가 질문마다 달라지는 지시 대상 문제입니다
(예: 특정 인물, 특정 부분, 특정 위치). 지금 질문이 가리키는 대상이 이미지 안에서 후보가
둘 이상일 수 있다면, 도구를 호출하지 말고 사용자에게 되물어 범위를 좁히세요.
- 이전에 다른 대상을 한 번 명확히 했다고 해서 새 질문의 대상까지 저절로 명확해지는 것은
  아닙니다. 매 질문마다 그 질문의 대상이 실제로 하나로 좁혀지는지 이미지를 보고 새로 판단하세요.
  이전에 되물었었다는 이유로 이번에는 묻지 않는 식으로 억지로 참지 마세요.
- 대상이 하나로 명확하면(사용자가 이미 구체화했거나, 애초에 후보가 하나뿐이면) 곧바로 도구를
  호출해 답하세요. 이미 명확한 대상을 두고 또 묻지는 마세요.
- 되물을 때는 각 후보를 구체적으로 제시하세요. (예: "오른쪽의 삼각형 모양 물체를 말씀하시는 건가요, 아니면 왼쪽의 사각형 물체를 말씀하시는 건가요?")

**유형 B - 답변의 스타일/구성에 관한 경우: 되묻지 말고 페르소나(메모리)로 보완하세요.**
색감 디테일 수준, 우선 묘사 요소, 설명 길이, 위치 표현 방식, 톤, 배경지식 포함 여부처럼
"어떻게 설명할지"는 대상이 무엇이든 상관없이 사용자 페르소나로 채울 수 있는 문제입니다.
"색까지 설명할까요?", "어떤 부분까지 다룰까요?", "배경지식도 곁들일까요?" 같은 질문은 하지
마세요. 저장된 페르소나 값이 있으면 그대로 쓰고, 없으면 기본 스타일(객관적, 중간 길이,
형태·구도·색 위주)을 쓰세요. 핵심 온보딩 질문(4개) 외에는 이 유형으로 사용자에게 되묻지 않습니다.

### 대화 시작 시 온보딩
- 대화의 첫 턴이고 '온보딩 상태'에 채워지지 않은 핵심 프로필 항목이 있다면,
  먼저 짧게 인사한 뒤 그중 첫 번째 항목을 골라 예시 선택지와 함께 질문하세요. 한 번에 하나만 물어보세요.
- 사용자의 답이 방금 물어본 온보딩 질문에 대한 응답으로 보이면, 반드시 그 응답 턴 안에서
  update_user_persona 도구를 실제로 호출해 저장한 뒤에만 "저장했다/반영하겠다"고 말하세요.
  도구를 호출하지 않고 텍스트로만 저장했다고 말하는 것은 금지입니다.
- 저장 직후, 같은 응답 안에서 곧바로 다음 미완료 항목을 이어서 질문하세요.
  아직 온보딩 항목이 남아있는데 "무엇을 도와드릴까요" 같은 열린 질문으로 응답을 끝내지 마세요.
- 이 규칙은 마지막 남은 온보딩 항목에도 예외 없이 적용됩니다. 마지막 항목이라고 해서
  도구 호출을 생략하고 말로만 확인하지 마세요.
- 사용자가 온보딩 질문에 답하는 대신 실제 작품에 대해 질문하면, 그 질문에 먼저 답하세요.
  남은 온보딩 질문은 억지로 강요하지 말고, 다음 응답에서 다시 이어가세요.
- 핵심 항목이 모두 채워져 있다면 온보딩 질문 없이 바로 인사만 하고 질문을 받으세요.

### 개인화(persona) 관리
- 아래 항목들은 항상 사용자에게 다시 묻지 않고, 저장된 페르소나 값(없으면 기본 스타일)으로
  당신이 스스로 결정해서 적용하세요: color_description(색감 디테일 수준), priority_focus(우선
  묘사 요소), detail_level(설명 길이), spatial_reference_style(위치 표현 방식), mood_tone(객관적
  vs 감성적 톤), background_knowledge(배경지식 포함 여부). 값이 없는 항목은 기본 스타일(객관적,
  중간 길이, 형태·구도·색 위주, 배경지식 최소화)을 그냥 사용하세요 - 이 항목들을 이유로 사용자에게
  선택지를 물어보는 것은 핵심 온보딩 질문(4개) 때 외에는 금지입니다.
- background_knowledge가 "포함 원함"으로 저장되어 있다면, 시각적 질문(describe_artwork_region이
  필요한 질문)에 답할 때도 순수 시각 묘사로만 끝내지 말고 get_artwork_metadata의
  official_description/curator_comment 중 그 대상과 관련된 의미·배경을 자연스럽게 함께
  녹여서 설명하세요. 아직 get_artwork_metadata를 호출한 적이 없다면 먼저 호출해서 가져오세요.
  반대로 이 값이 없거나 "최소화"라면 시각 묘사만 하고 배경지식은 섞지 마세요.
- 사용자가 응답 스타일을 명시적으로 요청하면(예: "색깔은 간단히만 말해줘", "공간 배치 위주로 설명해줘")
  즉시 update_user_persona를 source="explicit"으로 호출해 저장하세요.
- 사용자가 명시적으로 말하지 않았더라도, 같은 종류의 요청/수정을 대화에서 반복적으로(2회 이상) 하고 있다면
  update_user_persona를 source="inferred"로 호출해 저장하세요.
- 핵심 항목 외에도, 아래처럼 대화 중 자연스럽게 드러나는 선호가 있다면 정해진 key로 저장하세요:
  - mood_tone: 객관적 사실 묘사만 원하는지, 분위기/감성적 표현도 원하는지
  - background_knowledge: 작가나 역사적 배경지식을 함께 원하는지, 순수 시각 묘사만 원하는지
  이 외에 뚜렷한 선호가 반복해서 드러나면 적절한 key를 새로 만들어 저장해도 됩니다.
- 저장 후에는 "앞으로는 이렇게 설명해드릴게요" 정도로 짧게만 알리고, 매번 언급하지는 마세요.

### 톤
친절하지만 간결하게. 저시력 사용자가 듣기 편하도록 서술형으로 답하세요. '-입니다' 대신 '-예요'를 기본으로 구어체로 응답하세요. '저는' 같은 1인칭 표현은 피하고, '이 작품은', '이 부분은'처럼 작품 중심으로 말하세요."""


class ArtAgent:
    def __init__(self, user_id: str, artwork_id: str, model: str = "gpt-4o", debug: bool = False):
        self.client = OpenAI(api_key=_resolve_api_key())
        self.user_id = user_id
        self.artwork_id = artwork_id
        self.model = model
        self.debug = debug
        self.tools = ToolExecutor(self.client, user_id, artwork_id)
        self.history: List[Dict[str, Any]] = []

    def _debug_log(self, message: str) -> None:
        if self.debug:
            print(f"[debug] {message}", file=sys.stderr)

    def _system_message(self) -> Dict[str, str]:
        return {"role": "system", "content": system_message_content(self.user_id, self.tools.artwork)}

    def start_conversation(self) -> str:
        """대화 시작 시 에이전트가 먼저 인사하고, 필요하면 온보딩 질문을 건넨다."""
        kickoff = {
            "role": "user",
            "content": (
                "(system trigger: 대화가 막 시작되었고 사용자는 아직 아무 말도 하지 않았습니다. "
                "시스템 프롬프트의 '대화 시작 시 온보딩' 규칙에 따라 먼저 인사하고, "
                "필요하다면 온보딩 질문을 건네세요. 이 트리거 메시지 자체는 언급하지 마세요.)"
            ),
        }
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[self._system_message(), kickoff],
            tools=TOOL_SCHEMAS,
            tool_choice="none",
        )
        text = response.choices[0].message.content or ""
        self.history.append({"role": "assistant", "content": text})
        return text

    def chat(self, user_message: str, max_tool_rounds: int = 5) -> str:
        self.history.append({"role": "user", "content": user_message})

        for _ in range(max_tool_rounds):
            messages = [self._system_message()] + self.history
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOL_SCHEMAS,
                tool_choice="auto",
            )
            msg = response.choices[0].message

            if msg.tool_calls:
                self.history.append(msg.model_dump(exclude_none=True))
                for tc in msg.tool_calls:
                    args = json.loads(tc.function.arguments or "{}")
                    self._debug_log(f"tool_call -> {tc.function.name}({json.dumps(args, ensure_ascii=False)})")
                    result = self.tools.call(tc.function.name, args)
                    preview = result if len(result) <= 300 else result[:300] + " ...(truncated)"
                    self._debug_log(f"tool_result <- {tc.function.name}: {preview}")
                    self.history.append(
                        {"role": "tool", "tool_call_id": tc.id, "content": result}
                    )
                continue

            final_text = msg.content or ""
            self.history.append({"role": "assistant", "content": final_text})
            return final_text

        fallback = "(도구 호출이 너무 많아 응답을 생성하지 못했습니다.)"
        self.history.append({"role": "assistant", "content": fallback})
        return fallback
