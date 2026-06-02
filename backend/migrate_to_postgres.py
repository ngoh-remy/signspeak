"""
SignSpeak - SQLite → PostgreSQL Migration Script
=================================================
Run this ONCE to migrate your existing Railway SQLite data to Render's PostgreSQL.

Usage:
  1. Make sure signspeak.db is present in this (backend/) directory
  2. Set the RENDER_DATABASE_URL environment variable to your Render PostgreSQL URL
     (find it in Render dashboard → your database → "External Database URL")
  3. Run:  python migrate_to_postgres.py

What it does:
  - Reads all users from SQLite
  - Reads all translation_history records from SQLite
  - Inserts them all into PostgreSQL (preserving IDs, timestamps, passwords)
  - Skips records that already exist (safe to re-run)
"""

import os
import sys
from datetime import datetime

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# ─── Config ──────────────────────────────────────────────────────────────────

SQLITE_URL = "sqlite:///./signspeak.db"

# Get from: Render Dashboard → signspeak-db → "External Database URL"
POSTGRES_URL = os.environ.get("RENDER_DATABASE_URL")

if not POSTGRES_URL:
    print("❌ ERROR: Set the RENDER_DATABASE_URL environment variable first.")
    print()
    print("   Example (PowerShell):")
    print('   $env:RENDER_DATABASE_URL = "postgresql://user:pass@host/dbname"')
    print()
    print("   Find it in: Render Dashboard → signspeak-db → External Database URL")
    sys.exit(1)

# Render gives a postgres:// URL but SQLAlchemy needs postgresql://
POSTGRES_URL = POSTGRES_URL.replace("postgres://", "postgresql://", 1)

# ─── Connect to both databases ────────────────────────────────────────────────

print("🔌 Connecting to SQLite...")
sqlite_engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
SQLiteSession = sessionmaker(bind=sqlite_engine)

print("🔌 Connecting to PostgreSQL (Render)...")
pg_engine = create_engine(POSTGRES_URL)
PGSession = sessionmaker(bind=pg_engine)

# ─── Create tables in PostgreSQL ─────────────────────────────────────────────

print("📦 Creating tables in PostgreSQL if they don't exist...")
# Import models so SQLAlchemy knows about them
sys.path.insert(0, os.path.dirname(__file__))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from database import Base
from models.models import User, TranslationHistory  # noqa

# Override engine temporarily so create_all targets PostgreSQL
Base.metadata.create_all(bind=pg_engine)
print("   ✅ Tables ready.")

# ─── Migrate Users ────────────────────────────────────────────────────────────

sqlite_db = SQLiteSession()
pg_db = PGSession()

try:
    users = sqlite_db.query(User).all()
    print(f"\n👤 Found {len(users)} user(s) in SQLite. Migrating...")

    migrated_users = 0
    skipped_users = 0

    for user in users:
        # Check if user already exists in PostgreSQL (safe re-run)
        existing = pg_db.query(User).filter(User.id == user.id).first()
        if existing:
            skipped_users += 1
            continue

        new_user = User(
            id=user.id,
            username=user.username,
            email=user.email,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
            created_at=user.created_at,
        )
        pg_db.add(new_user)
        migrated_users += 1

    pg_db.flush()

    # Reset the PostgreSQL sequence so new users get correct IDs
    if migrated_users > 0:
        max_id = max(u.id for u in users)
        pg_db.execute(text(f"SELECT setval('users_id_seq', {max_id})"))

    print(f"   ✅ Migrated: {migrated_users}  |  Skipped (already exist): {skipped_users}")

    # ─── Migrate Translation History ─────────────────────────────────────────

    histories = sqlite_db.query(TranslationHistory).all()
    print(f"\n📜 Found {len(histories)} translation record(s) in SQLite. Migrating...")

    migrated_hist = 0
    skipped_hist = 0

    for h in histories:
        existing = pg_db.query(TranslationHistory).filter(TranslationHistory.id == h.id).first()
        if existing:
            skipped_hist += 1
            continue

        new_h = TranslationHistory(
            id=h.id,
            user_id=h.user_id,
            sign_label=h.sign_label,
            confidence=h.confidence,
            session_id=h.session_id,
            created_at=h.created_at,
        )
        pg_db.add(new_h)
        migrated_hist += 1

    pg_db.flush()

    if migrated_hist > 0:
        max_hist_id = max(h.id for h in histories)
        pg_db.execute(text(f"SELECT setval('translation_history_id_seq', {max_hist_id})"))

    print(f"   ✅ Migrated: {migrated_hist}  |  Skipped (already exist): {skipped_hist}")

    # ─── Commit all ──────────────────────────────────────────────────────────

    pg_db.commit()
    print("\n🎉 Migration complete! All data is now in Render PostgreSQL.")
    print("   You can now safely delete your Railway backend service.")

except Exception as e:
    pg_db.rollback()
    print(f"\n❌ Migration failed: {e}")
    raise
finally:
    sqlite_db.close()
    pg_db.close()
