from sqlalchemy.orm import Session
from app.models.models import User


def get_user_by_telegram_id(
    db: Session,
    telegram_id: int
):
    return db.query(User).filter(
        User.telegram_id == telegram_id
    ).first()


def create_user(db: Session, user_data):
    user = User(
        telegram_id=user_data.telegram_id,
        name=user_data.name,
        username=user_data.username,
        band_level=user_data.band_level
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_or_create_user(db: Session, user_data):
    user = get_user_by_telegram_id(
        db, user_data.telegram_id
    )
    if user:
        return user, False
    user = create_user(db, user_data)
    return user, True


def get_user_stats(db: Session, telegram_id: int):
    user = get_user_by_telegram_id(db, telegram_id)
    if not user:
        return {}
    return {
        "name": user.name,
        "xp_points": user.xp_points,
        "streak_days": user.streak_days,
        "band_level": user.band_level,
        "subscription_type": user.subscription_type,
    }