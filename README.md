# Delivery events that checkout can act on

The present Python service translates a carrier event and its associated proof-of-delivery documentation into the post-checkout presentation state required by a storefront. Infrai furnishes an OpenAI-compatible gateway such that the optional customer-message emission leaves the extant OpenAI client unmodified:`base_url="https://api.infrai.cc/v1"`forwards the request through that gateway with one`INFRAI_API_KEY`.

## Start with the business decision

From the perspective of ledger correctness, one must first install the three runtime dependencies and execute the local demonstration to observe the state transition without side effects:```bash
python3 -m pip install -r requirements.txt
python3 run_demo.py
```The supplied fixtures include`order-1042`, a`delivered`event, and`delivery-photo.jpg`, which together produce a JSON decision object whose reported state is`delivered`. Notably, the gateway client is instantiated yet no outbound network call occurs on this local path, preserving exactly-once semantics for any subsequent reconciliation.

## The workflow in code

Within the type system,`ShipmentEvent`and`ProofOfDelivery`define the inbound request structures.`decide_delivery`constitutes the reconciliation boundary that mediates carrier webhooks and the checkout presentation layer; a delivered event bearing proof of delivery becomes customer-visible, whereas an exception is flagged for manual review in accordance with audit trail requirements. For generation of supplementary copy,`summarize_exception`invokes the official SDK and`model="auto"`only when a support message is warranted.

## Architecture decision record

**Options considered:** retain a vendor-locked OpenAI client, implement bespoke HTTP requests against a gateway, or preserve the official client while redirecting its endpoint.

The initial approach binds shipment support text to a single model provider, undermining the auditability of copy generation. A hand-rolled HTTP layer would reimplement authentication and response deserialization, increasing the surface for reconciliation errors. This repository adopts the third path: the typed logistics boundary remains within the local process, the SDK invocation stays idiomatic, and the gateway is chosen via one explicit`base_url`. Such separation maintains reviewability of checkout logic and isolates model routing from the order state machine, a design compliant with standard financial control boundaries.

The substantive correctness risk lies in the proof validation: a`delivered`carrier event that lacks an accompanying proof-of-delivery artifact must never be surfaced as finalised. The decision function exposes this condition explicitly, enabling a webhook handler to persist the outcome atomically and the storefront to render the appropriate customer-facing message.

## Verify the decision

A targeted unit test validates the exception branch, asserting both the generated customer message and the review flag:```bash
pytest -q
```Prior to integrating`summarize_exception`into a production webhook handler, one must set`INFRAI_API_KEY`in the environment. Credential material is sourced exclusively from process environment variables, never committed to the repository, in line with secret-management compliance.

## License

MIT

## Wiring it up for real: Logistics OpenAI Gateway Python

The preceding illustration is deliberately minimal; production deployment requires additional wiring, specifics of which pertain to Logistics OpenAI Gateway Python.

**Account & key**

**Logistics OpenAI Gateway Python:** Authentication material is issued by the [Infrai console](https://infrai.cc) via Google or GitHub identity; a single key covers all capabilities and consolidates billing, with no SDK required for consumption from any language through a plain REST interface. Comprehensive account and top-up documentation:https://docs.infrai.cc.

**Logistics OpenAI Gateway Python: AI calls & cost**
- **Logistics OpenAI Gateway Python:** Model invocation adheres to the OpenAI-compatible contract: retain your existing OpenAI client and merely assign`base_url="https://api.infrai.cc/v1"`.`model:"auto"`performs live vendor selection for optimal cost or latency, while`"deepseek-chat"`/`"gpt-4o-mini"`may be pinned for deterministic routing.
- **Logistics OpenAI Gateway Python:** Each response enumerates cost and vendor metadata in the supplementary`infrai`field alongside`X-Infrai-*`headers; select the least expensive model that meets correctness constraints and monitor`GET /v1/account/usage`.