import yagmail

# Gmail sender credentials (Your account)
GMAIL_USER = "haroldhopwoodvandyckjr@gmail.com"
GMAIL_APP_PASSWORD = "yjffcxgwkpwdnwti"  # App Password without spaces

def send_email(recipient, subject, content):
    try:
        yag = yagmail.SMTP(GMAIL_USER, GMAIL_APP_PASSWORD)
        yag.send(to=recipient, subject=subject, contents=content)
        print(f"✅ Email sent to {recipient}")
        return True
    except Exception as e:
        print("❌ Email sending failed:", e)
        return False
