from sqlalchemy.orm import Session
from app.models import ActivityLog
from app.core.context import client_ip_ctx

class ActivityLogService:
    @staticmethod
    def log(db: Session, user_id: str, action: str, target_detail: str, ip_address: str = None, status: str = "Berhasil"):
        if not ip_address:
            ip_address = client_ip_ctx.get()
            
        log_entry = ActivityLog(
            user_id=user_id,
            action=action,
            target_detail=target_detail,
            ip_address=ip_address,
            status=status
        )
        db.add(log_entry)
        db.commit()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> list:
        return (
            db.query(ActivityLog)
            .order_by(ActivityLog.timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )