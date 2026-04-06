from sqlalchemy.orm import Session
from antifraud.app.schemas.schemas import TransactionCreate
from antifraud.app.models.models import Transaction
from antifraud.app.services.velocity import VelocityCheckService
from antifraud.app.services.geo import GeoCheckService
from antifraud.app.services.device import DeviceRiskService
from antifraud.app.services.scoring import ScoringEngine
from antifraud.app.rules.base import VelocityRule, GeoRule, DeviceRule
import logging

logger = logging.getLogger("antifraud_orchestrator")

class AntifraudOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        self.v_service = VelocityCheckService()
        self.geo_service = GeoCheckService(db)
        self.device_service = DeviceRiskService(db)
        self.engine = ScoringEngine([VelocityRule(), GeoRule(), DeviceRule()])

    async def process_transaction(self, transaction: TransactionCreate) -> Transaction:
        # Check if exists
        db_tx = self.db.query(Transaction).filter(Transaction.transaction_id == transaction.transaction_id).first()
        if not db_tx:
            db_tx = Transaction(**transaction.model_dump(), status="PENDING")
            self.db.add(db_tx)
            self.db.commit()
            self.db.refresh(db_tx)

        # Context for rules
        prev_tx = self.db.query(Transaction).filter(
            Transaction.user_id == transaction.user_id,
            Transaction.transaction_id != transaction.transaction_id
        ).order_by(Transaction.timestamp.desc()).first()

        context = {
            "velocity_service": self.v_service,
            "geo_service": self.geo_service,
            "device_service": self.device_service,
            "prev_transaction": prev_tx
        }

        # Evaluate
        result = await self.engine.calculate_score(transaction, context)
        
        # Update state (Redis velocity and DB geo history)
        self.v_service.add_transaction(transaction)
        self.geo_service.update_country_history(transaction.user_id, transaction.sender_country)

        # Persist results
        self.engine.persist_results(self.db, transaction.transaction_id, transaction.user_id, result["score"], result["decision"], result["results"])
        
        # Track failed attempts if declined
        if result["decision"] == "DECLINED":
            self.v_service.track_failed_attempt(transaction.user_id)
        
        self.db.refresh(db_tx)
        logger.info(f"Transaction {transaction.transaction_id} processed: {result['decision']} (Score: {result['score']})")
        
        return db_tx
