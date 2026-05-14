# ============================================================
# Nexify - Agent Tools
# These are the 5 tools our AI agent can use
# ============================================================

import sqlite3
import pandas as pd
from pathlib import Path
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

# Database path
DB_PATH = 'database/nexify.db'

# ============================================================
# HELPER FUNCTION — Safe Database Query
# ============================================================

def query_database(sql: str) -> dict:
    """
    Safely run a SQL query and return results.
    Only allows SELECT queries — can never delete or modify data!
    """
    
    # Security check — only allow reading data
    if not sql.strip().upper().startswith('SELECT'):
        return {'error': 'Only SELECT queries are allowed'}
    
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(sql, conn)
        conn.close()
        
        return {
            'columns': list(df.columns),
            'data': df.head(20).to_dict('records'),
            'total_rows': len(df)
        }
    except Exception as e:
        return {'error': str(e)}

# ============================================================
# HELPER FUNCTION — Load Vector Store
# ============================================================

def load_vector_store():
    """Load our ChromaDB vector store for RAG searches."""
    
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    vector_store = Chroma(
        persist_directory='rag/chroma_db',
        embedding_function=embeddings
    )
    
    return vector_store

# ============================================================
# TOOL 1 — Revenue Summary
# ============================================================

@tool
def get_revenue_summary(period: str = "all_time") -> str:
    """
    Get revenue and payment statistics.
    Use this when user asks about revenue, income, 
    payments, money, or financial performance.
    Period options: all_time, last_30_days, last_90_days
    """
    
    if period == "last_30_days":
        date_filter = "WHERE date >= date('now', '-30 days')"
    elif period == "last_90_days":
        date_filter = "WHERE date >= date('now', '-90 days')"
    else:
        date_filter = ""
    
    sql = f"""
        SELECT 
            COUNT(*) as total_payments,
            SUM(amount) as total_revenue,
            ROUND(AVG(amount), 2) as avg_payment,
            SUM(CASE WHEN status='failed' 
                THEN 1 ELSE 0 END) as failed_payments,
            SUM(CASE WHEN status='success' 
                THEN amount ELSE 0 END) as successful_revenue
        FROM payments
        {date_filter}
    """
    
    result = query_database(sql)
    
    if 'error' in result:
        return f"Error getting revenue: {result['error']}"
    
    data = result['data'][0]
    
    return f"""
    💰 REVENUE SUMMARY ({period}):
    ─────────────────────────────
    Total Revenue:      ${data['total_revenue']:,.2f}
    Successful Revenue: ${data['successful_revenue']:,.2f}
    Total Payments:     {data['total_payments']}
    Failed Payments:    {data['failed_payments']}
    Average Payment:    ${data['avg_payment']:,.2f}
    Payment Success Rate: {((data['total_payments'] - data['failed_payments']) / data['total_payments'] * 100):.1f}%
    """

# ============================================================
# TOOL 2 — Member Statistics
# ============================================================

@tool
def get_member_stats(filter_by: str = "all") -> str:
    """
    Get member counts and statistics.
    Use this when user asks about members, customers,
    subscriptions, signups, or membership numbers.
    filter_by options: all, active, churned, basic, 
    standard, premium
    """
    
    if filter_by == "active":
        where = "WHERE churn_date IS NULL"
    elif filter_by == "churned":
        where = "WHERE churn_date IS NOT NULL"
    elif filter_by in ["basic", "standard", "premium"]:
        where = f"WHERE tier = '{filter_by}'"
    else:
        where = ""
    
    sql = f"""
        SELECT 
            COUNT(*) as total_members,
            SUM(CASE WHEN churn_date IS NULL 
                THEN 1 ELSE 0 END) as active_members,
            SUM(CASE WHEN churn_date IS NOT NULL 
                THEN 1 ELSE 0 END) as churned_members,
            SUM(CASE WHEN tier='basic' 
                THEN 1 ELSE 0 END) as basic_members,
            SUM(CASE WHEN tier='standard' 
                THEN 1 ELSE 0 END) as standard_members,
            SUM(CASE WHEN tier='premium' 
                THEN 1 ELSE 0 END) as premium_members,
            ROUND(AVG(age), 1) as average_age
        FROM members
        {where}
    """
    
    result = query_database(sql)
    
    if 'error' in result:
        return f"Error getting members: {result['error']}"
    
    data = result['data'][0]
    churn_rate = (data['churned_members'] / 
                  data['total_members'] * 100)
    
    return f"""
    👥 MEMBER STATISTICS ({filter_by}):
    ─────────────────────────────────
    Total Members:    {data['total_members']}
    Active Members:   {data['active_members']}
    Churned Members:  {data['churned_members']}
    Churn Rate:       {churn_rate:.1f}%
    
    📊 By Tier:
    Basic:     {data['basic_members']} members
    Standard:  {data['standard_members']} members
    Premium:   {data['premium_members']} members
    
    Average Age: {data['average_age']} years
    """

