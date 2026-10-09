

import gradio as gr
from langchain_core.messages import ToolMessage

from support_agent import create_agent, format_response
from support_agent import policy_search, order_lookup


SYSTEM_PROMPT = (
    "You are the KartEase customer support assistant. "
    "Only answer questions related to KartEase orders and policies. "
    "Use policy_search for policy questions and order_lookup for "
    "specific orders. Use both tools when needed. "
    "For unrelated questions, reply exactly: "
    "'Sorry, I can only help with KartEase orders and policies.' "
    "Base policy answers on retrieved policy information. "
    "Never invent order details or policy information. "
    "Answer politely, clearly, and concisely."
)

llm_with_tools = create_agent()


def respond(message, history):
    if not message.strip():
        return "Please enter a question."

    messages = [("system", SYSTEM_PROMPT)]

    # Restore this chat's previous conversation.
    for item in history:
        if isinstance(item, dict):
            role = item.get("role")
            content = item.get("content", "")

            if role == "user":
                messages.append(("human", content))
            elif role == "assistant":
                messages.append(("ai", content))

    messages.append(("human", message))

    tools_used = []

    try:
        response = llm_with_tools.invoke(messages)
        messages.append(response)

        while response.tool_calls:
            for tool_call in response.tool_calls:
                name = tool_call["name"]
                tools_used.append(name)

                if name == "policy_search":
                    result = policy_search.invoke(tool_call["args"])
                elif name == "order_lookup":
                    result = order_lookup.invoke(tool_call["args"])
                else:
                    result = "Unknown tool requested."

                messages.append(
                    ToolMessage(
                        content=str(result),
                        tool_call_id=tool_call["id"],
                    )
                )

            response = llm_with_tools.invoke(messages)
            messages.append(response)

        answer = format_response(response.content)

        if tools_used:
            answer += "\n\n**Tools used:** " + ", ".join(
                dict.fromkeys(tools_used)
            )

        return answer

    except Exception as exc:
        print(f"Web app error: {exc}")
        return "Sorry, something went wrong. Please try again."


demo = gr.ChatInterface(
    fn=respond,
    title="KartEase Support Assistant",
    description=(
        "Welcome! Ask about orders, shipping, returns, refunds, "
        "payments, and warranty policies."
    ),
    examples=[
        "How many days do I have to return a phone?",
        "Where is my order KE1002?",
        "My return for KE1006 was picked up. When will I get my refund?",
        "Write me a poem about Diwali.",
    ],
)

if __name__ == "__main__":
    demo.launch()
