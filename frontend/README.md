# 🏙️ Real Estate Analysis Chatbot (React + Django)

A smart web-based chatbot that analyzes real estate localities using an Excel dataset.
Built as part of the **SigmaValue Full Stack Developer Assignment**.

The system provides:

- 💬 Chat-based user interaction
- 📊 Price & demand trend charts
- 🧾 Filtered property data table
- 🧠 AI or rule-based natural-language summary
- 📤 CSV download (bonus feature)

---

# 🚀 Features

### **Core Features**

✔ Search any locality
✔ Extract and filter real estate data from Excel
✔ Generate charts (price, demand, trend)
✔ View tabular results for selected areas
✔ Auto-detect query type:

- Single area analysis
- Compare multiple locations
- Price growth
- Demand trend

---

### **Bonus Features Implemented**

⭐ **OpenAI-powered summaries**
⭐ **Download filtered CSV**
⭐ **Smart query interpretation engine**
⭐ **Modern chat UI with animations**
⭐ **Clean code structure (React + DRF)**

---

# 🛠️ Tech Stack

### **Frontend**

- React
- Bootstrap
- Recharts
- Axios

### **Backend**

- Django
- Django REST Framework
- Pandas (Excel processing)
- OpenPyXL
- python-dotenv
- OpenAI API (Optional)

---

# 📂 Project Structure

```
sigmavalue-real-estate-chatbot/
│
├── backend/
│   ├── core/
│   ├── realestate/
│   ├── venv/
│   ├── sample_data.xlsx
│   ├── manage.py
│   └── .env
│
└── frontend/
    └── real-estate-chatbot/
        ├── src/
        ├── public/
        └── package.json
```

---

# ⚙️ Setup Instructions

## **1️⃣ Backend Setup (Django)**

```sh
cd backend
.\venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

Add your `.env`:

```
OPENAI_API_KEY=REDACTED

```

Run server:

```sh
python manage.py runserver
```

Backend →
[http://127.0.0.1:8000/api/analyze/](http://127.0.0.1:8000/api/analyze/)

---

## **2️⃣ Frontend Setup (React)**

```sh
cd frontend/real-estate-chatbot
npm install
npm start
```

Frontend →
[http://localhost:3000](http://localhost:3000)

---

# 📡 API Endpoints

### **POST /api/analyze/**

Analyze user query and return:

- Summary
- Chart Data
- Table Data
- Areas detected
- Query classification

Example Request:

```json
{ "message": "Analyze Wakad" }
```

---

### **GET /api/download/?area=Wakad**

Download CSV of filtered data.

---

# 💬 Example Queries

- “Give me analysis of Wakad”
- “Compare Aundh and Baner”
- “Show price growth for Akurdi”
- “Demand trend for Ambegaon Budruk”

---

# 🎨 UI Preview (Add your screenshots)

📌 _Create a folder `/screenshots` in repo and upload images._

Example:

```
/screenshots/chat.png
/screenshots/results.png
/screenshots/chart.png
```

---

# 🎥 Demo Video

demo video of real-estate-chatbot
videolink-https://drive.google.com/drive/u/1/home

---

# 🧑‍💻 Author

**Aniket**
Full-Stack Developer
📌 GitHub: https://github.com/Aniketm09
📧 Email: aniketmali0912@gmail.com

---