# ============================================================
# TOOL 3 — At Risk Members
# ============================================================

@tool
def get_at_risk_members(limit: int = 10) -> str:
    """
    Find members who are at risk of cancelling 
    their membership.
    Use this when user asks about churn risk, 
    at-risk members, who might leave, or 
    retention concerns.
    """
    
    sql = f"""
        SELECT 
            m.member_id,
            m.name,
            m.email,
            m.tier,
            COUNT(CASE WHEN p.status='failed' 
                THEN 1 END) as failed_payments,
            COUNT(b.booking_id) as total_bookings
        FROM members m
        LEFT JOIN payments p 
            ON m.member_id = p.member_id
        LEFT JOIN bookings b 
            ON m.member_id = b.member_id
        WHERE m.churn_date IS NULL
        GROUP BY m.member_id
        HAVING failed_payments > 0
        ORDER BY failed_payments DESC
        LIMIT {limit}
    """
    
    result = query_database(sql)
    
    if 'error' in result:
        return f"Error: {result['error']}"
    
    if not result['data']:
        return "✅ No at-risk members found!"
    
    response = f"""
    ⚠️  AT-RISK MEMBERS (Top {limit}):
    ─────────────────────────────────
    """
    
    for i, member in enumerate(result['data'], 1):
        response += f"""
    {i}. {member['name']} ({member['tier']} tier)
       Email:           {member['email']}
       Failed Payments: {member['failed_payments']}
       Total Bookings:  {member['total_bookings']}
    """
    
    response += f"\n    Total at-risk members found: {result['total_rows']}"
    return response

# ============================================================
# TOOL 4 — Draft Retention Email
# ============================================================

