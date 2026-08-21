import os
import datetime
import smtplib
from email.mime.text import MIMEText
from garminconnect import Garmin
from google import genai

today = datetime.date.today().isoformat()
yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()

try:
    print(f"Fetching Garmin metrics (Yesterday: {yesterday}, Sleep/Morning: {today})...")
    garmin = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
    garmin.login()

    # Fetch early morning activities for today (if any)
    try:
        today_activities = garmin.get_activities_by_date(today, today)
    except Exception as act_err:
        print(f"Could not fetch today's activities: {act_err}")
        today_activities = []

    garmin_payload = {
        "yesterday_daytime_metrics": {
            "summary": garmin.get_user_summary(yesterday),
            "stress": garmin.get_stress_data(yesterday)
        },
        "last_night_sleep": garmin.get_sleep_data(today),
        "today_morning_activities": today_activities
    }

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    prompt = f"""
    You are an elite sports scientist and recovery coach. 
    Analyze this complete sequence of health and training data:
    1. Yesterday's Daytime Effort & Stress ({yesterday}): {garmin_payload['yesterday_daytime_metrics']}
    2. Last Night's Sleep & Recovery ({today}): {garmin_payload['last_night_sleep']}
    3. Today's Early Morning Activities logged before 9:00 AM ({today}): {garmin_payload['today_morning_activities']}

    Provide a concise breakdown:
    - Sleep Quality: How yesterday's effort influenced last night's sleep score.
    - Morning Session Impact: Analyze any workout completed this morning (or note if no morning session was logged).
    - Guidance for Today: Pacing, rest, or recommended training load for the rest of the day.
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
    msg['Subject'] = f"Garmin Recovery & Morning Report ({today})"
    msg['From'] = email_address
    msg['To'] = email_address

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(email_address, email_password)
    server.send_message(msg)
    server.quit()
    print("Email sent successfully!")

except Exception as e:
    print(f"Error: {e}")
