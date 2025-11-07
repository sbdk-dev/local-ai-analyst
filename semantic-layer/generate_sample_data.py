#!/usr/bin/env python3
"""
Generate realistic product analytics sample data

Creates:
- users.csv (1,000 users with demographics)
- events.csv (50,000 events with user actions)
- sessions.csv (10,000 sessions aggregated from events)

Following Rasmus's product analytics patterns.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from faker import Faker
import random

fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

# Configuration
NUM_USERS = 1000
NUM_EVENTS = 50000
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2024, 12, 31)

# Constants
PLAN_TYPES = ['free', 'starter', 'pro', 'enterprise']
PLAN_WEIGHTS = [0.60, 0.25, 0.12, 0.03]  # 60% free, 25% starter, 12% pro, 3% enterprise

INDUSTRIES = ['saas', 'ecommerce', 'fintech', 'healthtech', 'edtech', 'marketing', 'consulting']
INDUSTRY_WEIGHTS = [0.25, 0.20, 0.15, 0.10, 0.10, 0.12, 0.08]

COMPANY_SIZES = ['small', 'medium', 'large']
COMPANY_SIZE_WEIGHTS = [0.65, 0.25, 0.10]  # Skewed toward small

COUNTRIES = ['US', 'UK', 'CA', 'AU', 'DE', 'FR', 'SG', 'IN']
COUNTRY_WEIGHTS = [0.45, 0.15, 0.10, 0.08, 0.07, 0.06, 0.05, 0.04]

EVENT_TYPES = [
    'signup', 'login', 'feature_use', 'export', 'share',
    'invite', 'upgrade', 'settings_change', 'logout'
]

FEATURES = [
    'dashboard_view', 'report_create', 'report_export', 'chart_create',
    'data_upload', 'team_invite', 'integration_setup', 'api_call',
    'alert_create', 'collaboration_edit'
]

print("Generating product analytics sample data...")

# ============================================================================
# Generate Users
# ============================================================================

print(f"\n1. Generating {NUM_USERS} users...")

users = []
for i in range(NUM_USERS):
    user_id = f"user_{str(i+1).zfill(4)}"

    # Signup date (spread across 2024)
    days_offset = random.randint(0, (END_DATE - START_DATE).days)
    signup_date = START_DATE + timedelta(days=days_offset)

    # Demographics
    plan_type = random.choices(PLAN_TYPES, weights=PLAN_WEIGHTS)[0]
    industry = random.choices(INDUSTRIES, weights=INDUSTRY_WEIGHTS)[0]
    company_size = random.choices(COMPANY_SIZES, weights=COMPANY_SIZE_WEIGHTS)[0]
    country = random.choices(COUNTRIES, weights=COUNTRY_WEIGHTS)[0]

    users.append({
        'user_id': user_id,
        'signup_date': signup_date.strftime('%Y-%m-%d'),
        'plan_type': plan_type,
        'industry': industry,
        'company_size': company_size,
        'country': country
    })

users_df = pd.DataFrame(users)
print(f"   Created {len(users_df)} users")
print(f"   Plan distribution: {users_df['plan_type'].value_counts().to_dict()}")
print(f"   Industry distribution: {users_df['industry'].value_counts().to_dict()}")

# ============================================================================
# Generate Events
# ============================================================================

print(f"\n2. Generating {NUM_EVENTS} events...")

events = []
event_id_counter = 1
session_id_counter = 1

# For each user, generate events based on their plan type
for _, user in users_df.iterrows():
    user_id = user['user_id']
    signup_date = pd.to_datetime(user['signup_date'])
    plan_type = user['plan_type']

    # Number of events per user varies by plan
    # Enterprise users are more active
    if plan_type == 'free':
        num_user_events = random.randint(5, 30)
        session_duration_avg = 15  # minutes
    elif plan_type == 'starter':
        num_user_events = random.randint(20, 80)
        session_duration_avg = 25
    elif plan_type == 'pro':
        num_user_events = random.randint(50, 150)
        session_duration_avg = 35
    else:  # enterprise
        num_user_events = random.randint(100, 300)
        session_duration_avg = 45

    # Cap total events to stay within NUM_EVENTS budget
    if len(events) + num_user_events > NUM_EVENTS:
        num_user_events = NUM_EVENTS - len(events)

    if num_user_events <= 0:
        break

    # Generate sessions for this user
    num_sessions = max(1, num_user_events // random.randint(3, 8))

    for session_idx in range(num_sessions):
        session_id = f"sess_{str(session_id_counter).zfill(5)}"
        session_id_counter += 1

        # Session starts randomly after signup
        days_after_signup = random.randint(0, (END_DATE - signup_date).days)
        session_start = signup_date + timedelta(
            days=days_after_signup,
            hours=random.randint(8, 20),  # Business hours
            minutes=random.randint(0, 59)
        )

        # Session duration
        duration_minutes = int(np.random.exponential(session_duration_avg))
        duration_minutes = min(duration_minutes, 180)  # Max 3 hours

        # Events in this session
        events_in_session = random.randint(2, 8)
        events_in_session = min(events_in_session, num_user_events)

        for event_idx in range(events_in_session):
            event_id = f"evt_{str(event_id_counter).zfill(6)}"
            event_id_counter += 1

            # Event timestamp within session
            event_offset_minutes = int((event_idx / events_in_session) * duration_minutes)
            event_timestamp = session_start + timedelta(minutes=event_offset_minutes)

            # First event is usually login (unless signup)
            if session_idx == 0 and event_idx == 0:
                event_type = 'signup'
                feature_name = 'account_creation'
            elif event_idx == 0:
                event_type = 'login'
                feature_name = 'dashboard_view'
            else:
                event_type = 'feature_use'
                feature_name = random.choice(FEATURES)

            # Last event might be logout
            if event_idx == events_in_session - 1 and random.random() < 0.3:
                event_type = 'logout'
                feature_name = None

            events.append({
                'event_id': event_id,
                'user_id': user_id,
                'event_timestamp': event_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'event_type': event_type,
                'feature_name': feature_name if feature_name else '',
                'session_id': session_id
            })

            num_user_events -= 1
            if num_user_events <= 0:
                break

        if num_user_events <= 0:
            break

    if len(events) >= NUM_EVENTS:
        break

events_df = pd.DataFrame(events)
print(f"   Created {len(events_df)} events")
print(f"   Event type distribution: {events_df['event_type'].value_counts().to_dict()}")
print(f"   Unique users: {events_df['user_id'].nunique()}")
print(f"   Unique sessions: {events_df['session_id'].nunique()}")

# ============================================================================
# Generate Sessions (aggregated from events)
# ============================================================================

print(f"\n3. Generating sessions (aggregated from events)...")

sessions = []
for session_id in events_df['session_id'].unique():
    session_events = events_df[events_df['session_id'] == session_id]

    user_id = session_events['user_id'].iloc[0]
    session_start = pd.to_datetime(session_events['event_timestamp'].min())
    session_end = pd.to_datetime(session_events['event_timestamp'].max())
    session_date = session_start.date()
    event_count = len(session_events)

    sessions.append({
        'session_id': session_id,
        'user_id': user_id,
        'session_start': session_start.strftime('%Y-%m-%d %H:%M:%S'),
        'session_end': session_end.strftime('%Y-%m-%d %H:%M:%S'),
        'session_date': str(session_date),
        'event_count': event_count
    })

sessions_df = pd.DataFrame(sessions)
print(f"   Created {len(sessions_df)} sessions")
print(f"   Avg events per session: {sessions_df['event_count'].mean():.1f}")
print(f"   Avg sessions per user: {len(sessions_df) / events_df['user_id'].nunique():.1f}")

# ============================================================================
# Save to CSV
# ============================================================================

print(f"\n4. Saving to CSV files...")

users_df.to_csv('semantic-layer/data/users.csv', index=False)
print(f"   ✓ users.csv ({len(users_df)} rows)")

events_df.to_csv('semantic-layer/data/events.csv', index=False)
print(f"   ✓ events.csv ({len(events_df)} rows)")

sessions_df.to_csv('semantic-layer/data/sessions.csv', index=False)
print(f"   ✓ sessions.csv ({len(sessions_df)} rows)")

# ============================================================================
# Summary Statistics
# ============================================================================

print(f"\n5. Summary Statistics:")
print(f"\n   Users:")
print(f"   - Total users: {len(users_df)}")
print(f"   - Date range: {users_df['signup_date'].min()} to {users_df['signup_date'].max()}")
print(f"   - Plan types: {dict(users_df['plan_type'].value_counts())}")
print(f"   - Industries: {dict(users_df['industry'].value_counts())}")

print(f"\n   Events:")
print(f"   - Total events: {len(events_df)}")
print(f"   - Date range: {events_df['event_timestamp'].min()} to {events_df['event_timestamp'].max()}")
print(f"   - Unique users with events: {events_df['user_id'].nunique()}")
print(f"   - Avg events per user: {len(events_df) / events_df['user_id'].nunique():.1f}")

print(f"\n   Sessions:")
print(f"   - Total sessions: {len(sessions_df)}")
print(f"   - Avg events per session: {sessions_df['event_count'].mean():.1f}")
print(f"   - Avg sessions per user: {len(sessions_df) / sessions_df['user_id'].nunique():.1f}")

print(f"\n✅ Sample data generation complete!")
print(f"\nNext steps:")
print(f"1. Load data to DuckDB: uv run python load_to_duckdb.py")
print(f"2. Define semantic models in models/")
print(f"3. Test queries via Ibis")
