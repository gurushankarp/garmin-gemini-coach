import os
import datetime
from garminconnect import Garmin
from google import genai

today = datetime.date.today().isoformat()

try:
    print(f"Fetching Garmin metrics for {today}...")
    garmin = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
    garmin.login()

    garmin_payload = {
        "user_summary": garmin.get_user_summary(today),
        "sleep": garmin.get_sleep_data(today),
        "stress": garmin.get_stress_data(today)
    }

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=f"You are an elite sports scientist and recovery coach. Analyze these Garmin metrics for {today}: {garmin_payload}"
    )

    print("\n=== DAILY RECOVERY REPORT ===")
    print(response.text)

except Exception as e:
    print(f"Error: {e}")
