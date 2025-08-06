# my_rag_project/app/chains/rag_chain.py

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain_core.messages import trim_messages, AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

# Import configuration constants
from app.config import (
    MODEL_NAME, CHAT_MODEL, CHAT_HISTORY_WINDOW_SIZE
)


def get_conversational_chain_with_memory(model_name: str, vectorstore: FAISS, api_key: str):
    """
    Constructs a LangChain RAG conversational chain with explicit memory trimming.
    """
    if model_name != "Google AI":
        raise ValueError("Unsupported model_name. Currently only 'Google AI' is supported.")

    llm = ChatGoogleGenerativeAI(model=CHAT_MODEL, temperature=0.3, google_api_key=api_key)
    retriever = vectorstore.as_retriever()

    # Define a runnable that explicitly trims the chat history
    history_trimmer = trim_messages(
        token_counter=llm,
        max_tokens=CHAT_HISTORY_WINDOW_SIZE * 50, # Rough estimate for 3 exchanges (6 messages)
        strategy="last",
        include_system=True,
        start_on="human",
        allow_partial=False
    )

    # 1. History-aware Retriever: Reformulates the input question based on trimmed chat history
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Given a chat history and the latest user question "
                       "which might reference context in the chat history, "
                       "formulate a standalone question which can be understood without the chat history. "
                       "Do NOT answer the question, just reformulate it if needed and otherwise return it as is."),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    # 2. Answer Generation Chain: Combines retrieved documents and trimmed chat history for the final answer
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", """
            You are a professional AI assistant for Semanto Ghosh.Your name is "SERA" (Semanto's Executive Response & AI Assistant) you specialize in answering questions based on his resume, research, work experience, and professional background.

            Your responsibilities include:
            - Answering user questions using the context provided from Semanto's profile
            - If the answer is not present in the context, clearly say:
              "This information is not available in Semanto's profile context. However, based on general knowledge, here’s what I can tell you..."
            - Never make up answers about Semanto beyond what the context provides
            - Be polite, concise, and professional in tone

            Context:
            {context}
            """),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    document_chain = create_stuff_documents_chain(llm, qa_prompt)

    # 3. Full RAG Chain: Connects history-aware retriever with answer generation
    rag_chain = create_retrieval_chain(history_aware_retriever, document_chain)

    # 4. Integrate history trimming AND ensure 'output' key for the tracer:
    final_chain_with_trimming = (
        {
            "input": lambda x: x["input"],
            "chat_history": lambda x: history_trimmer.invoke(x["chat_history"]),
        }
        | rag_chain
        | RunnableLambda(lambda x: {"output": x.get("answer", "")})
    )

    return final_chain_with_trimming