@tool
def draft_retention_email(
    email_type: str = "re_engagement"
) -> str:
    """
    Draft a professional email for member retention.
    Use this when user asks to write, draft, or 
    create an email for members.
    email_type options: re_engagement, payment_failed,
    welcome_back, promotion, class_reminder
    """
    
    # Email templates for different situations
    templates = {
        "re_engagement": {
            "subject": "We miss you at Nexify! 💪",
            "body": """
Dear [Member Name],

We noticed you haven't visited us recently, and we wanted 
to reach out personally.

Your fitness journey matters to us, and we're here to 
support you every step of the way.

As a valued member, we'd love to offer you:
✨ One FREE personal training session
✨ Access to our new premium classes this week
✨ A dedicated fitness consultant to help you 
   restart your routine

Simply reply to this email or call us to book your 
free session.

We believe in you and we're excited to see you back!

Warm regards,
The Nexify Team
            """
        },
        "payment_failed": {
            "subject": "Action needed: Payment update required",
            "body": """
Dear [Member Name],

We noticed your recent payment was unsuccessful, and we 
wanted to reach out to help resolve this quickly.

Your membership is important to us, and we don't want 
you to lose access to your fitness routine.

Please update your payment method by clicking below:
→ [Update Payment Details]

If you're experiencing financial difficulties, please 
contact us — we have flexible options available.

Your account will remain active for the next 7 days 
while you update your details.

Thank you for being a valued Nexify member.

Best regards,
The Nexify Team
            """
        },
        "welcome_back": {
            "subject": "Welcome back to Nexify! 🎉",
            "body": """
Dear [Member Name],

We are absolutely thrilled to welcome you back to 
the Nexify family!

To help you get back into your groove, we've prepared:
🎯 A personalized fitness plan based on your history
🏋️ Priority booking for your favourite classes
💪 A free fitness assessment with our top trainer

Your journey starts fresh today — and we're with you 
every step of the way.

See you at the gym!

With excitement,
The Nexify Team
            """
        },
        "promotion": {
            "subject": "Exclusive offer just for you! 🌟",
            "body": """
Dear [Member Name],

As one of our most valued members, we have an 
exclusive offer just for you!

For this week only:
⭐ Upgrade to Premium for 50% off first month
⭐ Bring a friend FREE for 30 days
⭐ Access to all specialist classes included

This offer expires in 48 hours — don't miss out!

→ [Claim Your Offer Now]

Thank you for being part of the Nexify community.

Best regards,
The Nexify Team
            """
        },
        "class_reminder": {
            "subject": "Your class is tomorrow — are you ready? 💪",
            "body": """
Dear [Member Name],

Just a friendly reminder that you have a class 
booked for tomorrow!

📅 Class Details:
   Class:      [Class Name]
   Instructor: [Instructor Name]
   Time:       [Class Time]
   Location:   Main Studio

Tips for tomorrow:
✅ Arrive 10 minutes early
✅ Bring water and a towel
✅ Wear comfortable workout clothes

Can't make it? Please cancel at least 2 hours before 
so another member can take your spot.

See you there!

The Nexify Team
            """
        }
    }
    
    # Get the right template
    template = templates.get(
        email_type, 
        templates["re_engagement"]
    )
    
    return f"""
    📧 DRAFTED EMAIL ({email_type}):
    ─────────────────────────────────
    Subject: {template['subject']}
    
    {template['body']}
    
    💡 Tip: Replace [Member Name] and other 
    placeholders with actual member details 
    before sending!
    """

# ============================================================
# TOOL 5 — Search Knowledge Base
# ============================================================

@tool
def search_knowledge_base(query: str) -> str:
    """
    Search Nexify's business knowledge base for 
    definitions, benchmarks, policies and best practices.
    Use this when user asks about KPIs, definitions,
    benchmarks, industry standards, or best practices.
    """
    
    try:
        vector_store = load_vector_store()
        
        # Find top 3 most relevant chunks
        results = vector_store.similarity_search(
            query, k=3
        )
        
        if not results:
            return "No relevant information found."
        
        response = f"""
    📚 KNOWLEDGE BASE RESULTS for '{query}':
    ─────────────────────────────────────────
        """
        
        for i, doc in enumerate(results, 1):
            response += f"""
    Result {i} (from {doc.metadata['source']}):
    {doc.page_content[:300]}...
    ─────────────────────────────────────────
            """
        
        return response
        
    except Exception as e:
        return f"Error searching knowledge base: {str(e)}"

# ============================================================
# TEST ALL TOOLS
# ============================================================

if __name__ == "__main__":
    print("Testing all tools...\n")
    
    print("1. Testing Revenue Tool:")
    print(get_revenue_summary.invoke({"period": "all_time"}))
    
    print("\n2. Testing Member Stats Tool:")
    print(get_member_stats.invoke({"filter_by": "all"}))
    
    print("\n3. Testing At-Risk Members Tool:")
    print(get_at_risk_members.invoke({"limit": 3}))
    
    print("\n4. Testing Email Draft Tool:")
    print(draft_retention_email.invoke(
        {"email_type": "re_engagement"}
    ))
    
    print("\n5. Testing Knowledge Base Tool:")
    print(search_knowledge_base.invoke(
        {"query": "what is churn rate"}
    ))