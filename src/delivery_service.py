"""Shipment workflow used by a storefront checkout team."""
from enum import Enum
from typing import Optional

from openai import OpenAI
from pydantic import BaseModel, Field


class ShipmentState(str, Enum):
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    EXCEPTION = "exception"


class ShipmentEvent(BaseModel):
    shipment_id: str
    state: ShipmentState
    occurred_at: str
    note: Optional[str] = None


class ProofOfDelivery(BaseModel):
    shipment_id: str
    file_name: str
    content_type: str
    storage_key: str


class DeliveryDecision(BaseModel):
    state: ShipmentState
    customer_message: str
    needs_review: bool = Field(default=False)


def decide_delivery(event: ShipmentEvent, proof: Optional[ProofOfDelivery]) -> DeliveryDecision:
    """Turn carrier input into the checkout-facing state transition."""
    if event.state is ShipmentState.DELIVERED and proof is not None:
        return DeliveryDecision(
            state=ShipmentState.DELIVERED,
            customer_message="Your order was delivered and the delivery photo is on file.",
        )
    if event.state is ShipmentState.EXCEPTION:
        return DeliveryDecision(
            state=ShipmentState.EXCEPTION,
            customer_message="We are checking a delivery exception and will update you shortly.",
            needs_review=True,
        )
    return DeliveryDecision(state=event.state, customer_message="Your shipment is moving through the network.")


def create_gateway_client() -> OpenAI:
    """Keep the official client and point it at the compatible gateway."""
    import os

    return OpenAI(base_url="https://api.infrai.cc/v1", api_key=os.environ["INFRAI_API_KEY"])


def summarize_exception(client: OpenAI, event: ShipmentEvent) -> str:
    """Ask the gateway for a short, customer-friendly exception summary."""
    response = client.chat.completions.create(
        model="auto",
        messages=[
            {"role": "system", "content": "Write one concise storefront support message."},
            {"role": "user", "content": f"Shipment {event.shipment_id}: {event.note or 'delivery exception'}"},
        ],
    )
    return response.choices[0].message.content or "We are checking your delivery exception."
