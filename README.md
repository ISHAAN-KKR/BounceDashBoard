
# 🛴 Bounce Fleet Management Dashboard

An interactive Streamlit dashboard to monitor and manage a high-speed electric scooter rental fleet. Built for real-time insights, risk alerts, and operational decision-making for gig economy-focused micromobility services in India.

---

## 🚀 Features

- 📍 Real-time fleet location map (Plotly Mapbox)
- 📊 Hub performance and uptime metrics
- 📈 Trend analytics for trip completion and utilization
- 🔋 Alerts for low battery, maintenance, and faults
- 🔧 Maintenance scheduling and swap crew dispatch
- 💬 SMS alert system for fleet managers (via Twilio)
- 📄 Export fleet summary as downloadable CSV
- 🔁 Manual fleet data sync and dashboard refresh

---

## 🧰 Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Data Visualization**: Plotly (Mapbox, Graphs)
- **Backend Logic**: Python
- **Alerts**: Twilio SMS Integration

---

## 📂 Project Structure

```

├── dashboard.py            # Main Streamlit application
├── requirements.txt        # Python dependencies
└── .streamlit/
└── config.toml         # (Optional) Theme and UI settings

````

---

## ⚙️ Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/bounce-dashboard.git
cd bounce-dashboard
````

### 2. Install Dependencies

Create a virtual environment (optional):

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

Then install required packages:

```bash
pip install -r requirements.txt
```

### 3. Run the App Locally

```bash
streamlit run dashboard.py
```

---

## ☁️ Deploy to Streamlit Cloud

1. Push the project to a public GitHub repo.
2. Go to [https://streamlit.io/cloud](https://streamlit.io/cloud)
3. Click **New App** and connect your repo.
4. Set `dashboard.py` as the main file.
5. Click **Deploy** – your app will be live!

---

## 🔐 Optional: Twilio SMS Setup

1. Install Twilio SDK:

   ```bash
   pip install twilio
   ```

2. Get credentials from [Twilio Console](https://console.twilio.com/)

   * Account SID
   * Auth Token
   * Twilio phone number

3. Enter credentials in the Streamlit sidebar during app runtime.


## 🤝 Contributing

Contributions and suggestions welcome! Please open issues or submit PRs.


