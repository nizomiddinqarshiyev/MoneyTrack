import time
import pytest
import fakeredis
from antifraud.app.services.velocity import VelocityCheckService

@pytest.fixture
def velocity_service():
    service = VelocityCheckService()
    # Mock redis with fakeredis
    service.redis_client = fakeredis.FakeStrictRedis(decode_responses=True)
    return service

def test_velocity_count_1m(velocity_service):
    # Mock transaction
    tx = TransactionCreate(
        transaction_id="tx1", user_id="user_1", sender_card="c1", receiver_card="r1",
        amount=100, currency="UZS", timestamp=datetime.now(),
        sender_country="UZ", receiver_country="UZ", ip_address="1.1.1.1",
        device_id="d1", channel="WEB"
    )
    # Add 6 transactions
    for i in range(6):
        tx.transaction_id = f"tx_{i}"
        velocity_service.add_transaction(tx)
    
    count = velocity_service.get_count("user", "user_1", 60)
    assert count == 6

def test_velocity_total_amount(velocity_service):
    tx = TransactionCreate(
        transaction_id="tx_a", user_id="user_2", sender_card="c1", receiver_card="r1",
        amount=1000.0, currency="UZS", timestamp=datetime.now(),
        sender_country="UZ", receiver_country="UZ", ip_address="1.1.1.1",
        device_id="d1", channel="WEB"
    )
    velocity_service.add_transaction(tx)
    
    tx.transaction_id = "tx_b"
    tx.amount = 2000.0
    velocity_service.add_transaction(tx)
    
    total = velocity_service.get_total_amount("user", "user_2", 1800)
    assert total == 3000.0

def test_unique_cards_and_receivers(velocity_service):
    tx = TransactionCreate(
        transaction_id="tx_c1", user_id="u3", sender_card="card1", receiver_card="rec1",
        amount=100, currency="UZS", timestamp=datetime.now(),
        sender_country="UZ", receiver_country="UZ", ip_address="1.1.1.1",
        device_id="dev1", channel="WEB"
    )
    velocity_service.add_transaction(tx)
    
    # Same device, different card
    tx.transaction_id = "tx_c2"
    tx.sender_card = "card2"
    velocity_service.add_transaction(tx)
    
    assert velocity_service.get_unique_cards_on_device("dev1") == 2
    
    # Same card, different receiver
    tx.transaction_id = "tx_c3"
    tx.sender_card = "card1"
    tx.receiver_card = "rec2"
    velocity_service.add_transaction(tx)
    
    assert velocity_service.get_unique_receivers_for_card("card1") == 2
