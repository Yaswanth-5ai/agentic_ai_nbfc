import asyncio
import uuid

import streamlit as st

from app.agent.graph import loan_agent


# Page configuration
st.set_page_config(
    page_title="NBFC Loan Assistant",
    page_icon="💳",
    layout="centered",
)

st.title("💳 NBFC Loan Assistant")
st.caption("Your AI assistant for loan balance, EMI details, and payment history.")

# Demo customer ID
# In production, obtain this from an authenticated customer session.
CUSTOMER_ID = "C001"


# Initialize conversation state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())


# Display customer information for the demo
with st.sidebar:
    st.subheader("Customer Information")
    st.write("Customer ID:", CUSTOMER_ID)
    st.write("Conversation:", st.session_state.thread_id[:8])

    if st.button("New Conversation"):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()


# Display existing messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Chat input
question = st.chat_input("Ask something about your loan...")

if question:
    # Display and store the customer message
    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.markdown(question)

    # Use the same thread ID for this conversation
    config = {
        "configurable": {
            "thread_id": st.session_state.thread_id
        }
    }

    # Execute the existing LangGraph agent
    with st.chat_message("assistant"):
        with st.spinner("Checking your loan information..."):
            try:
                result = asyncio.run(
                    loan_agent.ainvoke(
                        {
                            "customer_id": CUSTOMER_ID,
                            "question": question,
                            "intent": "",
                            "tool_result": {},
                            "response": "",
                        },
                        config=config,
                    )
                )

                answer = result["response"]
                st.markdown(answer)

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

            except Exception as exc:
                st.error("Sorry, I couldn't process your request.")
                st.exception(exc)

                print(f"Agent error: {type(exc).__name__}: {exc}")