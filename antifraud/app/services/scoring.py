from typing import List, Dict, Any
from antifraud.app.rules.base import AntiFraudRule, RuleResult
from antifraud.app.schemas.schemas import TransactionCreate
from antifraud.app.models.models import FraudAlert, Transaction
from sqlalchemy.orm import Session

class ScoringEngine:
    def __init__(self, rules: List[AntiFraudRule]):
        self.rules = rules

    async def calculate_score(self, transaction: TransactionCreate, context: Dict[str, Any]) -> Dict[str, Any]:
        total_score = 0.0
        applied_results: List[RuleResult] = []

        for rule in self.rules:
            results = await rule.evaluate(transaction, context)
            for res in results:
                total_score += res.score_impact
                applied_results.append(res)

        # Decision logic
        # < 30 approve
        # 30–60 OTP required
        # > 60 decline
        decision = "APPROVED"
        if total_score > 60:
            decision = "DECLINED"
        elif total_score >= 30:
            decision = "OTP_REQUIRED"

        return {
            "score": total_score,
            "decision": decision,
            "results": applied_results
        }

    def persist_results(self, db: Session, transaction_id: str, user_id: str, score: float, decision: str, results: List[RuleResult]):
        # Update transaction status
        tx = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
        if tx:
            tx.status = decision
            tx.risk_score = score
        
        # Create fraud alerts for medium/high/critical impacts
        for res in results:
            if res.score_impact != 0:
                alert = FraudAlert(
                    transaction_id=transaction_id,
                    user_id=user_id,
                    rule_name=res.name,
                    severity=res.severity,
                    description=res.description
                )
                db.add(alert)
        
        db.commit()
