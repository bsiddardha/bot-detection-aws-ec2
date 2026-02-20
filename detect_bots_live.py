import re
import joblib
import pandas as pd
from datetime import datetime, timedelta
import boto3


LOG_FILE = "/var/log/nginx/access.log"
WINDOW_MINUTES = 5

#i Randomforest g
MODEL_PATH = "bot_detection_model.pkl"

SNS_TOPIC_ARN = "arn:aws:sns:eu-north-1:140723489456:bot-detection-alerts"
AWS_REGION = "eu-north-1"

BOT_PROB_THRESHOLD = 0.9

# Load ML model
model = joblib.load(MODEL_PATH)

# SNS client (uses EC2 IAM role)
sns = boto3.client("sns", region_name=AWS_REGION)

# NGINX log regex
log_pattern = re.compile(
    r'(?P<ip>\S+) .* \[(?P<time>.*?)\] "(?P<req>.*?)" .* "(?P<ua>.*?)"$'
)

def parse_time(t):
    return datetime.strptime(t.split()[0], "%d/%b/%Y:%H:%M:%S")

# ================= READ LOGS =================
rows = []

with open(LOG_FILE) as f:
    for line in f:
        match = log_pattern.search(line)
        if not match:
            continue

        rows.append({
            "ip": match.group("ip"),
            "time": parse_time(match.group("time")),
            "url": match.group("req"),
            "ua": match.group("ua")
        })

df = pd.DataFrame(rows)

if df.empty:
    print("ℹ️ No traffic found")
    exit()

# ================= TIME WINDOW =================
latest_time = df["time"].max()
df = df[df["time"] >= latest_time - timedelta(minutes=WINDOW_MINUTES)]

if df.empty:
    print("ℹ️ No traffic in last window")
    exit()

# ================= FEATURE EXTRACTION =================
features = []

for ip, g in df.groupby("ip"):
    rpm = len(g)
    avg_gap = g["time"].sort_values().diff().dt.total_seconds().mean()
    unique_urls = g["url"].nunique()
    empty_ua_ratio = (g["ua"] == "-").mean()

    features.append({
        "ip": ip,
        "requests_per_minute": rpm,
        "avg_time_between_requests": avg_gap if avg_gap else 0,
        "unique_urls": unique_urls,
        "empty_user_agent_ratio": empty_ua_ratio,
        "same_ip_ratio": 1.0
    })

feature_df = pd.DataFrame(features)

# ================= PREDICTION =================
X = feature_df.drop("ip", axis=1)

predictions = model.predict(X)
probabilities = model.predict_proba(X)[:, 1]

feature_df["is_bot"] = predictions
feature_df["bot_probability"] = probabilities

bots = feature_df[feature_df["bot_probability"] >= BOT_PROB_THRESHOLD]

# ================= ACTION =================
if bots.empty:
    print("✅ Traffic analyzed — no bots detected")
else:
    print("🚨 BOT DETECTED 🚨")

    for _, row in bots.iterrows():
        message = f"""
🚨 BOT TRAFFIC DETECTED 🚨

IP Address: {row['ip']}
Requests per minute: {row['requests_per_minute']}
Unique URLs: {row['unique_urls']}
Bot Probability: {round(row['bot_probability'] * 100, 2)} %

Time Window: Last {WINDOW_MINUTES} minutes
"""

        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="🚨 EC2 Bot Traffic Detected",
            Message=message
        )

        print(f"🚨 Alert sent for IP: {row['ip']}")

