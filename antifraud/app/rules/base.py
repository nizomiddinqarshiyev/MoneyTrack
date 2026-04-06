from abc import ABC, abstractmethod
from typing import List, Dict, Any
from antifraud.app.schemas.schemas import TransactionCreate

class RuleResult:
    def __init__(self, name: str, score_impact: float, severity: str, description: str):
        self.name = name
        self.score_impact = score_impact
        self.severity = severity
        self.description = description

class AntiFraudRule(ABC):
    @abstractmethod
    async def evaluate(self, transaction: TransactionCreate, context: Dict[str, Any]) -> List[RuleResult]:
        pass

class VelocityRule(AntiFraudRule):
    async def evaluate(self, transaction: TransactionCreate, context: Dict[str, Any]) -> List[RuleResult]:
        results = []
        v_service = context.get("velocity_service")
        if not v_service:
            return results

        # > 5 transactions in 1 minute
        count_1m = v_service.get_count("user", transaction.user_id, 60)
        if count_1m > 5:
            results.append(RuleResult("HighFrequency1m", 25, "HIGH", f"User had {count_1m} transactions in 1 minute"))

        # Amount threshold (example: > 10,000,000 in 30 mins)
        total_30m = v_service.get_total_amount("user", transaction.user_id, 1800)
        if total_30m > 10000000:
            results.append(RuleResult("HighVolume30m", 25, "MEDIUM", f"Total transferred {total_30m} in 30 minutes"))
        
        # Multiple cards on same device
        unique_cards = v_service.get_unique_cards_on_device(transaction.device_id)
        if unique_cards >= 3:
            results.append(RuleResult("MultipleCardsOnDevice", 30, "HIGH", f"Device used with {unique_cards} unique cards"))

        # Same card sending to multiple receivers
        unique_receivers = v_service.get_unique_receivers_for_card(transaction.sender_card)
        if unique_receivers > 5:
            results.append(RuleResult("MultipleReceiversForCard", 25, "MEDIUM", f"Card sending to {unique_receivers} unique receivers"))

        # Failed attempts count
        failed_count = v_service.get_failed_attempts(transaction.user_id)
        if failed_count >= 3:
            results.append(RuleResult("HighFailedAttempts", 20, "MEDIUM", f"User has {failed_count} failed attempts today"))

        return results

class GeoRule(AntiFraudRule):
    async def evaluate(self, transaction: TransactionCreate, context: Dict[str, Any]) -> List[RuleResult]:
        results = []
        geo_service = context.get("geo_service")
        if not geo_service:
            return results

        # Trusted corridor logic
        is_trusted = geo_service.is_trusted_corridor(transaction.sender_country, transaction.receiver_country)
        if is_trusted:
            results.append(RuleResult("TrustedCorridor", -10, "LOW", "Transaction within trusted corridor"))

        prev_tx = context.get("prev_transaction")
        if prev_tx and prev_tx.sender_country != transaction.sender_country:
            time_diff_hours = (transaction.timestamp - prev_tx.timestamp).total_seconds() / 3600.0
            
            # country changed within 1 hour → high risk
            if time_diff_hours < 1:
                results.append(RuleResult("GeoAnomaly", 30, "HIGH", "Country changed within 1 hour"))
            
            # country changed + inactivity > 7 days → low risk
            elif time_diff_hours > 168: # 7 days
                results.append(RuleResult("InactivityReturn", 10, "LOW", "Country change after >7 days inactivity"))

            # impossible travel speed > 900 km/h → fraud alert
            # In real system, we'd need lat/lon from IP or country database
            # Here we simulate with a placeholder speed calculation logic
            if hasattr(transaction, 'ip_address') and hasattr(prev_tx, 'ip_address'):
                # Simplified speed check for demo
                if time_diff_hours < 5: # If very fast change for significant distance
                     results.append(RuleResult("ImpossibleTravel", 50, "CRITICAL", "Potential impossible travel detected"))

        return results

class DeviceRule(AntiFraudRule):
    async def evaluate(self, transaction: TransactionCreate, context: Dict[str, Any]) -> List[RuleResult]:
        results = []
        device_service = context.get("device_service")
        if not device_service:
            return results

        dev_info = device_service.check_device(transaction.user_id, transaction.device_id)
        
        if dev_info["is_new_device"]:
            results.append(RuleResult("NewDevice", 20, "LOW", "Transaction from a new device"))
        
        if dev_info["multiple_users"]:
            results.append(RuleResult("SharedDevice", 15, "MEDIUM", f"Device shared with {dev_info['other_users_count']} other users"))

        return results
