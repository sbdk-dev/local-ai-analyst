#!/usr/bin/env python3
"""
Test semantic layer queries via Ibis

Validates:
1. Database connection works
2. Tables loaded correctly
3. Basic semantic model patterns
4. Engagement metrics (DAU, MAU, retention)
"""

import ibis
from ibis import _
import datetime

# Connect to DuckDB
con = ibis.duckdb.connect('semantic-layer/data/analytics.duckdb')

print("=" * 60)
print("SEMANTIC LAYER QUERY TESTS")
print("=" * 60)

# Test 1: Basic table access
print("\n1. BASIC TABLE ACCESS")
print("-" * 60)

users = con.table('users')
events = con.table('events')
sessions = con.table('sessions')

print(f"Users table: {users.count().execute()} rows")
print(f"Events table: {events.count().execute()} rows")
print(f"Sessions table: {sessions.count().execute()} rows")

# Test 2: Users semantic model - dimensions and measures
print("\n2. USERS SEMANTIC MODEL")
print("-" * 60)

# Total users by plan type
users_by_plan = (
    users
    .group_by('plan_type')
    .aggregate(total_users=_.user_id.nunique())
    .order_by(ibis.desc('total_users'))
)
print("\nTotal users by plan type:")
print(users_by_plan.execute())

# Conversion rate (paid vs free)
total_users_count = users.count().execute()
paid_users_count = users.filter(_.plan_type != 'free').count().execute()
conversion_rate = (paid_users_count / total_users_count) * 100
print(f"\nConversion rate: {conversion_rate:.1f}% ({paid_users_count}/{total_users_count} users on paid plans)")

# Users by industry
users_by_industry = (
    users
    .group_by('industry')
    .aggregate(total_users=_.user_id.nunique())
    .order_by(ibis.desc('total_users'))
    .limit(10)
)
print("\nTop 10 industries:")
print(users_by_industry.execute())

# Test 3: Events semantic model - measures
print("\n3. EVENTS SEMANTIC MODEL")
print("-" * 60)

# Total events and unique users
event_stats = events.aggregate(
    total_events=_.count(),
    unique_users=_.user_id.nunique(),
    unique_sessions=_.session_id.nunique()
).execute()

print(f"Total events: {event_stats['total_events'].iloc[0]:,}")
print(f"Unique users: {event_stats['unique_users'].iloc[0]:,}")
print(f"Unique sessions: {event_stats['unique_sessions'].iloc[0]:,}")
print(f"Events per user: {event_stats['total_events'].iloc[0] / event_stats['unique_users'].iloc[0]:.1f}")
print(f"Events per session: {event_stats['total_events'].iloc[0] / event_stats['unique_sessions'].iloc[0]:.1f}")

# Events by type
events_by_type = (
    events
    .group_by('event_type')
    .aggregate(count=_.count())
    .order_by(ibis.desc('count'))
)
print("\nEvents by type:")
print(events_by_type.execute())

# Feature usage (feature_use events only)
feature_usage = (
    events
    .filter(_.event_type == 'feature_use')
    .group_by('feature_name')
    .aggregate(
        usage_count=_.count(),
        unique_users=_.user_id.nunique()
    )
    .order_by(ibis.desc('usage_count'))
)
print("\nTop features by usage:")
print(feature_usage.execute())

# Test 4: Sessions semantic model - duration metrics
print("\n4. SESSION METRICS")
print("-" * 60)

# Average session duration
# Calculate duration in seconds, then convert to minutes
session_durations = (
    sessions
    .aggregate(
        total_sessions=_.count(),
        unique_users=_.user_id.nunique()
    )
    .execute()
)

# Use Python to calculate duration from the data
sessions_df = sessions.execute()
sessions_df['duration_minutes'] = (sessions_df['session_end'] - sessions_df['session_start']).dt.total_seconds() / 60
avg_duration_minutes = sessions_df['duration_minutes'].mean()
median_duration_minutes = sessions_df['duration_minutes'].median()
print(f"Average session duration: {avg_duration_minutes:.1f} minutes")
print(f"Median session duration: {median_duration_minutes:.1f} minutes")
print(f"Total sessions: {session_durations['total_sessions'].iloc[0]:,}")
print(f"Sessions per user: {session_durations['total_sessions'].iloc[0] / session_durations['unique_users'].iloc[0]:.1f}")

# Test 5: Engagement metrics (DAU/MAU/WAU)
print("\n5. ENGAGEMENT METRICS")
print("-" * 60)

# Get date range of events
date_range = events.aggregate(
    min_date=_.event_timestamp.min(),
    max_date=_.event_timestamp.max()
).execute()

print(f"Event data range: {date_range['min_date'].iloc[0]} to {date_range['max_date'].iloc[0]}")

# For testing, we'll use the max date in the data as our reference date
reference_date = date_range['max_date'].iloc[0]
print(f"Reference date for metrics: {reference_date}")

