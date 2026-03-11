# 🛡️ Global Cyber Incidents Analytics Dashboard

Interactive Streamlit dashboard connected to Databricks Gold Layer for real-time cybersecurity breach analytics.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red)
![Databricks](https://img.shields.io/badge/Databricks-SQL-orange)

---

## 🚀 Deploy to Streamlit Cloud (via GitHub)

### Step 1 — Create GitHub Repository

```bash
# In your terminal, navigate to this project folder
cd cyber-dashboard

# Initialize git
git init
git add .
git commit -m "Initial commit: Cyber Incidents Dashboard"

# Create repo on GitHub (via github.com > New Repository)
# Name it: cyber-incidents-dashboard
# Keep it Public (required for free Streamlit Cloud)

# Connect and push
git remote add origin https://github.com/YOUR_USERNAME/cyber-incidents-dashboard.git
git branch -M main
git push -u origin main
```

### Step 2 — Deploy on Streamlit Cloud

1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Sign in with your **GitHub account**
3. Click **"New app"**
4. Select:
   - **Repository:** `YOUR_USERNAME/cyber-incidents-dashboard`
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. Click **"Advanced settings"** → paste your Databricks secrets:

```toml
[databricks]
server_hostname = "your-workspace.cloud.databricks.com"
http_path = "/sql/1.0/warehouses/your-warehouse-id"
access_token = "dapi_your_real_token"
```

6. Click **"Deploy!"**

Your app will be live at: `https://YOUR_USERNAME-cyber-incidents-dashboard.streamlit.app`

---

## 🖥️ Run Locally

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/cyber-incidents-dashboard.git
cd cyber-incidents-dashboard

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Add your secrets
# Edit .streamlit/secrets.toml with your Databricks credentials

# Run
streamlit run app.py
```

---

## 📁 Project Structure

```
cyber-incidents-dashboard/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .gitignore                  # Protects secrets from git
├── .streamlit/
│   ├── config.toml             # Theme & server config
│   └── secrets.toml            # 🔒 Databricks credentials (NOT in git)
└── README.md                   # This file
```

## 🔐 Security Notes

- **NEVER** commit `secrets.toml` to GitHub
- The `.gitignore` is pre-configured to exclude it
- On Streamlit Cloud, secrets are stored encrypted in the platform
- Your Databricks access token should have minimal READ permissions

---

## 📊 Dashboard Features

| Feature | Description |
|---------|-------------|
| KPI Cards | Total incidents, financial loss, records compromised, avg disclosure time |
| Choropleth Map | Global incident distribution by country |
| Scatter Plot | Revenue vs financial loss correlation (log scale) |
| Bar Chart | Top 10 targeted companies |
| Donut Chart | Attack vector distribution |
| Data Table | Expandable filtered raw data view |
| Sidebar Filters | Year and attack vector filtering |
