# ============================================================
# Nexify - RAG Pipeline Builder
# Converts our knowledge documents into AI-searchable format
# ============================================================

import os
from pathlib import Path

# LangChain components for RAG
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import MarkdownTextSplitter
from langchain.schema import Document
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
        
        # Create a Document object with content and metadata
        doc = Document(
            page_content=content,
            metadata={
                'source': file_path.name,      # filename
                'topic': file_path.stem,        # filename without extension
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
    Why? AI works better with focused, small pieces of text.
    Think of it like highlighting specific paragraphs 
    instead of reading the whole book.
    """
    
    splitter = MarkdownTextSplitter(
        chunk_size=500,      # each chunk = max 500 characters
        chunk_overlap=50     # 50 char overlap between chunks
                             # overlap prevents losing context
                             # at chunk boundaries
    )
    
    chunks = splitter.split_documents(documents)
    print(f"\n✅ Split into {len(chunks)} chunks")
    
    return chunks

# ============================================================
# 3. CREATE VECTOR STORE
# ============================================================

def build_vector_store(chunks):
    """
    Convert text chunks into numbers (embeddings) 
    and store in ChromaDB.
    
    Embeddings = mathematical representation of text meaning.
    Similar meanings = similar numbers = easy to find!
    """
    
    print("\nCreating embeddings and building vector store...")
    print("(This may take a minute...)")
    
    # OpenAI's embedding model converts text to numbers
    embeddings = OpenAIEmbeddings(
        model='text-embedding-3-small'  # cheap and very accurate
    )
    
    # ChromaDB stores these numbers for fast searching
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory='rag/chroma_db'  # save to disk
    )
    
    print("✅ Vector store built and saved!")
    return vector_store

# ============================================================
# 4. TEST THE RAG PIPELINE
# ============================================================

def test_rag(vector_store):
    """
    Test that our RAG pipeline works correctly
    by searching for some sample queries.
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
            # Show first 200 characters of result
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
    print("\nKnowledge base is ready for the AI copilot!")

if __name__ == "__main__":
    build_rag_pipeline()