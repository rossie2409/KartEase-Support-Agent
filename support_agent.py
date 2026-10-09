

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
            "gemini-3.5-flash-lite"
        ),
        google_api_key=api_key,
    )

    return llm.bind_tools([policy_search, order_lookup])


def format_response(content):
    """Convert Gemini's response into readable text."""
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

    messages = [
        (
            "system",
            "You are the KartEase customer support assistant. "
            "Use policy_search for policy questions and order_lookup "
            "for specific order questions. Never invent policy details "
            "or order information. If the order ID is missing, ask for it. "
            "Answer clearly and concisely using the tool results."
        )
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

            print(
                f"\nAssistant: "
                f"{format_response(response.content)}\n"
            )

        except Exception as exc:
            print(f"\nAn error occurred: {exc}\n")


if __name__ == "__main__":
    main()
