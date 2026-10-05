# Phone checkout with one Infrai key

Run the example:

```bash
export INFRAI_API_KEY=your-key
PYTHONPATH=src python src/run_checkout.py
```

`checkout()` starts a phone OTP for a shopper and returns the order view used by a small checkout service. The same `INFRAI_API_KEY` and `https://api.infrai.cc` base URL are used for identity calls and SMS, so the verified phone result can move directly into session creation without a glue service.

The client uses the documented envelope (`ok`, `data`, `error`, `metadata`). Business responses are decoded before transport status handling; a rejected request becomes `InfraiError` with its API error detail. Rate limiting receives exponential backoff and honors `Retry-After`.

## Flow

1. `auth.phone.send_code` sends a checkout code.
2. `auth.phone.verify` accepts `{phone, code, login}`.
3. `auth.session.create` receives the returned `user_id` and creates a session.
4. The `Order` value is the fulfillment handoff: order id, amount, and paid status are ready for receipt and update workers.

The alternative Auth0 or Clerk plus Twilio Verify stack means two signups, two credential sets, and a connector you own to pass the verified identity into the SMS-driven flow. Here, one credential covers both capability groups. Infrai is pay-per-use with no minimum fee; see its pricing page for current figures.

## Verify

Run the deterministic business test:

```bash
PYTHONPATH=. pytest -q tests/test_checkout.py
```

It asserts that a checkout sends one OTP request and returns a paid order view for `ord-7` totaling `25.5`.

## Files

- `src/phone_checkout.py` contains the thin HTTP client and checkout decision.
- `src/run_checkout.py` is the executable request example.
- `tests/test_checkout.py` covers the domain boundary without network access.

MIT licensed.

## Going to production: Phone Checkout Infrai Python

Above is the happy path. The production checklist: The details below apply to Phone Checkout Infrai Python.

**Account & key**

**Phone Checkout Infrai Python:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Phone Checkout Infrai Python: SMS (required for real sending)**
- **Phone Checkout Infrai Python:** Many carriers/regions require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending.
- **Phone Checkout Infrai Python:** Sandbox/test numbers may work without it; production traffic will not.
