from app.agents.demand_analyst import (
    build_demand_analyst_agent,
    parse_travel_task_book_response,
)


def main() -> None:
    # 先构建智能体图
    graph = build_demand_analyst_agent("cheyann")

    # 调用一次，模拟用户输入
    state = graph.invoke(
        {"messages": [{"role": "user", "content": "我想去上海玩3天"}]}
    )

    # LangGraph 返回的 state["messages"] 是一组 Message 对象（如 AIMessage）
    last_msg_obj = state["messages"][-1]
    print(type(last_msg_obj), last_msg_obj)  # 先看下结构

    # 如果是标准 AIMessage，这里用属性访问
    last_msg_text = last_msg_obj.content

    parsed = parse_travel_task_book_response(last_msg_text)
    print(parsed.model_dump())


if __name__ == "__main__":
    main()