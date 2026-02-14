# bot-detection-aws-ec2







Here is a clean, professional **README.md** for your project.
Just copy this into a file named `README.md`.

---

# 🚨 Real-Time Bot Detection System (AWS EC2 + Nginx + ML)

## 📌 Project Overview

This project is a **real-time bot detection system** that:

* Monitors live traffic from **Nginx access logs**
* Extracts request-based features
* Uses a **Random Forest ML model**
* Detects suspicious / bot-like traffic
* Can trigger alerts (optional SNS integration)

The system runs on an **AWS EC2 instance** and analyzes real server traffic.

---

## 🏗️ Architecture

Local Machine → Sends HTTP Traffic
⬇
AWS EC2 (Ubuntu)
⬇
Nginx Web Server
⬇
Access Logs (`/var/log/nginx/access.log`)
⬇
Feature Extraction
⬇
Trained ML Model (`bot_detection_model.pkl`)
⬇
Bot / Normal Classification

---

## 📂 Project Structure

```
detect_bots_live.py          # Real-time log analysis & prediction
train_model.py               # Model training script
test_model.py                # Model testing script
realistic_bot_training_data_v2.csv  # Training dataset
bot_detection_model.pkl      # Trained ML model
```

---

## ⚙️ Features Used for Training

The model is trained using realistic traffic metrics such as:

* `requests_per_minute`
* `unique_urls`
* `avg_time_between_requests`
* `is_suspicious_user_agent`
* `failed_requests_ratio`

### Traffic Behavior Logic

Normal Users:

* 5–80 requests per minute
* Normal browsing patterns
* Mixed URLs
* Real user agents

Bots:

* 100+ requests per minute
* Repeated same endpoint
* Very small time gaps
* Empty or suspicious user agents

---

## 🧠 Model Details

* Algorithm: Random Forest Classifier
* Framework: Scikit-learn
* Output:

  * 0 → Normal User
  * 1 → Bot

---

## 🚀 Setup Instructions

### 1️⃣ Install dependencies

```bash
pip install pandas scikit-learn numpy
```

---

### 2️⃣ Train the model

```bash
python train_model.py
```

This will generate:

```
bot_detection_model.pkl
```

---

### 3️⃣ Test the model

```bash
python test_model.py
```

---

### 4️⃣ Run Live Detection (on EC2)

```bash
python detect_bots_live.py
```

It will:

* Read last 5 minutes of nginx logs
* Extract features
* Predict bot activity
* Print result in terminal

---

## 🔎 Checking Nginx Logs

```bash
sudo tail -f /var/log/nginx/access.log
```

---

## 🌐 Sending Traffic from Local Machine

Example:

```bash
curl http://<EC2_PUBLIC_IP>/
```

Or using browser.

---

## 🛑 Important Notes

* If EC2 is terminated, all files will be lost unless:

  * Pushed to GitHub
  * Backed up
  * Using EBS snapshot

* Do NOT commit:

  * `botenv/`
  * `aws/`
  * AWS credentials

---

## 📈 Future Improvements

* Add CloudWatch log streaming
* Integrate SNS email alerts
* Convert to Flask API service
* Deploy as systemd background service
* Add IP blocking (iptables / fail2ban)
* Add real-time dashboard


