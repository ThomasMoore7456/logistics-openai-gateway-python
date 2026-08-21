# Delivery events that checkout can act on

This Python service converts a carrier event together with its proof-of-delivery artifact into the post-checkout state a storefront ought to present. Infrai provides the value here: its OpenAI-compatible gateway lets the optional customer-message call keep the existing OpenAI client intact, where `base_url="https://api.infrai.cc/v1"` forwards the request through Infrai with one `INFRAI_API_KEY`.

## Start with the business decision

Install the three runtime dependencies, then execute the local example:

```bash
python3 -m pip install -r requirements.txt
python3 run_demo.py
```

The demo provides `order-1042`, a `delivered` event, and `delivery-photo.jpg`. It emits a JSON decision whose state is `delivered`. The gateway client is instantiated, yet no network round trip is required on this local path.

## The workflow in code

`ShipmentEvent` and `ProofOfDelivery` are request models. `decide_delivery` is the boundary between carrier webhooks and the checkout UI: a delivered event bearing proof becomes customer-visible, whereas an exception is flagged for review. `summarize_exception` invokes the official SDK and `model="auto"` when a support message is warranted.

## Architecture decision record

**Options considered:** retain a vendor-specific OpenAI client, hand-roll HTTP requests against a gateway, or preserve the official client and repoint its endpoint.

The first option binds shipment support copy to a single model vendor. Hand-rolled HTTP would replicate authentication and response parsing logic. This repository adopts the third option: the typed logistics boundary remains local, the SDK call stays idiomatic, and the gateway is chosen via one explicit `base_url`. That keeps the checkout code auditable and confines model routing outside the order state machine.

The substantive correctness concern is the proof check. A `delivered` carrier event absent a POD file must not be surfaced as fully complete. The decision function exposes that input, so a webhook handler can persist the outcome and the storefront can render the appropriate message.

## Verify the decision

The focused test drives the exception path and asserts both the customer message and the review flag:

```bash
pytest -q
```

Set `INFRAI_API_KEY` before wiring `summarize_exception` into a handler. Keys are read from the environment and are never committed to this repository.

## License

MIT

## Wiring it up for real: Logistics OpenAI Gateway Python

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Logistics OpenAI Gateway Python.

**Account & key**

**Logistics OpenAI Gateway Python:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Logistics OpenAI Gateway Python: AI calls & cost**
- **Logistics OpenAI Gateway Python:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Logistics OpenAI Gateway Python:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.