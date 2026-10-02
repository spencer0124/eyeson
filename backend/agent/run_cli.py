import argparse

from . import artwork_data
from .art_agent import ArtAgent


def main():
    parser = argparse.ArgumentParser(description="Eyeson art docent agent (CLI demo)")
    parser.add_argument("--user_id", default="demo_user")
    parser.add_argument("--artwork_id", default=None, help="eng_id of the artwork, e.g. self-portrait.jpg")
    parser.add_argument("--list", action="store_true", help="사용 가능한 작품 목록 출력")
    parser.add_argument(
        "--debug", action="store_true", help="어떤 도구(tool)가 어떤 인자로 호출되고 무엇을 반환했는지 stderr에 출력"
    )
    parser.add_argument(
        "--engine",
        choices=["legacy", "langchain", "split"],
        default="legacy",
        help=(
            "legacy: 수동 OpenAI tool-calling 루프(ArtAgent, 기본값) / "
            "langchain: LangGraph 기반 재구현(ArtAgentLC, tool-calling과 답변 생성이 한 모델에 결합) / "
            "split: tool 호출 결정(Planner)과 답변 생성(Answerer)을 분리한 실험 버전(ArtAgentSplit)"
        ),
    )
    args = parser.parse_args()

    if args.list or not args.artwork_id:
        print("사용 가능한 작품:")
        for a in artwork_data.list_artworks():
            print(f"  - {a['artwork_id']}: {a['title']}")
        if not args.artwork_id:
            return

    if args.engine == "langchain":
        from .art_agent_lc import ArtAgentLC as Agent
    elif args.engine == "split":
        from .art_agent_split import ArtAgentSplit as Agent
    else:
        Agent = ArtAgent

    agent = Agent(user_id=args.user_id, artwork_id=args.artwork_id, debug=args.debug)
    print(f"[{args.artwork_id}] 와 대화를 시작합니다. 종료: exit / quit")
    opening = agent.start_conversation()
    print(f"Agent: {opening}")
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if user_input.lower() in ("exit", "quit"):
            break
        if not user_input:
            continue
        reply = agent.chat(user_input)
        print(f"Agent: {reply}")


if __name__ == "__main__":
    main()
