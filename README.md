# Weather AI Bot

This project is an AI-powered weather assistant built using **FastAPI**, **Groq LLM**, and the **OpenWeather API**.  
Users can ask questions like _“Weather in Mumbai tomorrow?”_ and the backend responds with accurate, real-time weather information.

---

## 🚀 Features

- Natural language weather queries using **Groq Llama 3**
- Real-time & forecast data from **OpenWeather**
- FastAPI backend with clean REST API
- LangChain tool-calling agent for weather requests
- Works with a simple React frontend

---

## 🛠️ Tech Stack

### Backend
- Python 3.11
- FastAPI
- Groq API (Llama3-70b-8192)
- LangChain
- OpenWeather API

### Frontend
- React + Vite
- Axios for API requests

---

## 📂 Project Structure

weather-ai-bot/
│── backend/
│ ├── main.py
│ ├── requirements.txt
│ ├── .env
│ └── venv/
│
│── frontend/
│ ├── src/
│ ├── public/
│ ├── package.json
│ └── vite.config.js
│
└── README.md


---

## 🔑 Environment Variables

Create a `.env` file inside `backend/`:

GROQ_API_KEY=your_groq_key
OPENWEATHER_API_KEY=your_openweather_key


---

## ▶️ Run Backend

cd backend
pip install -r requirements.txt
uvicorn main:app --reload



Backend runs at:  
`http://127.0.0.1:8000`

---

## ▶️ Run Frontend

cd frontend
npm install
npm run dev



Frontend runs at:  
`http://localhost:3000`


🧑‍💻 Author
Atharva Parchure
