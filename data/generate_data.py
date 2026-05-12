# ============================================================
# Nexify - Synthetic Data Generator
# This file creates realistic fake business data
# ============================================================

import pandas as pd          # for creating and saving data tables
import numpy as np           # for math and random numbers
import random                # for random choices
import os                    # for creating folders
from faker import Faker      # for generating fake names, emails etc
from datetime import datetime, timedelta  # for working with dates

# ---- Setup ----
fake = Faker()               # create a Faker object
np.random.seed(42)           # makes random numbers repeatable
random.seed(42)              # same result every time we run

# Create output folder if it doesn't exist
os.makedirs('data/raw', exist_ok=True)

print("Starting data generation...")

# ============================================================
# 1. GENERATE MEMBERS
# ============================================================

def generate_members(n=500):
    """
    Generate n fake members with realistic attributes.
    About 25% of members will have churned (cancelled).
    """
    
    # Membership tiers and their monthly prices
    tiers = ['basic', 'standard', 'premium']
    tier_weights = [0.5, 0.3, 0.2]  # 50% basic, 30% standard, 20% premium
    
    members = []  # empty list to store each member
    
    for i in range(n):
        
        # Random join date between Jan 2022 and Jan 2024
        join_date = datetime(2022, 1, 1) + timedelta(
            days=random.randint(0, 730)
        )
        
        # 25% chance this member churned (cancelled)
        has_churned = random.random() < 0.25
        
        # If churned, set a churn date after joining
        if has_churned:
            churn_date = join_date + timedelta(
                days=random.randint(60, 400)
            )
            # Make sure churn date isn't in the future
            if churn_date > datetime(2024, 6, 1):
                churn_date = datetime(2024, 6, 1)
        else:
            churn_date = None  # still active member
        
        # Pick a random tier
        tier = random.choices(tiers, weights=tier_weights)[0]
        
        # Create the member record
        member = {
            'member_id': f'M{i:04d}',          # M0001, M0002 etc
            'name': fake.name(),                 # realistic fake name
            'email': fake.email(),               # realistic fake email
            'phone': fake.phone_number(),        # fake phone number
            'tier': tier,                        # basic/standard/premium
            'join_date': join_date.date(),       # when they joined
            'churn_date': churn_date.date() if churn_date else None,
            'age': random.randint(18, 65),       # random age
            'city': fake.city(),                 # fake city
            'gender': random.choice(['M', 'F', 'Other']),
        }
        
        members.append(member)  # add to our list
    
    return pd.DataFrame(members)  # convert list to table


# ============================================================
# 2. GENERATE PAYMENTS
# ============================================================

def generate_payments(members_df):
    """
    Generate monthly payment records for each member.
    Each member pays every month from join to churn (or today).
    """
    
    # Monthly prices for each tier
    tier_prices = {
        'basic': 29,
        'standard': 59,
        'premium': 99
    }
    
    payments = []  # empty list to store payments
    
    for _, member in members_df.iterrows():
        # iterrows() goes through each member one by one
        
        # Payment period: from join date to churn date (or Jun 2024)
        start_date = pd.to_datetime(member['join_date'])
        
        if member['churn_date'] is not None:
            end_date = pd.to_datetime(member['churn_date'])
        else:
            end_date = datetime(2024, 6, 1)
        
        # Generate one payment per month
        current_date = start_date
        
        while current_date < end_date:
            
            # 3% chance of payment failure (realistic!)
            payment_failed = random.random() < 0.03
            
            # Add some realistic variation to amount
            base_price = tier_prices[member['tier']]
            
            payment = {
                'payment_id': fake.uuid4(),          # unique ID
                'member_id': member['member_id'],    # links to member
                'date': current_date.date(),         # payment date
                'amount': base_price,                # amount paid
                'status': 'failed' if payment_failed else 'success',
                'payment_method': random.choice([
                    'credit_card', 'debit_card', 'bank_transfer'
                ])
            }
            
            payments.append(payment)
            
            # Move to next month
            current_date += timedelta(days=30)
    
    return pd.DataFrame(payments)


# ============================================================
# 3. GENERATE CLASSES
# ============================================================

