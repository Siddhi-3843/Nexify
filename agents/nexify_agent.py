# Fix import path
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================================
# Nexify - AI Agent (Modern LangGraph version)
# ============================================================

from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

# Import our 5 tools
from agents.tools import (
    get_revenue_summary,
    get_member_stats,
    get_at_risk_members,
    draft_retention_email,
    search_knowledge_base
)

load_dotenv()

# ============================================================
# 1. SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are Nexify AI — a smart, friendly business intelligence 
assistant for fitness and wellness businesses.

You help business owners understand their data and make 
better decisions. You have access to real business data 
through your tools.

YOUR PERSONALITY:
- Friendly and encouraging
- Clear and concise — business owners are busy!
- Always back up answers with real data
- Proactively suggest next actions
- Use emojis to make responses friendly

YOUR TOOLS:
1. get_revenue_summary — for ANY question about money, 
   revenue, payments, or financial performance
2. get_member_stats — for ANY question about members, 
   customers, subscriptions, or membership numbers
3. get_at_risk_members — for ANY question about churn risk,
   who might leave, or retention concerns
4. draft_retention_email — for ANY request to write, draft,
   or create emails for members
5. search_knowledge_base — for ANY question about KPIs,
   definitions, benchmarks, or best practices

IMPORTANT RULES:
- ALWAYS use a tool to get real data before answering
- NEVER make up numbers — only use data from tools
- After sharing data, ALWAYS suggest 1-2 next actions
- Keep responses clear and easy to understand
"""

# ============================================================
# 2. BUILD THE AGENT
# ============================================================

def build_nexify_agent():
    """
    Build and return the Nexify AI agent.
    Uses LangGraph's modern ReAct agent.
    """
    
    # Initialize Groq LLM — FREE!
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )
    
    # All 5 tools
    tools = [
        get_revenue_summary,
        get_member_stats,
        get_at_risk_members,
        draft_retention_email,
        search_knowledge_base
    ]
    
    # Create modern ReAct agent
    # ReAct = Reasoning + Acting
    # Agent thinks step by step before acting
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=SYSTEM_PROMPT
    )
    
    return agent

# ============================================================
# 3. CHAT FUNCTION
# ============================================================

# Store conversation history
conversation_history = []

def chat_with_nexify(agent, user_message: str) -> str:
    """
    Send a message to agent and get response.
    Maintains conversation history for context.
    """
    
    # Add user message to history
    conversation_history.append(
        HumanMessage(content=user_message)
    )
    
    try:
        # Send to agent with full history
        response = agent.invoke({
            "messages": conversation_history
        })
        
        # Get the last message (agent's response)
        ai_response = response["messages"][-1].content
        
        # Add to history for next turn
        from langchain_core.messages import AIMessage
        conversation_history.append(
            AIMessage(content=ai_response)
        )
        
        return ai_response
    
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

# ============================================================
# 4. TEST THE AGENT
# ============================================================

if __name__ == "__main__":
    print("="*50)
    print("NEXIFY AI AGENT TEST")
    print("="*50)
    print("Building agent...")
    
    agent = build_nexify_agent()
    
    print("✅ Agent ready!\n")
    print("Testing with sample questions...\n")
    
    test_questions = [
        "How many members do we have?",
        "What is our total revenue?",
        "Who are our most at-risk members?",
    ]
    
    for question in test_questions:
        print(f"\n{'='*50}")
        print(f"👤 Question: {question}")
        print(f"{'='*50}")
        response = chat_with_nexify(agent, question)
        print(f"\n🤖 Nexify AI: {response}")
        print()