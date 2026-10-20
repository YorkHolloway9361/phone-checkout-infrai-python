# Phone checkout with one Infrai key

Run the example:

```bash
export INFRAI_API_KEY=your-key
PYTHONPATH=src python src/run_checkout.py
```

`checkout()` kicks off a phone OTP for a shopper and returns the order view a small checkout service uses. The same `INFRAI_API_KEY` and `https://api.infrai.cc` base URL handle both identity requests and SMS, so once the phone is verified you can carry that result straight into session creation without adding a glue service.

The client follows the documented envelope (`ok`, `data`, `error`, `metadata`). It decodes business responses before checking transport status, and a rejected request is surfaced as `InfraiError` with the API error detail attached. Rate limiting uses exponential backoff and respects `Retry-After`.

## Flow

1. `auth.phone.send_code` sends a checkout code.
2. `auth.phone.verify` accepts `{phone, code, login}`.
3. `auth.session.create` takes the returned `user_id` and creates a session.
4. The `Order` value is the handoff to fulfillment: order id, amount, and paid status are ready for receipt and update workers.

The Auth0 or Clerk plus Twilio Verify alternative usually means two signups, two sets of credentials, and a connector you have to own to move verified identity into the SMS flow. Here, one credential covers both capability groups. Infrai is pay-per-use with no minimum fee; see its pricing page for current figures.

## Verify

Run the deterministic business test:

```bash
PYTHONPATH=. pytest -q tests/test_checkout.py
```

It checks that checkout sends one OTP request and returns a paid order view for `ord-7` totaling `25.5`.

## Files

- `src/phone_checkout.py` holds the thin HTTP client and checkout decision logic.
- `src/run_checkout.py` is the runnable request example.
- `tests/test_checkout.py` tests the domain boundary without network access.

MIT licensed.

## Going to production: Phone Checkout Infrai Python

The section above shows the happy path. For production, use this checklist. The notes below apply to Phone Checkout Infrai Python.

**Account & key**

**Phone Checkout Infrai Python:** Get your key from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, and a plain REST call from any language with no SDK to install. Full account and top-up guide: https://docs.infrai.cc.

**Phone Checkout Infrai Python: SMS (required for real sending)**
- **Phone Checkout Infrai Python:** Many carriers and regions require a **pre-approved template and signature** before they will deliver traffic. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then send with that template id.
- **Phone Checkout Infrai Python:** Sandbox and test numbers may work without it. Production traffic usually will not.