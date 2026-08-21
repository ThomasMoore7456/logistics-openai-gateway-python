from src.delivery_service import ProofOfDelivery, ShipmentEvent, ShipmentState, decide_delivery


def test_exception_requires_review_and_customer_update() -> None:
    event = ShipmentEvent(
        shipment_id="order-77",
        state=ShipmentState.EXCEPTION,
        occurred_at="2026-08-21T10:00:00Z",
        note="Address label is unreadable",
    )

    decision = decide_delivery(event, proof=None)

    assert decision.state is ShipmentState.EXCEPTION
    assert decision.needs_review is True
    assert "checking" in decision.customer_message