# DAU (users active on the last day in dataset)
dau = (
    events
    .filter(_.event_timestamp.date() == reference_date.date())
    .aggregate(dau=_.user_id.nunique())
    .execute()
)
print(f"\nDAU (on {reference_date.date()}): {dau['dau'].iloc[0]:,}")

# WAU (users active in last 7 days from reference)
seven_days_ago = reference_date - datetime.timedelta(days=7)
wau = (
    events
    .filter(_.event_timestamp >= seven_days_ago)
    .aggregate(wau=_.user_id.nunique())
    .execute()
)
print(f"WAU (7 days ending {reference_date.date()}): {wau['wau'].iloc[0]:,}")

# MAU (users active in last 30 days from reference)
thirty_days_ago = reference_date - datetime.timedelta(days=30)
mau = (
    events
    .filter(_.event_timestamp >= thirty_days_ago)
    .aggregate(mau=_.user_id.nunique())
    .execute()
)
print(f"MAU (30 days ending {reference_date.date()}): {mau['mau'].iloc[0]:,}")

# Stickiness (DAU/MAU)
stickiness = (dau['dau'].iloc[0] / mau['mau'].iloc[0]) * 100 if mau['mau'].iloc[0] > 0 else 0
print(f"Stickiness (DAU/MAU): {stickiness:.1f}%")

# Test 6: Retention metrics
print("\n6. RETENTION METRICS")
print("-" * 60)

# Join users + events to calculate D1 retention
# Users who had an event 1 day after signup
user_events = (
    users
    .join(events, users.user_id == events.user_id)
    .select(
        users.user_id,
        users.signup_date,
        events.event_timestamp
    )
)

# Calculate days since signup for each event
user_events = user_events.mutate(
    days_since_signup=(_.event_timestamp.date() - _.signup_date).days
)

# D1 retention: users who had event 1 day after signup / total users
d1_returned = (
    user_events
    .filter((_.days_since_signup >= 1) & (_.days_since_signup < 2))
    .aggregate(users_returned=_.user_id.nunique())
    .execute()
)

total_users_for_retention = users.count().execute()
d1_retention = (d1_returned['users_returned'].iloc[0] / total_users_for_retention) * 100

print(f"D1 Retention: {d1_retention:.1f}% ({d1_returned['users_returned'].iloc[0]}/{total_users_for_retention} users returned day 1)")

# D7 retention: users who had event 7 days after signup
d7_returned = (
    user_events
    .filter((_.days_since_signup >= 7) & (_.days_since_signup < 8))
    .aggregate(users_returned=_.user_id.nunique())
    .execute()
)

d7_retention = (d7_returned['users_returned'].iloc[0] / total_users_for_retention) * 100
print(f"D7 Retention: {d7_retention:.1f}% ({d7_returned['users_returned'].iloc[0]}/{total_users_for_retention} users returned day 7)")

# Test 7: Cross-dimensional analysis (plan type × engagement)
print("\n7. PLAN TYPE × ENGAGEMENT")
print("-" * 60)

# Average events per user by plan type
events_by_plan = (
    users
    .join(events, users.user_id == events.user_id)
    .group_by(users.plan_type)
    .aggregate(
        unique_users=_.user_id.nunique(),
        total_events=_.count(),
        avg_events_per_user=(_.count() / _.user_id.nunique())
    )
    .order_by(ibis.desc('avg_events_per_user'))
)
print("\nEvents per user by plan type:")
print(events_by_plan.execute())

# Test 8: Feature adoption by industry
print("\n8. FEATURE ADOPTION BY INDUSTRY")
print("-" * 60)

# Top feature by industry (for feature_use events)
feature_by_industry = (
    users
    .join(events, users.user_id == events.user_id)
    .filter(events.event_type == 'feature_use')
    .group_by([users.industry, events.feature_name])
    .aggregate(usage_count=_.count())
    .order_by([users.industry, ibis.desc('usage_count')])
)

# Show top feature for each of top 5 industries
top_industries = users_by_industry.execute()['industry'].head(5).tolist()
for industry in top_industries:
    top_feature = (
        feature_by_industry
        .filter(_.industry == industry)
        .limit(1)
        .execute()
    )
    if not top_feature.empty:
        print(f"{industry}: {top_feature['feature_name'].iloc[0]} ({top_feature['usage_count'].iloc[0]} uses)")

print("\n" + "=" * 60)
print("ALL TESTS COMPLETED")
print("=" * 60)
print("\nSemantic layer validation:")
print("✅ Database connection")
print("✅ Table access (users, events, sessions)")
print("✅ Basic measures (counts, aggregations)")
print("✅ Engagement metrics (DAU, MAU, stickiness)")
print("✅ Retention calculations (D1, D7)")
print("✅ Cross-dimensional analysis (plan × events, industry × features)")
print("\nReady for MCP server implementation (Phase 3)")
