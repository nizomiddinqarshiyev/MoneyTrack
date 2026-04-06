import math
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from antifraud.app.models.models import CountryHistory

class GeoCheckService:
    TRUSTED_CORRIDORS = [
        ("UZ", "RU"), ("RU", "UZ"),
        ("UZ", "KZ"), ("KZ", "UZ")
    ]

    def __init__(self, db: Session):
        self.db = db

    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Haversine formula to calculate distance in km."""
        R = 6371.0  # Earth radius in km
        
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        
        a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c

    def is_trusted_corridor(self, sender_country: str, receiver_country: str) -> bool:
        return (sender_country, receiver_country) in self.TRUSTED_CORRIDORS

    def get_last_country(self, user_id: str) -> Optional[CountryHistory]:
        return self.db.query(CountryHistory).filter(CountryHistory.user_id == user_id).order_by(CountryHistory.last_seen.desc()).first()

    def update_country_history(self, user_id: str, country_code: str):
        history = self.db.query(CountryHistory).filter(
            CountryHistory.user_id == user_id, 
            CountryHistory.country_code == country_code
        ).first()
        
        if history:
            history.last_seen = datetime.utcnow()
        else:
            history = CountryHistory(user_id=user_id, country_code=country_code)
            self.db.add(history)
        
        self.db.commit()

    def check_impossible_travel(self, last_lat: float, last_lon: float, last_time: datetime, 
                                curr_lat: float, curr_lon: float, curr_time: datetime) -> bool:
        """Returns True if travel speed > 900 km/h."""
        distance = self.calculate_distance(last_lat, last_lon, curr_lat, curr_lon)
        time_diff = (curr_time - last_time).total_seconds() / 3600.0  # hours
        
        if time_diff <= 0:
            return False
            
        speed = distance / time_diff
        return speed > 900
