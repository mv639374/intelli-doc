# app/engine.py

import os
from typing import List
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader  # Use TextLoader for .txt file
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.messages import BaseMessage

# Import our configuration
from . import config

# Define persistent storage paths
ABS_PATH = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(ABS_PATH, "..", "vector_store")


class RagEngine:
    """
    This class encapsulates the entire RAG pipeline, from document processing
    to answering questions with source citations.
    """

    def __init__(self):
        """Initializes the core components of the RAG engine."""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=100
        )
        self.embeddings = OpenAIEmbeddings(api_key=config.OPENAI_API_KEY)
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=config.OPENAI_API_KEY)

        self.vector_store = Chroma(
            persist_directory=DB_DIR, embedding_function=self.embeddings
        )
        
        # --- ENHANCEMENT 1: Configure the Retriever ---
        # We are configuring the retriever to fetch the top 5 most relevant chunks (k=5).
        # The default is 4. Increasing this gives the LLM more context to find the
        # correct answer, which is crucial for specific questions like titles or authors.
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})

        self.chain = self._create_conversational_rag_chain()

    def _create_conversational_rag_chain(self):
        """
        Creates and returns a conversational RAG chain.
        """
        contextualize_q_system_prompt = (
            "Given a chat history and the latest user question "
            "which might reference context in the chat history, "
            "formulate a standalone question which can be understood "
            "without the chat history. Do NOT answer the question, "
            "just reformulate it if needed and otherwise return it as is."
        )
        
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        
        history_aware_retriever = create_history_aware_retriever(
            self.llm, self.retriever, contextualize_q_prompt
        )

        # --- ENHANCEMENT 2: Refine the Answering Prompt ---
        # We've made the prompt slightly more direct and explicit, telling the model
        # to base its answer strictly on the provided context. This reduces the
        # chance of it using prior knowledge or getting confused by irrelevant chunks.
        qa_system_prompt = (
            "You are an assistant for question-answering tasks. "
            "Use only the following pieces of retrieved context to answer the question. "
            "If you don't know the answer from the context, just say that you don't know. "
            "Keep the answer concise."
            "\n\n"
            "{context}"
        )
        
        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", qa_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        
        question_answer_chain = create_stuff_documents_chain(self.llm, qa_prompt)

        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
        
        return rag_chain

    def add_document(self, file_path: str):
        """
        Loads a PDF, splits it into chunks, and adds it to the vector store.
        """
        print(f"Processing document: {file_path}")
        loader = PyPDFLoader(file_path)
        docs = loader.load_and_split(self.text_splitter)
        print(f"Created {len(docs)} document chunks.")
        self.vector_store.add_documents(docs)
        print("Document added to vector store.")

    def ask_question(self, question: str, chat_history: List[BaseMessage] = []):
        """
        Takes a user's question and chat history, invokes the RAG chain,
        and returns the answer and source documents.
        """
        result = self.chain.invoke({"input": question, "chat_history": chat_history})
        
        sources = [
            {
                "source": doc.metadata.get("source", "N/A"),
                "page": doc.metadata.get("page", "N/A"),
                "content": doc.page_content,
            }
            for doc in result.get("context", [])
        ]
        
        return {"answer": result["answer"], "sources": sources}