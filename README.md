# 💨 Compressed Air Ring Main Network — Live Monitoring Dashboard

A production-grade, interactive industrial monitoring application built with Python and Streamlit. This dashboard establishes a real-time data streaming connection with a cloud-managed Neon PostgreSQL database to monitor pressure and flow metrics across various industrial departments.

## 🚀 Live Application Link
[Click here to view the live production dashboard](https://compressed-air-dashboard-pmr6qncweb9fry8rdvzc3j.streamlit.app/)

---

## ✨ Features

* **Real-Time Data Streaming:** Continuously polls and fetches timestamped data directly from a cloud-hosted Neon Postgres instance.
* **Sleek Dark Theme UI:** Designed with a custom dark palette optimized for industrial control rooms to maximize scannability.
* **Smart Safety Thresholds:** Built-in logic flags abnormal values instantly:
  * **Critical Low Pressure Alert:** Triggers if pressure falls below `6.0 Bar`.
  * **Critical Low Flow Alert:** Triggers if flow rate falls below `200.0 Nm³/h`.
* **Dynamic Historical Trend Analysis:** Interactive line charts powered by Plotly, allowing users to filter tracking matrices by specific plant departments (e.g., *BF Utility*, *Engg Shops*).
* **Live Activity Logs:** A collapsible data grid viewer to view chronological database metrics on demand.

---

## 🛠️ Tech Stack & Architecture

* **Frontend Framework:** Streamlit (Python-based Web UI)
* **Database Backend:** Neon Cloud Serverless PostgreSQL
* **Data Visualization:** Plotly Graphing Library & Pandas DataFrames
* **Deployment System:** Streamlit Community Cloud hooked with GitHub CI/CD

---

## 📂 Project Structure

* `app.py` — Core application logic containing database connectors, interface layout, CSS styling, and threshold validation.
* `requirements.txt` — Configuration manifest detailing underlying module dependencies (`psycopg2-binary`, `pandas`, `plotly`).

---

## 🔒 Configuration & Deployment Secret

The app utilizes a secured TOML environment configuration file to securely query the system backend via encrypted Streamlit Secrets:

```toml
DATABASE_URL = "postgresql://neondb_owner:YOUR_SECRET_KEY@ep-your-pool-id.eastus2.azure.neon.tech/neondb?sslmode=require"
