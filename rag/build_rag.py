# ============================================================
# Nexify - RAG Pipeline Builder
# Using Groq (FREE) + Local Embeddings (FREE)
# ============================================================

import os
from pathlib import Path
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import MarkdownTextSplitter
from langchain_core.documents import Document
from dotenv import load_dotenv


# Load environment variables (API keys)
load_dotenv()

# ============================================================
# 1. READ ALL KNOWLEDGE BASE DOCUMENTS
# ============================================================

def load_knowledge_documents():
    """
    Read all markdown files from knowledge_base folder.
    Returns a list of Document objects.
    """
    
    knowledge_base_path = Path('rag/knowledge_base')
    documents = []
    
    # Loop through every .md file in the folder
    for file_path in sorted(knowledge_base_path.glob('*.md')):
        
        # Read the file content
        content = file_path.read_text(encoding='utf-8')
        
        # Create a Document object
        doc = Document(
            page_content=content,
            metadata={
                'source': file_path.name,
                'topic': file_path.stem,
            }
        )
        
        documents.append(doc)
        print(f"📄 Loaded: {file_path.name}")
    
    return documents

# ============================================================
# 2. SPLIT DOCUMENTS INTO CHUNKS
# ============================================================

def split_documents(documents):
    """
    Split large documents into smaller chunks.
    AI works better with small focused pieces of text.
    """
    
    splitter = MarkdownTextSplitter(
        chunk_size=500,    # max 500 characters per chunk
        chunk_overlap=50   # 50 char overlap to keep context
    )
    
    chunks = splitter.split_documents(documents)
    print(f"\n✅ Split into {len(chunks)} chunks")
    
    return chunks

# ============================================================
# 3. CREATE VECTOR STORE (FREE Local Embeddings)
# ============================================================

def build_vector_store(chunks):
    """
    Convert text chunks into numbers (embeddings)
    and store in ChromaDB.
    
    We use HuggingFace embeddings — completely FREE!
    Runs locally on your computer — no API needed!
    """
    
    print("\nLoading embedding model...")
    print("(First time downloads ~90MB — please wait...)")
    
    # This runs completely on your computer — FREE!
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        # Small but powerful model
        # Perfect for our use case
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    print("✅ Embedding model loaded!")
    print("\nBuilding vector store...")
    
    # Store embeddings in ChromaDB
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory='rag/chroma_db'
    )
    
    print("✅ Vector store built and saved!")
    return vector_store

# ============================================================
# 4. TEST THE RAG PIPELINE
# ============================================================

def test_rag(vector_store):
    """
    Test our RAG pipeline with sample queries.
    """
    
    print("\n" + "="*50)
    print("TESTING RAG PIPELINE")
    print("="*50)
    
    test_queries = [
        "What is the churn rate?",
        "How do I retain at-risk members?",
        "What is MRR?",
        "What are fraud warning signals?"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        
        # Search for most relevant chunks
        results = vector_store.similarity_search(query, k=1)
        
        if results:
            preview = results[0].page_content[:200]
            source = results[0].metadata['source']
            print(f"📌 Found in: {source}")
            print(f"💬 Preview: {preview}...")

# ============================================================
# 5. MAIN FUNCTION
# ============================================================

def build_rag_pipeline():
    print("="*50)
    print("BUILDING NEXIFY RAG PIPELINE")
    print("="*50)
    
    # Step 1: Load documents
    print("\nStep 1: Loading knowledge documents...")
    documents = load_knowledge_documents()
    print(f"✅ Loaded {len(documents)} documents")
    
    # Step 2: Split into chunks
    print("\nStep 2: Splitting into chunks...")
    chunks = split_documents(documents)
    
    # Step 3: Build vector store
    print("\nStep 3: Building vector store...")
    vector_store = build_vector_store(chunks)
    
    # Step 4: Test it
    test_rag(vector_store)
    
    print("\n" + "="*50)
    print("RAG PIPELINE COMPLETE!")
    print("="*50)
    print("\nKnowledge base is ready for AI copilot!")

if __name__ == "__main__":
    build_rag_pipeline()