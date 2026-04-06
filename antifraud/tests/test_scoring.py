import pytest
from antifraud.app.services.scoring import ScoringEngine
from antifraud.app.rules.base import RuleResult, AntiFraudRule
from antifraud.app.schemas.schemas import TransactionCreate
from datetime import datetime

class MockRule(AntiFraudRule):
    def __init__(self, impact, severity):
        self.impact = impact
        self.severity = severity

    async def evaluate(self, transaction, context):
        return [RuleResult("MockRule", self.impact, self.severity, "Mock description")]

@pytest.mark.asyncio
async def test_scoring_logic_approve():
    rules = [MockRule(10, "LOW"), MockRule(15, "MEDIUM")]
    engine = ScoringEngine(rules)
    
    # Mock transaction
    tx_data = {
        "transaction_id": "tx1", "user_id": "u1", "sender_card": "c1", "receiver_card": "c2",
        "amount": 100, "currency": "UZS", "timestamp": datetime.now(),
        "sender_country": "UZ", "receiver_country": "UZ", "ip_address": "1.1.1.1",
        "device_id": "d1", "channel": "WEB"
    }
    tx = TransactionCreate(**tx_data)
    
    result = await engine.calculate_score(tx, {})
    assert result["score"] == 25
    assert result["decision"] == "APPROVED"

@pytest.mark.asyncio
async def test_scoring_logic_decline():
    rules = [MockRule(40, "HIGH"), MockRule(25, "HIGH")]
    engine = ScoringEngine(rules)
    
    tx_data = {
        "transaction_id": "tx2", "user_id": "u1", "sender_card": "c1", "receiver_card": "c2",
        "amount": 100, "currency": "UZS", "timestamp": datetime.now(),
        "sender_country": "UZ", "receiver_country": "UZ", "ip_address": "1.1.1.1",
        "device_id": "d1", "channel": "WEB"
    }
    tx = TransactionCreate(**tx_data)
    
    result = await engine.calculate_score(tx, {})
    assert result["score"] == 65
    assert result["decision"] == "DECLINED"
