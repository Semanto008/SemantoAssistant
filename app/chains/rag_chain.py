# app/chains/rag_chain.py

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain_core.messages import trim_messages, AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

# Import configuration constants from your config.py
from app.config import (
    MODEL_NAME, CHAT_MODEL, CHAT_HISTORY_WINDOW_SIZE
)


def get_conversational_chain_with_memory(model_name: str, vectorstore: FAISS, api_key: str):
    """
    Constructs a LangChain RAG conversational chain with explicit memory trimming.

    This chain integrates:
    1. A history-aware retriever that rephrases questions based on chat history.
    2. A document combining chain that stuffs retrieved context into the prompt.
    3. Explicit trimming of chat history to control token usage.
    4. Ensures the final output is in a consistent 'output' key.

    Args:
        model_name (str): The name of the LLM model to use (e.g., "Google AI").
        vectorstore (FAISS): The FAISS vector store for document retrieval.
        api_key (str): Your Google AI API key.

    Returns:
        Runnable: An LCEL-compatible retrieval chain with history awareness and output formatting.
    """
    if model_name != "Google AI":
        raise ValueError("Unsupported model_name. Currently only 'Google AI' is supported.")

    llm = ChatGoogleGenerativeAI(model=CHAT_MODEL, temperature=0.3, google_api_key=api_key)
    retriever = vectorstore.as_retriever()

    # Define a runnable that explicitly trims the chat history
    # This uses the LLM's tokenizer for more accurate token counting.
    # CHAT_HISTORY_WINDOW_SIZE * 50 is a rough estimate; adjust max_tokens based on testing.
    history_trimmer = trim_messages(
        token_counter=llm,
        max_tokens=CHAT_HISTORY_WINDOW_SIZE * 50, # e.g., 6 messages * ~50 tokens/message
        strategy="last", # Keep the most recent messages
        include_system=True, # Always include system messages if present
        start_on="human", # Ensure the history starts with a human message or system+human
        allow_partial=False # Do not allow partial messages if they exceed the token limit
    )

    # 1. History-aware Retriever Prompt: Guides the LLM to reformulate the question
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Given a chat history and the latest user question "
                       "which might reference context in the chat history, "
                       "formulate a standalone question which can be understood without the chat history. "
                       "Do NOT answer the question, just reformulate it if needed and otherwise return it as is."),
            MessagesPlaceholder("chat_history"), # Placeholder for the trimmed chat history
            ("human", "{input}"), # The current user's question
        ]
    )

    # Create the history-aware retriever chain
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    # 2. Answer Generation Prompt: Guides the LLM to answer using retrieved context and history
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", """
            You are a professional AI assistant for Semanto Ghosh. Your name is "SERA" (Semanto's Executive Response & AI Assistant) you specialize in answering questions based on his resume, research, work experience, and professional background.

            Your responsibilities include:
            - Answering user questions using the context provided from Semanto's profile
            - If the answer is not present in the context, clearly say:
              "This information is not available in Semanto's profile context. However, based on general knowledge, here’s what I can tell you..."
            - Never make up answers about Semanto beyond what the context provides
            - Be polite, concise, and professional in tone

            Context:
            {context}
            """),
            MessagesPlaceholder("chat_history"), # Trimmed chat history is also passed here for final answer generation
            ("human", "{input}"), # The original (or reformulated) user input
        ]
    )

    # Create the document combining chain (stuffs context into the prompt)
    document_chain = create_stuff_documents_chain(llm, qa_prompt)

    # 3. Full RAG Chain: Combines the history-aware retriever with the document chain
    rag_chain = create_retrieval_chain(history_aware_retriever, document_chain)

    # 4. Final Chain with History Trimming and Output Formatting:
    # This uses RunnablePassthrough.assign to create an input dictionary for the rag_chain,
    # applying history_trimmer to 'chat_history' before passing it.
    # Finally, it maps the 'answer' output from rag_chain to an 'output' key for consistency.
    final_chain_with_trimming = (
        {
            "input": lambda x: x["input"], # Pass the user's input through
            "chat_history": lambda x: history_trimmer.invoke(x["chat_history"]), # Trim history before passing
        }
        | rag_chain # Pass prepared inputs to the RAG chain
        | RunnableLambda(lambda x: {"output": x.get("answer", "")}) # Ensure 'output' key is present
    )

    return final_chain_with_trimming
