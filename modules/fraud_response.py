import time
import uuid
import random
from typing import Dict, Any
from modules.twilio_service import send_sms

# ── Mock User Database ─────────────────────────────────
# Maps user_id → registered phone number (E.164 international format)
MOCK_USERS = {
    "user_123": "+919490823945",  # Primary test user
    "user_456": "+919490823945"   # Same number for dev/test
}

# ── State Management ───────────────────────────────────
OTP_STORE: Dict[str, dict] = {}           # Maps transaction_id -> {"otp": "123456", "user_id": "...", "expires": float}
LAST_SMS_SENT: Dict[str, float] = {}       # Maps user_id -> float (timestamp)

COOLDOWN_SECONDS = 300   # 5 minutes rate limit per user

def generate_otp() -> str:
    """Generates a secure 6-digit OTP."""
    return str(random.randint(100000, 999999))

def can_send_sms(user_id: str) -> bool:
    """Checks if the user is out of the SMS cooldown period to prevent SMS bombing."""
    now = time.time()
    last_sent = LAST_SMS_SENT.get(user_id, 0)
    if (now - last_sent) > COOLDOWN_SECONDS:
        return True
    return False

def handle_response(user_id: str, risk_score: float, amount: float, background_tasks=None, simulate_sms: bool = False) -> dict:
    """
    Determines fraud response action based on risk score.
    Generates OTPs, handles SMS dispatch logic as background tasks, and enforces rate limits.
    """
    if not user_id:
        user_id = "user_123" # Fallback mapping for unauthenticated requests
        
    phone_number = MOCK_USERS.get(user_id, None)
    
    response = {
        "action": "ALLOW",
        "risk_score": risk_score,
        "sms_sent": False,
        "transaction_id": None
    }
    
    # If no phone number is found, degrade gracefully
    if not phone_number:
        if risk_score >= 0.7:
            response["action"] = "BLOCK"
        elif risk_score >= 0.5:
            response["action"] = "OTP"
        return response

    if risk_score >= 0.7:
        # High Risk: Block immediately and alert user
        response["action"] = "BLOCK"
        if can_send_sms(user_id):
            message = (
                f"🚨 Q-Shield FRAUD ALERT\n"
                f"An unusual transaction of ₹{amount:.2f} has been detected and BLOCKED from your account. "
                f"If this was not you, please contact your bank immediately."
            )
            if simulate_sms:
                print(f"[SIMULATED SMS to {phone_number}] {message}")
            else:
                if background_tasks:
                    background_tasks.add_task(send_sms, phone_number, message)
                else:
                    send_sms(phone_number, message)
            LAST_SMS_SENT[user_id] = time.time()
            response["sms_sent"] = True

    elif 0.5 <= risk_score < 0.7:
        # Medium Risk (> 50%): Require OTP Verification
        response["action"] = "OTP"
        transaction_id = f"tx_{uuid.uuid4().hex[:12]}"
        otp = generate_otp()
        
        # Store OTP temporarily (10 mins)
        OTP_STORE[transaction_id] = {
            "otp": otp,
            "user_id": user_id,
            "expires": time.time() + 600 
        }
        response["transaction_id"] = transaction_id
        
        if can_send_sms(user_id):
            message = (
                f"⚠️ Q-Shield Alert: An unusual transaction of ₹{amount:.2f} was attempted on your account.\n"
                f"Your verification OTP is: {otp}\n"
                f"Do NOT share this OTP with anyone. If you did not initiate this, contact your bank."
            )
            if simulate_sms:
                print(f"[SIMULATED SMS to {phone_number}] {message}")
            else:
                if background_tasks:
                    background_tasks.add_task(send_sms, phone_number, message)
                else:
                    send_sms(phone_number, message)
            LAST_SMS_SENT[user_id] = time.time()
            response["sms_sent"] = True

    return response

def verify_otp(transaction_id: str, submitted_otp: str) -> bool:
    """Verifies the OTP for a given transaction."""
    record = OTP_STORE.get(transaction_id)
    if not record:
        return False
        
    # Check expiry
    if time.time() > record["expires"]:
        del OTP_STORE[transaction_id]
        return False
        
    # Verify OTP
    if record["otp"] == str(submitted_otp):
        del OTP_STORE[transaction_id] # Clear after successful use
        return True
        
    return False
