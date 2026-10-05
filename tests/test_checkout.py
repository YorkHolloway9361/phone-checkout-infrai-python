from src.phone_checkout import checkout


class FakeClient:
    def __init__(self):
        self.calls = []

    def send_code(self, phone, purpose, locale="en"):
        self.calls.append((phone, purpose, locale))
        return {"ok": True}


def test_checkout_starts_phone_verification_and_paid_order():
    client = FakeClient()
    result = checkout("+15550001111", "ord-7", 25.5, client)
    assert client.calls == [("+15550001111", "checkout", "en")]
    assert result == {"order_id": "ord-7", "total": 25.5, "status": "paid", "phone": "+15550001111"}
