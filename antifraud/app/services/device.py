from datetime import datetime
from sqlalchemy.orm import Session
from antifraud.app.models.models import UserDevice

class DeviceRiskService:
    def __init__(self, db: Session):
        self.db = db

    def check_device(self, user_id: str, device_id: str) -> dict:
        """Checks device history and returns risk flags."""
        # Find if this device has been used by this user before
        user_device = self.db.query(UserDevice).filter(
            UserDevice.user_id == user_id,
            UserDevice.device_id == device_id
        ).first()

        is_new_device = False
        if not user_device:
            is_new_device = True
            # Log new device
            new_dev = UserDevice(user_id=user_id, device_id=device_id)
            self.db.add(new_dev)
            self.db.commit()
        else:
            user_device.last_seen = datetime.utcnow()
            self.db.commit()

        # Check if multiple users use this same device
        other_users_count = self.db.query(UserDevice).filter(
            UserDevice.device_id == device_id,
            UserDevice.user_id != user_id
        ).count()

        return {
            "is_new_device": is_new_device,
            "multiple_users": other_users_count > 0,
            "other_users_count": other_users_count
        }

    def get_user_devices(self, user_id: str) -> list:
        return self.db.query(UserDevice).filter(UserDevice.user_id == user_id).all()
