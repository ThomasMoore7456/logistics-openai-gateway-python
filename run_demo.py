from src.delivery_service import (
    ProofOfDelivery,
    ShipmentEvent,
    ShipmentState,
    create_gateway_client,
    decide_delivery,
)


def main() -> None:
    event = ShipmentEvent(
        shipment_id="order-1042",
        state=ShipmentState.DELIVERED,
        occurred_at="2026-08-21T09:30:00Z",
    )
    proof = ProofOfDelivery(
        shipment_id=event.shipment_id,
        file_name="delivery-photo.jpg",
        content_type="image/jpeg",
        storage_key="pod/order-1042.jpg",
    )
    print(decide_delivery(event, proof).model_dump_json())
    print("Gateway ready:", type(create_gateway_client()).__name__)


if __name__ == "__main__":
    main()
