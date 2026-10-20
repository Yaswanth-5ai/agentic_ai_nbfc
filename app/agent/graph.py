#import asyncio

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from app.mcp_server.client import call_mcp_tool



load_dotenv()

llm = ChatGoogleGenerativeAI(
   model="gemini-3-flash-preview",
)

class LoanAgentState(TypedDict):
    customer_id: str
    question: str
    intent: str
    tool_result: dict
    response: str


# def identify_intent(state: LoanAgentState) -> dict:
#     question = state["question"].lower()

    # if "balance" in question or "outstanding" in question:
    #     intent = "outstanding_balance"

    # elif "emi" in question or "installment" in question:
    #     intent = "emi_details"

    # elif "payment" in question or "transaction" in question:
    #     intent = "payment_history"

    # else:
    #     intent = "unknown"

    # return {"intent": intent}



async def identify_intent(state: LoanAgentState) -> dict:
    prompt = f"""
    You are an intent classifier for an NBFC loan-servicing voice bot.

    Classify the customer's question into exactly one category:

    - outstanding_balance: Questions about remaining loan balance or dues.
    - emi_details: Questions about EMI amounts or upcoming EMI dates.
    - payment_history: Questions about previous payments or transaction status.
    - human_handoff: Requests to speak to a human, customer support, an agent, or a representative.
    - unknown: Unrelated questions or requests that do not fit the categories.

    Return only the category name.
    Customer question: {state["question"]}

    Return only the category name.
    """

    result = await llm.ainvoke(prompt)
    #intent = result.content.strip().lower()
    content = result.content

    if isinstance(content, list):
        intent = "".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        ).strip().lower()
    else:
        intent = str(content).strip().lower()

    allowed_intents = {
        "outstanding_balance",
        "emi_details",
        "payment_history",
        "human_handoff",
        "unknown",
    }

    if intent not in allowed_intents:
        intent = "unknown"

    return {"intent": intent}


def route_by_intent(state: LoanAgentState) -> str:
    return state["intent"]


async def outstanding_balance_node(state: LoanAgentState) -> dict:
    result = await call_mcp_tool(
        "outstanding_balance",
        {"customer_id": state["customer_id"]},
    )
    return {"tool_result": result}


async def emi_details_node(state: LoanAgentState) -> dict:
    result = await call_mcp_tool(
        "emi_details",
        {"customer_id": state["customer_id"]},
    )
    return {"tool_result": result}


async def payment_history_node(state: LoanAgentState) -> dict:
    result = await call_mcp_tool(
        "payment_history",
        {
            "customer_id": state["customer_id"],
            "limit": 5,
        },
    )
    return {"tool_result": result}


async def generate_response(state: LoanAgentState) -> dict:
    intent = state["intent"]
    result = state["tool_result"]

    if not result.get("success"):
        response = result.get(
            "error",
            "I couldn't retrieve your loan information.",
        )

    elif intent == "outstanding_balance":
        amount = result["total_outstanding_amount"]
        response = f"Your total outstanding loan balance is ₹{amount:,.2f}."

    elif intent == "emi_details":
        details = result["emi_details"]

        response = "Here are your upcoming EMI details: " + "; ".join(
            f"{item['loan_type']}: ₹{item['emi_amount']:,.2f}, "
            f"due on {item['next_emi_date']}"
            for item in details
        )

    elif intent == "payment_history":
        payments = result["payments"]

        if not payments:
            response = "No payment records were found."

        else:
            response = "Here is your recent payment history: " + "; ".join(
                f"{item['loan_id']}: ₹{item['amount']:,.2f}, "
                f"date {item['payment_date']}, status {item['status']}"
                for item in payments
            )

    else:
        response = "I couldn't identify your request."

    return {"response": response}

def human_handoff_node(state: LoanAgentState) -> dict:
    return {
        "tool_result": {},
        "response": (
            "I can help with your loan balance, EMI, and payment history. "
            "For further assistance, your request needs to be handled "
            "by our customer support team."
        ),
    }


def unknown_intent_node(state: LoanAgentState) -> dict:
    return {
        "tool_result": {},
        "response": (
            "I'm sorry, I couldn't identify your request. "
            "Please ask about your loan balance, EMI, or payment history."
        ),
    }


builder = StateGraph(LoanAgentState)

builder.add_node("identify_intent", identify_intent)
builder.add_node("outstanding_balance", outstanding_balance_node)
builder.add_node("emi_details", emi_details_node)
builder.add_node("payment_history", payment_history_node)
builder.add_node("generate_response", generate_response)
builder.add_node("unknown", unknown_intent_node)
builder.add_node("human_handoff", human_handoff_node)

builder.add_edge(START, "identify_intent")

builder.add_conditional_edges(
    "identify_intent",
    route_by_intent,
    {
        "outstanding_balance": "outstanding_balance",
        "emi_details": "emi_details",
        "payment_history": "payment_history",
        "unknown": "unknown",
        "human_handoff": "human_handoff",
    },
)

builder.add_edge("outstanding_balance", "generate_response")
builder.add_edge("emi_details", "generate_response")
builder.add_edge("payment_history", "generate_response")

builder.add_edge("generate_response", END)
builder.add_edge("unknown", END)
builder.add_edge("human_handoff", END)

checkpointer = MemorySaver()

loan_agent = builder.compile(
    checkpointer=checkpointer
)