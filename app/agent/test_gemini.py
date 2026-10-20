from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash",
    temperature=0,
)

response = llm.invoke(
    """
    Identify the intent of this customer question:
    "How much money do I still owe on my loan?"

    Choose one:
    - outstanding_balance
    - emi_details
    - payment_history

    Return only the intent.
    """
)

print(response.content)