import africastalking

# Initialize Africa's Talking
username = "sandbox"  # Change to your username when going live
api_key = "atsk_5b254d369598cb7309f0e80d7faed886f687a79ae551d0cf2d6a0d517fd28a46a4ad4c47"  # Add your AT API key
africastalking.initialize(username, api_key)

sms = africastalking.SMS

def send_sms_notification(phone_number, message):
    try:
        response = sms.send(message, [phone_number])
        print("✅ SMS sent:", response)
        return True
    except Exception as e:
        print("❌ SMS failed:", e)
        return False
