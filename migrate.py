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
    conn.commit()
    print('✅ Done!')