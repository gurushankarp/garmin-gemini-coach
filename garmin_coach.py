import os
import datetime
import smtplib
from email.mime.text import MIMEText
from garminconnect import Garmin
from google import genai

yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()

try:
    print(f"Fetching Garmin metrics for {yesterday}...")
    garmin = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
    garmin.login()

    garmin_payload = {
        "user_summary": garmin.get_user_summary(yesterday),
        "sleep": garmin.get_sleep_data(yesterday),
        "stress": garmin.get_stress_data(yesterday)
    }

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=f"You are an elite sports scientist and recovery coach. Analyze these Garmin metrics for {yesterday}: {garmin_payload}"
    )

    print("\n=== DAILY RECOVERY REPORT ===")
    print(response.text)

    # --- NEW EMAIL CODE ---
    print("\nSending email...")
    email_address = os.getenv("EMAIL_ADDRESS")
    email_password = os.getenv("EMAIL_PASSWORD")

    msg = MIMEText(response.text)
    msg['Subject'] = f"Garmin Recovery Report for {yesterday}"
    msg['From'] = email_address
    msg['To'] = email_address # Sends the email to yourself

    # Connect to Gmail and send
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(email_address, email_password)
    server.send_message(msg)
    server.quit()
    print("Email sent successfully!")

except Exception as e:
    print(f"Error: {e}")
