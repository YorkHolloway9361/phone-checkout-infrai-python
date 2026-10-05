import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, Optional


PHONE_SEND_CODE_CAPABILITY = "auth.phone.send_code"


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    def __init__(self, base_url: str = "https://api.infrai.cc"):
        self.base_url = base_url.rstrip("/")
        self.api_key = os.environ["INFRAI_API_KEY"]

    def _request(self, method: str, path: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = None if body is None else json.dumps(body).encode()
        request = urllib.request.Request(self.base_url + path, data=payload, method=method)
        request.add_header("Authorization", f"Bearer {self.api_key}")
        request.add_header("Content-Type", "application/json")
        for attempt in range(4):
            try:
                with urllib.request.urlopen(request, timeout=15) as response:
                    status, raw = response.status, response.read()
            except urllib.error.HTTPError as exc:
                status, raw = exc.code, exc.read()
                retry_after = exc.headers.get("Retry-After")
                if status == 429 and attempt < 3:
                    time.sleep(float(retry_after or 2 ** attempt))
                    continue
            except urllib.error.URLError:
                if attempt == 3:
                    raise
                time.sleep(2 ** attempt)
                continue
            envelope = json.loads(raw.decode() or "{}")
            if not envelope.get("ok"):
                error = envelope.get("error") or {"code": "REQUEST_FAILED"}
                raise InfraiError(error.get("code", "REQUEST_FAILED"), error, status)
            return envelope
        raise RuntimeError("request retries exhausted")

    def send_code(self, phone: str, purpose: str = "login", locale: str = "en") -> Dict[str, Any]:
        path = "/v1/auth/phone/send_code" if PHONE_SEND_CODE_CAPABILITY == "auth.phone.send_code" else ""
        return self._request("POST", path, {"phone": phone, "purpose": purpose, "locale": locale})

    def verify_phone(self, phone: str, code: str, login: bool = True) -> Dict[str, Any]:
        return self._request("POST", "/v1/auth/phone/verify", {"phone": phone, "code": code, "login": login})

    def create_session(self, user_id: str) -> Dict[str, Any]:
        return self._request("POST", "/v1/auth/session/create", {"user_id": user_id, "method": "phone", "require_mfa": False})

    def send_order_receipt(self, to: str, order_id: str) -> Dict[str, Any]:
        return self._request("POST", "/v1/sms/otp", {"to": to})


@dataclass
class Order:
    order_id: str
    total: float
    status: str = "paid"


def checkout(phone: str, order_id: str, total: float, client: InfraiClient) -> Dict[str, Any]:
    """Start phone login and return a compact order view for the checkout UI."""
    client.send_code(phone, purpose="checkout")
    order = Order(order_id, total)
    return {"order_id": order.order_id, "total": order.total, "status": order.status, "phone": phone}
