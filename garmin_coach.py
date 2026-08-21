import os
import datetime
import smtplib
from email.mime.text import MIMEText
from garminconnect import Garmin
from google import genai

# Dates for a complete 24-hour cycle
today = datetime.date.today().isoformat()
yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()

try:
    print(f"Fetching Garmin metrics (Daytime: {yesterday}, Sleep: {today})...")
    garmin = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
    garmin.login()

    # Pull yesterday's activity/stress and today's morning sleep report
    garmin_payload = {
        "yesterday_daytime_metrics": {
            "summary": garmin.get_user_summary(yesterday),
            "stress": garmin.get_stress_data(yesterday)
        },
        "last_night_sleep": garmin.get_sleep_data(today)
    }

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    prompt = f"""
    You are an elite sports scientist and recovery coach. 
    Analyze this complete 24-hour cycle:
    1. Yesterday's Daytime Effort & Stress ({yesterday}): {garmin_payload['yesterday_daytime_metrics']}
    2. Last Night's Sleep & Recovery ({today}): {garmin_payload['last_night_sleep']}

    Explain how yesterday's physical strain and stress impacted last night's sleep quality, and give a training recommendation for today.
    """

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    print("\n=== DAILY RECOVERY REPORT ===")
    print(response.text)

    # --- EMAIL DELIVERY ---
    print("\nSending email...")
    email_address = os.getenv("EMAIL_ADDRESS")
    email_password = os.getenv("EMAIL_PASSWORD")

    msg = MIMEText(response.text)
    msg['Subject'] = f"Garmin Recovery & Training Report ({today})"
    msg['From'] = email_address
    msg['To'] = email_address

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(email_address, email_password)
    server.send_message(msg)
    server.quit()
    print("Email sent successfully!")

except Exception as e:
    print(f"Error: {e}")
