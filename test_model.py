import joblib
import pandas as pd

model = joblib.load("bot_detection_model.pkl")

tests = [
    {
        "name": "Normal User",
        "requests_per_minute": 30,
        "avg_time_between_requests": 4.5,
        "unique_urls": 15,
        "empty_user_agent_ratio": 0.02,
        "same_ip_ratio": 0.3,
    },
    {
        "name": "Aggressive Bot",
        "requests_per_minute": 1200,
        "avg_time_between_requests": 0.05,
        "unique_urls": 1,
        "empty_user_agent_ratio": 1.0,
        "same_ip_ratio": 1.0,
    },
]

df = pd.DataFrame(tests)
names = df.pop("name")

predictions = model.predict(df)
probs = model.predict_proba(df)

for i in range(len(df)):
    print("\n" + names[i].center(40, "="))
    print("Prediction:", "BOT" if predictions[i] == 1 else "NORMAL")
    print("Bot probability:", round(probs[i][1] * 100, 2), "%")

