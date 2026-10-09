

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage

from search_policies import search_policies
from order_tools import lookup_order


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


@tool
def policy_search(question: str) -> str:
    """Search KartEase policies about returns, refunds, payments, shipping, and warranty."""
    return search_policies(question)


@tool
def order_lookup(order_id: str) -> str:
    """Look up a KartEase order using its order ID, such as KE1001."""
    result = lookup_order(order_id)

    if isinstance(result, dict):
        return "\n".join(
            f"{key}: {value}" for key, value in result.items()
        )

    return str(result)


def create_agent():
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY is missing from the .env file."
        )

    llm = ChatGoogleGenerativeAI(
        model=os.getenv(
            "GEMINI_MODEL",
            "gemini-3.5-flash-lite",
        ),
        google_api_key=api_key,
    )

    return llm.bind_tools([policy_search, order_lookup])


def format_response(content):
    """Extract readable text from Gemini's response."""
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []

        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(item["text"])
            elif isinstance(item, str):
                parts.append(item)

        return "\n".join(parts)

    return str(content)


def main():
    llm_with_tools = create_agent()

    system_prompt = (
        "You are the KartEase customer support assistant. "
        "Only answer questions related to KartEase orders and policies. "
        "Use policy_search for questions about returns, refunds, "
        "payments, shipping, warranties, and other KartEase policies. "
        "Use order_lookup for questions about a specific order. "
        "For questions that are unrelated to KartEase orders or policies, "
        "politely explain that you can only help with KartEase orders "
        "and policies. Do not answer unrelated questions using "
        "general knowledge. "
        "For policy questions, base your answer on the results returned "
        "by policy_search. If the search cannot find relevant policy "
        "information, explain that you could not find the answer in "
        "the KartEase policies. Do not guess or invent policy details. "
        "Never invent order information. If the order ID is missing, "
        "ask the customer to provide it. "
        "Answer politely, clearly, and concisely."
    )

    messages = [
        ("system", system_prompt)
    ]

    print("KartEase Support Agent")
    print("Ask about policies or orders. Type 'exit' to quit.\n")

    while True:
        question = input("You: ").strip()

        if question.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        if not question:
            continue

        messages.append(("human", question))

        try:
            response = llm_with_tools.invoke(messages)
            messages.append(response)

            while response.tool_calls:
                for tool_call in response.tool_calls:
                    print(f"[Tool used: {tool_call['name']}]")
                    if tool_call["name"] == "policy_search":
                        result = policy_search.invoke(
                            tool_call["args"]
                        )

                    elif tool_call["name"] == "order_lookup":
                        result = order_lookup.invoke(
                            tool_call["args"]
                        )

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
            print(f"\nAssistant: {answer}\n")

        except Exception as exc:
            print(f"\nAn error occurred: {exc}\n")


if __name__ == "__main__":
    main()
