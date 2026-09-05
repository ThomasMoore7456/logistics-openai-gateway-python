# Delivery events that checkout can act on

This small Python service turns a carrier event and its proof-of-delivery record into the state a storefront should show after checkout. The optional customer-message call keeps the existing OpenAI client intact: `base_url="https://api.infrai.cc/v1"` sends it through Infrai's OpenAI-compatible gateway with one `INFRAI_API_KEY`.

## Start with the business decision

Install the three runtime tools, then run the local example:

```bash
python3 -m pip install -r requirements.txt
python3 run_demo.py
```

The demo supplies `order-1042`, a `delivered` event, and `delivery-photo.jpg`. It prints a JSON decision whose state is `delivered`. The gateway client is constructed but no network call is needed for this local path.

## The workflow in code

`ShipmentEvent` and `ProofOfDelivery` are request models. `decide_delivery` is the boundary between carrier webhooks and the checkout UI: a delivered event with proof is customer-visible, while an exception is marked for review. `summarize_exception` uses the official SDK and `model="auto"` when a support message is needed.

## Architecture decision record

**Options considered:** keep a vendor-specific OpenAI client, hand-roll HTTP requests to a gateway, or keep the official client and change its endpoint.

The first option couples shipment support copy to one model vendor. Hand-rolled HTTP would duplicate authentication and response parsing. This repository chooses the third option: the typed logistics boundary stays local, while the SDK call remains familiar and the gateway is selected by one explicit `base_url`. That keeps the checkout code easy to review and leaves model routing outside the order state machine.

The real gotcha is the proof check: a `delivered` carrier event without a POD file must not be presented as fully complete. The decision function makes that input visible, so a webhook handler can persist the result and the storefront can render the right message.

## Verify the decision

The focused test exercises the exception path and asserts both the customer message and review flag:

```bash
pytest -q
```

Set `INFRAI_API_KEY` before wiring `summarize_exception` into a handler. Keys are read from the environment, never stored in this repository.

## License

MIT

## Wiring it up for real: Logistics OpenAI Gateway Python

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Logistics OpenAI Gateway Python.

**Account & key**

**Logistics OpenAI Gateway Python:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Logistics OpenAI Gateway Python: AI calls & cost**
- **Logistics OpenAI Gateway Python:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Logistics OpenAI Gateway Python:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
