import africastalking
from core.models import Farmer  # Make sure you have this model in your app

# Initialize Africa's Talking
username = "messaging system"  # Change when going live
api_key = "atsk_5b254d369598cb7309f0e80d7faed886f687a79ae551d0cf2d6a0d517fd28a46a4ad4c47"
africastalking.initialize(username, api_key)

sms = africastalking.SMS

def send_sms_notification(message, phone_number=None, send_to_all=False):
    """
    Sends an SMS notification to:
      - a single farmer (if phone_number is provided), or
      - all farmers (if send_to_all=True).
    """
    try:
        # Determine recipients
        if send_to_all:
            # Fetch all farmers’ phone numbers from the database
            recipients = [farmer.phone_number for farmer in Farmer.objects.all()]
            if not recipients:
                print("⚠️ No farmers found in the database.")
                return None
        elif phone_number:
            # Single recipient
            recipients = [phone_number]
        else:
            print("⚠️ No recipient specified.")
            return None

        # Send SMS
        response = sms.send(message, recipients)
        print(f"✅ SMS sent successfully to {len(recipients)} farmer(s):", response)
        return response

    except Exception as e:
        print("❌ SMS sending failed:", str(e))
        return None
