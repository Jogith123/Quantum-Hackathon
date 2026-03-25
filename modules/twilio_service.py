import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()  # Load .env credentials automatically

def get_client():
    """Returns a Twilio client using environment variables."""
    sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    
    # Return None if credentials are not configured, so we can gracefully fallback
    if not sid or not auth_token:
        return None
        
    return Client(sid, auth_token)

def send_whatsapp(to_number: str, message: str) -> bool:
    """
    Sends a WhatsApp message via Twilio Sandbox.
    The recipient must have joined the sandbox first by sending:
      'join <sandbox-keyword>' to +14155238886
    """
    client = get_client()
    
    if not client:
        print(f"\n[⚠️ TWILIO NOT CONFIGURED] Fallback Console Alert:")
        print(f"[FALLBACK WhatsApp to {to_number}] {message}\n")
        return False

    try:
        sandbox_number = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
        msg = client.messages.create(
            body=message,
            from_=sandbox_number,
            to=f"whatsapp:{to_number}"
        )
        print(f"[WhatsApp SENT] SID: {msg.sid} -> {to_number}")
        return True
    except Exception as e:
        print(f"[WhatsApp FAILED] Twilio error: {str(e)}")
        print(f"[FALLBACK PRINT] {message}")
        return False

# Keep send_sms as an alias for backward compatibility
send_sms = send_whatsapp
