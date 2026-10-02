# Eyeson Art Docent Agent (prototype)

저시력/시각장애인 관람객을 위한, 작품별 대화형 도슨트 에이전트 프로토타입입니다.
기존 FastAPI 서버(`routers/`, `services/`)에는 연결하지 않고, 같은 기능(작품 메타데이터 조회,
GPT 비전 기반 영역 설명)을 함수 도구로 재사용하는 독립 실행형 CLI입니다.

## 구성

- `persona_store.py` — 사용자별 응답 스타일 선호를 `agent/data/personas/{user_id}.json`에 저장/조회.
- `artwork_data.py` — `backend/data/data_david.json`에서 작품 메타데이터 + S3 이미지 URL 로드.
- `tools.py` — 에이전트가 호출하는 3개 도구:
  - `get_artwork_metadata` — 작가/제목/제작정보/공식 설명 (`description_router`, `metadata_router` 역할 재사용)
  - `describe_artwork_region` — 특정 영역을 GPT-4o 비전으로 서술 (`openai_service.answer_user_prompt` 역할 재사용)
  - `update_user_persona` — 명시적 요청 또는 반복 패턴 감지 시 페르소나 저장
- `art_agent.py` — `ArtAgent`: 시스템 프롬프트 구성(페르소나 주입) + tool-calling 대화 루프.
- `art_agent_lc.py` — `ArtAgentLC`: 같은 시스템 프롬프트/도구를 LangGraph(`create_react_agent`)로 재구현한 버전. `ArtAgent`와 동일한 인터페이스(`start_conversation`/`chat`)를 제공.
- `art_agent_split.py` — `ArtAgentSplit`: tool 호출 결정(Planner)과 최종 답변 작성(Answerer)을 서로 다른 모델 호출로 분리한 실험 버전. Planner는 `tool_choice="required"`로 매 턴 도구 호출(또는 종료 신호 `finish_planning`)만 할 수 있고, Answerer는 도구 없이 Planner가 넘긴 근거만으로 글을 씀.
- `evaluate_art_agent.py` — 프롬프트 variant별(`rule_based`/`few_shot`/`tool_calling_few_shot`) 자동 평가 스크립트. 결과는 `eval_results/`에 저장.
- `run_cli.py` — 터미널에서 바로 대화해볼 수 있는 REPL.

## 실행 방법

1. `backend/.env`에 `OPENAI_API_KEY` 설정 (`.env.example` 참고).
2. 필요 패키지: `openai`, `python-dotenv` (이미 `multiA` conda env에 설치되어 있음. 로컬 `eyeson` conda env는
   현재 비어 있어 사용 불가 — 별도 env를 쓰려면 `agent/requirements.txt` 설치).
3. `backend/` 디렉토리에서:

```bash
python -m agent.run_cli --list                     # 작품 목록 확인
python -m agent.run_cli --artwork_id wanderer-above-the-sea-of-fog.jpg --user_id demo_user
python -m agent.run_cli --artwork_id wanderer-above-the-sea-of-fog.jpg --user_id demo_user --engine langchain  # LangGraph 버전
python -m agent.run_cli --artwork_id wanderer-above-the-sea-of-fog.jpg --user_id demo_user --engine split      # Planner/Answerer 분리 버전
```

## 동작 방식 (요구사항 매핑)

1. **개인화 페르소나** — 대화 중 사용자가 스타일을 명시하면(`색은 간단히만 말해줘` 등) 즉시,
   또는 같은 패턴이 반복되면 추론적으로 `update_user_persona`를 호출해 저장합니다.
   저장된 선호는 다음 턴부터 시스템 프롬프트에 주입되어 이후 모든 응답에 반영됩니다.
2. **모호한 질문 재질문** — 작품 전체 이미지가 매 턴 컨텍스트에 포함되므로, 에이전트가 스스로
   이미지를 보고 후보가 여러 개인지 판단합니다. 후보가 여럿이면 도구를 호출하지 않고 먼저
   구체적으로 되묻습니다 (시스템 프롬프트의 "모호한 질문 처리" 규칙).
3. **기존 API를 도구로 재사용** — 실제 서버에 HTTP로 붙는 대신, 같은 프롬프트/로직을 함수로
   감싸 OpenAI tool-calling 스키마로 노출했습니다.

## 알려진 한계 / 다음 단계 후보

- `describe_artwork_region`은 실제 크롭 이미지가 아니라 전체 이미지 + 자연어 영역 지시로 동작합니다
  (프론트엔드의 확대/드래그 크롭 UI와 연결하면 원본 `gpt-artwork` 엔드포인트처럼 실제 크롭 이미지를
  함께 넘길 수 있습니다).
- persona 스키마가 자유 형식(key-value)이라 프론트 UI에서 편집 가능한 구조로 다듬으면 좋습니다.
- 현재 단일 프로세스 인메모리 히스토리(`ArtAgent.history`)만 사용 — 세션/DB 영속화는 아직 없습니다.
- 대화 로그 기반으로 실제 반복 선호를 더 안정적으로 감지하려면, 프롬프트 판단 외에
  `evidence_count` 임계치를 코드에서 직접 세는 방식도 고려할 수 있습니다.