def generate_classes():
    """
    Generate a list of fitness classes offered.
    """
    
    class_list = [
        {'class_id': 'C001', 'class_name': 'Yoga', 
         'instructor': 'Sarah Johnson', 'capacity': 20, 
         'duration_mins': 60, 'day': 'Monday', 'time': '07:00'},
        
        {'class_id': 'C002', 'class_name': 'HIIT', 
         'instructor': 'Mike Peters', 'capacity': 15, 
         'duration_mins': 45, 'day': 'Monday', 'time': '18:00'},
        
        {'class_id': 'C003', 'class_name': 'Pilates', 
         'instructor': 'Emma Davis', 'capacity': 12, 
         'duration_mins': 50, 'day': 'Tuesday', 'time': '09:00'},
        
        {'class_id': 'C004', 'class_name': 'Spin', 
         'instructor': 'Tom Wilson', 'capacity': 18, 
         'duration_mins': 45, 'day': 'Wednesday', 'time': '07:00'},
        
        {'class_id': 'C005', 'class_name': 'Zumba', 
         'instructor': 'Maria Garcia', 'capacity': 25, 
         'duration_mins': 60, 'day': 'Wednesday', 'time': '18:00'},
        
        {'class_id': 'C006', 'class_name': 'Boxing', 
         'instructor': 'James Brown', 'capacity': 10, 
         'duration_mins': 60, 'day': 'Thursday', 'time': '07:00'},
        
        {'class_id': 'C007', 'class_name': 'Meditation', 
         'instructor': 'Lisa Chen', 'capacity': 20, 
         'duration_mins': 30, 'day': 'Friday', 'time': '08:00'},
        
        {'class_id': 'C008', 'class_name': 'CrossFit', 
         'instructor': 'Mike Peters', 'capacity': 12, 
         'duration_mins': 60, 'day': 'Saturday', 'time': '09:00'},
    ]
    
    return pd.DataFrame(class_list)


# ============================================================
# 4. GENERATE BOOKINGS
# ============================================================

def generate_bookings(members_df, classes_df):
    """
    Generate class booking records for members.
    Active members book 2-8 classes per month.
    """
    
    bookings = []
    class_ids = classes_df['class_id'].tolist()
    
    for _, member in members_df.iterrows():
        
        start_date = pd.to_datetime(member['join_date'])
        
        if member['churn_date'] is not None:
            end_date = pd.to_datetime(member['churn_date'])
        else:
            end_date = datetime(2024, 6, 1)
        
        # Generate bookings month by month
        current_date = start_date
        
        while current_date < end_date:
            
            # Members near churn book fewer classes
            months_to_churn = (end_date - current_date).days / 30
            
            if months_to_churn < 2:
                # At risk member — books fewer classes
                num_bookings = random.randint(0, 2)
            else:
                # Active member — books more classes
                num_bookings = random.randint(2, 8)
            
            for _ in range(num_bookings):
                
                booking_date = current_date + timedelta(
                    days=random.randint(0, 29)
                )
                
                # 80% attendance rate (realistic)
                attended = random.random() < 0.80
                
                booking = {
                    'booking_id': fake.uuid4(),
                    'member_id': member['member_id'],
                    'class_id': random.choice(class_ids),
                    'booking_date': booking_date.date(),
                    'status': 'attended' if attended else random.choice(
                        ['missed', 'cancelled']
                    )
                }
                
                bookings.append(booking)
            
            current_date += timedelta(days=30)
    
    return pd.DataFrame(bookings)


# ============================================================
# 5. RUN EVERYTHING AND SAVE
# ============================================================

print("Generating members...")
members_df = generate_members(500)
members_df.to_csv('data/raw/members.csv', index=False)
print(f"✅ Created {len(members_df)} members")

print("Generating payments...")
payments_df = generate_payments(members_df)
payments_df.to_csv('data/raw/payments.csv', index=False)
print(f"✅ Created {len(payments_df)} payments")

print("Generating classes...")
classes_df = generate_classes()
classes_df.to_csv('data/raw/classes.csv', index=False)
print(f"✅ Created {len(classes_df)} classes")

print("Generating bookings...")
bookings_df = generate_bookings(members_df, classes_df)
bookings_df.to_csv('data/raw/bookings.csv', index=False)
print(f"✅ Created {len(bookings_df)} bookings")

print("\n" + "="*50)
print("DATA GENERATION COMPLETE!")
print("="*50)
print(f"\nSummary:")
print(f"  Members:  {len(members_df)}")
print(f"  Payments: {len(payments_df)}")
print(f"  Classes:  {len(classes_df)}")
print(f"  Bookings: {len(bookings_df)}")
print(f"\nFiles saved to: data/raw/")