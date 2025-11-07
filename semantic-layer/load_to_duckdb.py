#!/usr/bin/env python3
"""
Load product analytics data to DuckDB

Creates analytics.duckdb with 3 tables:
- users
- events
- sessions
"""

import duckdb
import pandas as pd
from pathlib import Path

print("Loading product analytics data to DuckDB...")

# Create database connection
db_path = Path('semantic-layer/data/analytics.duckdb')
print(f"\nCreating database: {db_path}")

con = duckdb.connect(str(db_path))

# ============================================================================
# Load Users Table
# ============================================================================

print("\n1. Loading users table...")
users_df = pd.read_csv('semantic-layer/data/users.csv')

con.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id VARCHAR PRIMARY KEY,
        signup_date DATE,
        plan_type VARCHAR,
        industry VARCHAR,
        company_size VARCHAR,
        country VARCHAR
    )
""")

con.execute("DELETE FROM users")  # Clear if exists
con.execute("INSERT INTO users SELECT * FROM users_df")

print(f"   ✓ Loaded {len(users_df)} users")
print(f"   ✓ Columns: {list(users_df.columns)}")

# ============================================================================
# Load Events Table
# ============================================================================

print("\n2. Loading events table...")
events_df = pd.read_csv('semantic-layer/data/events.csv')

con.execute("""
    CREATE TABLE IF NOT EXISTS events (
        event_id VARCHAR PRIMARY KEY,
        user_id VARCHAR,
        event_timestamp TIMESTAMP,
        event_type VARCHAR,
        feature_name VARCHAR,
        session_id VARCHAR,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
""")

con.execute("DELETE FROM events")
con.execute("INSERT INTO events SELECT * FROM events_df")

print(f"   ✓ Loaded {len(events_df)} events")
print(f"   ✓ Columns: {list(events_df.columns)}")

# ============================================================================
# Load Sessions Table
# ============================================================================

print("\n3. Loading sessions table...")
sessions_df = pd.read_csv('semantic-layer/data/sessions.csv')

con.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        session_id VARCHAR PRIMARY KEY,
        user_id VARCHAR,
        session_start TIMESTAMP,
        session_end TIMESTAMP,
        session_date DATE,
        event_count INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
""")

con.execute("DELETE FROM sessions")
con.execute("INSERT INTO sessions SELECT * FROM sessions_df")

print(f"   ✓ Loaded {len(sessions_df)} sessions")
print(f"   ✓ Columns: {list(sessions_df.columns)}")

# ============================================================================
# Create Indexes for Performance
# ============================================================================

print("\n4. Creating indexes...")

con.execute("CREATE INDEX IF NOT EXISTS idx_users_signup ON users(signup_date)")
con.execute("CREATE INDEX IF NOT EXISTS idx_users_plan ON users(plan_type)")
con.execute("CREATE INDEX IF NOT EXISTS idx_events_user ON events(user_id)")
con.execute("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(event_timestamp)")
con.execute("CREATE INDEX IF NOT EXISTS idx_events_session ON events(session_id)")
con.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id)")
con.execute("CREATE INDEX IF NOT EXISTS idx_sessions_date ON sessions(session_date)")

print("   ✓ Created indexes on key columns")

# ============================================================================
# Verify Data
# ============================================================================

print("\n5. Verifying data...")

# Count rows
users_count = con.execute("SELECT COUNT(*) FROM users").fetchone()[0]
events_count = con.execute("SELECT COUNT(*) FROM events").fetchone()[0]
sessions_count = con.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]

print(f"   ✓ users: {users_count} rows")
print(f"   ✓ events: {events_count} rows")
print(f"   ✓ sessions: {sessions_count} rows")

# Sample queries
print("\n6. Sample queries:")

print("\n   Plan type distribution:")
plan_dist = con.execute("SELECT plan_type, COUNT(*) as count FROM users GROUP BY plan_type ORDER BY count DESC").df()
print(plan_dist.to_string(index=False))

print("\n   Daily active users (last 7 days):")
dau = con.execute("""
    SELECT
        DATE(event_timestamp) as date,
        COUNT(DISTINCT user_id) as dau
    FROM events
    WHERE event_timestamp >= CURRENT_DATE - INTERVAL '7 days'
    GROUP BY DATE(event_timestamp)
    ORDER BY date DESC
    LIMIT 7
""").df()
print(dau.to_string(index=False))

print("\n   Top 5 features by usage:")
top_features = con.execute("""
    SELECT
        feature_name,
        COUNT(*) as usage_count,
        COUNT(DISTINCT user_id) as unique_users
    FROM events
    WHERE feature_name != ''
    GROUP BY feature_name
    ORDER BY usage_count DESC
    LIMIT 5
""").df()
print(top_features.to_string(index=False))

# ============================================================================
# Show Table Schemas
# ============================================================================

print("\n7. Table schemas:")

print("\n   Users:")
print(con.execute("DESCRIBE users").df().to_string(index=False))

print("\n   Events:")
print(con.execute("DESCRIBE events").df().to_string(index=False))

print("\n   Sessions:")
print(con.execute("DESCRIBE sessions").df().to_string(index=False))

con.close()

print(f"\n✅ Database created successfully: {db_path}")
print(f"\nDatabase size: {db_path.stat().st_size / 1024:.1f} KB")

print(f"\nNext steps:")
print(f"1. Define semantic models in semantic-layer/models/")
print(f"2. Test queries via Ibis: uv run python test_queries.py")
print(f"3. Create MCP server in semantic-layer/mcp_server/")
