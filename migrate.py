from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text(
        "ALTER TABLE user_vocabulary ADD COLUMN IF NOT EXISTS source VARCHAR(20) DEFAULT 'manual'"
    ))
    conn.execute(text(
        "ALTER TABLE essays ADD COLUMN IF NOT EXISTS is_premium BOOLEAN DEFAULT false"
    ))
    conn.execute(text(
        "ALTER TABLE essays ADD COLUMN IF NOT EXISTS ai_analysis JSON"
    ))
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS speaking_attempts (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            question_id INTEGER REFERENCES speaking_questions(id),
            part INTEGER DEFAULT 2,
            question_text TEXT NOT NULL,
            transcript TEXT NOT NULL,
            duration_sec INTEGER,
            ai_feedback JSON,
            ai_band FLOAT,
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        )
    """))
    # Web auth (email/parol) — telegram_id'siz, oddiy brauzerdan ro'yxatdan
    # o'tadigan foydalanuvchilar uchun.
    conn.execute(text(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS email VARCHAR(255) UNIQUE"
    ))
    conn.execute(text(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255)"
    ))
    conn.execute(text(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS auth_provider VARCHAR(20) DEFAULT 'telegram'"
    ))
    conn.commit()
    print('✅ Done!')
