import base64
import json
import mimetypes
import os
from typing import Any, Dict

from openai import OpenAI

from . import artwork_data, persona_store

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_artwork_metadata",
            "description": (
                "작품의 공식 메타데이터(작가, 제목, 제작연도/기법, 공식 설명, 큐레이터 코멘트)를 조회한다. "
                "'누가 그렸어', '언제 만들어졌어', '무슨 작품이야' 같은 사실/배경 질문에 사용한다."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "describe_artwork_region",
            "description": (
                "작품 이미지의 특정 영역을 GPT 비전으로 시각적으로 묘사한다. "
                "'저기 아래는 뭐야', '오른쪽 삼각형 설명해줘' 같이 이미지 속 형태/색/구도에 대한 질문에 사용한다. "
                "영역이 명확히 특정된 뒤에만 호출할 것 - 후보가 여러 개일 수 있으면 먼저 사용자에게 되물어라."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "description": "설명할 영역의 위치 및 대상 (예: '하단 중앙', '오른쪽의 삼각형 모양 물체')",
                    },
                    "user_question": {
                        "type": "string",
                        "description": "사용자의 원래 질문 (있다면 그대로)",
                    },
                },
                "required": ["region"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_user_persona",
            "description": (
                "사용자의 응답 스타일 선호를 저장/갱신한다. "
                "사용자가 명시적으로 요청했거나(source=explicit), "
                "같은 종류의 선호가 대화에서 반복적으로 드러날 때(source=inferred) 호출한다."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "선호 항목 식별자 (예: color_description, spatial_focus, tone, length)",
                    },
                    "value": {"type": "string", "description": "선호 내용 서술"},
                    "source": {"type": "string", "enum": ["explicit", "inferred"]},
                    "reason": {"type": "string", "description": "이 선호를 저장하는 근거가 된 사용자의 발화/행동"},
                },
                "required": ["key", "value", "source"],
            },
        },
    },
]


class ToolExecutor:
    def __init__(self, client: OpenAI, user_id: str, artwork_id: str):
        self.client = client
        self.user_id = user_id
        artwork = artwork_data.get_artwork(artwork_id)
        if artwork is None:
            raise ValueError(f"Unknown artwork_id: {artwork_id}")
        self.artwork = artwork

    def call(self, name: str, arguments: Dict[str, Any]) -> str:
        if name == "get_artwork_metadata":
            return self._get_metadata()
        if name == "describe_artwork_region":
            return self._describe_region(arguments.get("region", ""), arguments.get("user_question", ""))
        if name == "update_user_persona":
            return self._update_persona(arguments)
        return json.dumps({"error": f"unknown tool: {name}"}, ensure_ascii=False)

    def _get_metadata(self) -> str:
        a = self.artwork
        return json.dumps(
            {
                "title": a["title"],
                "artist": a["artist"],
                "style": a["style"],
                "official_description": a["description"],
                "curator_comment": a["comment"],
            },
            ensure_ascii=False,
        )

    def _describe_region(self, region: str, user_question: str) -> str:
        image_url = self._artwork_image_url()
        rule = f"""당신은 저시력(low-vision) 시각장애인 관람객에게 작품의 특정 영역을 설명하는 미술관 큐레이터입니다.

지금 설명할 영역: {region}
사용자의 질문: {user_question or '(특정 질문 없음, 해당 영역을 전반적으로 설명)'}

- 배경지식이나 주관적 해석 없이, 눈에 보이는 형태·구도·색을 객관적으로 설명하세요.
- 분명히 보이는 내용은 자신 있게 말하세요. "공식 자료에서 확인할 수 없습니다" 같은 문장은 쓰지 마세요.
- 다만 아주 작거나 흐릿한 세부만 "보입니다", "가깝습니다"처럼 신중하게 표현하세요.
- 작품 전체 이미지 중 "{region}"에 해당하는 부분에만 집중해서 설명하세요.
- 개조식이 아닌 서술형으로, 큐레이터가 설명하듯 답하세요."""

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a museum curator describing artworks to low-vision visitors.",
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "다음은 작품의 전체 이미지입니다."},
                        {"type": "image_url", "image_url": {"url": image_url}},
                        {"type": "text", "text": rule},
                    ],
                },
            ],
        )
        return response.choices[0].message.content or ""

    def _artwork_image_url(self) -> str:
        image_path = self.artwork.get("image_path", "")
        if image_path and os.path.exists(image_path):
            mime_type = mimetypes.guess_type(image_path)[0] or "image/jpeg"
            with open(image_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
            return f"data:{mime_type};base64,{encoded}"
        return self.artwork["image_url"]

    def _update_persona(self, arguments: Dict[str, Any]) -> str:
        key = arguments.get("key", "")
        value = arguments.get("value", "")
        source = arguments.get("source", "inferred")
        reason = arguments.get("reason", "")
        persona_store.upsert_preference(self.user_id, key, value, source, reason)
        return json.dumps({"status": "saved", "key": key, "value": value}, ensure_ascii=False)
