# Intelli-Doc: An Academic Research Assistant

#### **1. Objective**
A web application that allows a user to "chat" with their academic papers. The system ingests multiple PDF documents, answer user questions based on their content, and provide citations for every answer to ensure verifiability.

#### **2. Problem Statement (The "Why")**
Researchers, students, and professionals spend countless hours manually searching through dense documents to find specific information. This process is slow, tedious, and prone to error. Our application solves this by creating an intelligent, searchable knowledge base from a user's document library, enabling them to extract precise information in seconds. This is a real-world problem in fields like research, legal analysis, and corporate training.

#### **3. Key Features**
* **Multi-Document Q&A:** Ingest and query an entire library of PDF documents, not just one.
* **Source Citations:** For each answer, the model will cite the source document and show the exact text chunk used, building trust and allowing for fact-checking.
* **Conversational Memory:** The system will remember the chat history to allow for follow-up questions.
* **API-First Design:** The core logic will be exposed through a REST API, a standard industry practice.
* **Persistent Knowledge Base:** The processed document knowledge will be saved locally, so it doesn't need to be re-processed every time the app starts.

#### **4. Tech Stack**
* **Language:** Python
* **Web Framework:** FastAPI
* **AI Framework:** LangChain
* **LLM & Embeddings:** OpenAI
* **Vector Database:** **ChromaDB** (A popular, open-source vector store that runs locally)
* **PDF Processing:** `pypdf`
* **Deployment:** **Docker**

### **5. Run the Application**

* **Docker:** `docker-compose up --build`

* **FastAPI:** `uvicorn app.main:app --reload`