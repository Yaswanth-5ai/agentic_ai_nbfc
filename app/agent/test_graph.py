import asyncio

from app.agent.graph import loan_agent

questions = [
    # Outstanding balance
    "How much money do I still owe?",
    "What is the remaining amount on my loans?",]

# #questions = [
#     # Outstanding balance
#     "How much money do I still owe?",
#     "What is the remaining amount on my loans?",
#     "Can you tell me my pending loan dues?",

#     # EMI details
#     "When do I need to pay my next installment?",
#     "How much should I pay this month?",
#     "Tell me my upcoming EMI dates.",

#     # Payment history
#     "Was my last transaction successful?",
#     "Show me my previous loan payments.",
#     "Did my latest installment go through?",

#     # Unknown requests
#     "What is the weather today?",
#     "I want to speak to a customer support representative.",
# ]


async def main():
    for question in questions:
        result = await loan_agent.ainvoke(
            {
                "customer_id": "C001",
                "question": question,
                "intent": "",
                "tool_result": {},
                "response": "",
            },
            config={
                "configurable": {
                    "thread_id": "conversation_001"
                }
            }
        )

        print(f"\nQuestion: {question}")
        print(f"Intent: {result['intent']}")
        print(f"Tool result: {result['tool_result']}")
        print(f"Response: {result['response']}")


if __name__ == "__main__":
    asyncio.run(main())