import hmac
import hashlib
from fastapi import FastAPI, Request, HTTPException

app = FastAPI()
SECRET = b"super_secret_key"

@app.post("/webhook")
async def webhook(request: Request):
    raw_body = await request.body()
    signature = request.headers.get("X-Signature")

    if not signature:
        raise HTTPException(400, "Missing signature header")

    expected = hmac.new(SECRET, raw_body, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected, signature):
        raise HTTPException(401, "Invalid signature")

    return {"ok": True}
