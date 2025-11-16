# main.py
import os
import pathlib
from datetime import datetime, timedelta, timezone

import requests
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

# ------------------------------------------------
# Load environment variables
# ------------------------------------------------
BASE_DIR = pathlib.Path(__file__).parent
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not GROQ_API_KEY:
  raise RuntimeError("GROQ_API_KEY not set in .env")

if not OPENWEATHER_API_KEY:
  raise RuntimeError("OPENWEATHER_API_KEY not set in .env")

# ------------------------------------------------
# Weather tool
# ------------------------------------------------
@tool
def weather_tool(city: str, day_offset: int = 0) -> str:
    """
    Fetch weather for a city using OpenWeather API.
    day_offset = 0 (today), 1 (tomorrow), 2 (day after tomorrow).
    """
    base = "https://api.openweathermap.org/data/2.5"

    try:
        # Current weather
        if day_offset == 0:
            url = f"{base}/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
            data = requests.get(url, timeout=10).json()

            if data.get("cod") == "404":
                return f"City '{city}' not found."

            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            return f"Current weather in {city}: {temp}°C, {desc}."

        # Forecast for next days
        url = f"{base}/forecast?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        data = requests.get(url, timeout=10).json()

        if data.get("cod") == "404":
            return f"City '{city}' not found."

        target_date = (datetime.utcnow() + timedelta(days=day_offset)).date()
        matches = []

        for entry in data["list"]:
            ts = datetime.fromtimestamp(entry["dt"], tz=timezone.utc)
            if ts.date() == target_date:
                matches.append(entry)

        if not matches:
            return f"No forecast available for {city}."

        mid = matches[len(matches) // 2]
        temp = mid["main"]["temp"]
        desc = mid["weather"][0]["description"]

        when = "tomorrow" if day_offset == 1 else "day after tomorrow"
        return f"Weather in {city} {when}: {temp}°C, {desc}."

    except Exception as e:
        return f"Error fetching weather: {e}"


tools = [weather_tool]

# ------------------------------------------------
# LLM (Groq) – tool calling "by hand"
# ------------------------------------------------
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="llama-3.1-8b-instant",   # MAKE SURE this model exists in Groq console
    temperature=0.1,
    max_tokens=256,
)

# ------------------------------------------------
# FastAPI setup
# ------------------------------------------------
app = FastAPI(title="AI Weather Bot with Groq + LangChain")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class WeatherQuery(BaseModel):
    query: str


def call_weather_tool_from_text(text: str) -> str:
    """
    Very small parser:
    - Extract city name (just look after 'in')
    - Detect 'today' / 'tomorrow' / 'day after tomorrow'
    and call weather_tool directly (NO agent loops, so no max iterations issue).
    """
    lower = text.lower()

    # 1) Day offset
    if "day after tomorrow" in lower:
        day_offset = 2
    elif "tomorrow" in lower:
        day_offset = 1
    else:
        day_offset = 0  # default today

    # 2) Try to extract "in <city>"
    city = None
    if " in " in lower:
        # Example: "weather in mumbai tomorrow"
        parts = text.split(" in ", 1)
        after_in = parts[1]
        # stop at " tomorrow", " today", " day after"
        stop_words = [" tomorrow", " today", " day after", " day-after", " dayafter"]
        for stop in stop_words:
            idx = after_in.lower().find(stop)
            if idx != -1:
                after_in = after_in[:idx]
        city = after_in.strip(" ?.,!").title()

    if not city:
        return "Please specify a city name, e.g. 'Weather in Mumbai tomorrow'."

    # 3) Call the actual tool function
    return weather_tool.invoke({"city": city, "day_offset": day_offset})


@app.post("/ask-weather")
async def ask_weather(body: WeatherQuery):
    user_query = body.query.strip()
    if not user_query:
        return {"response": "Please enter a question, e.g. 'weather in Mumbai tomorrow'."}

    # Simple routing: if query mentions 'weather', use the weather tool directly.
    if "weather" in user_query.lower():
        tool_answer = call_weather_tool_from_text(user_query)
        return {"response": tool_answer}

    # Otherwise, let LLM chat normally (no tools).
    system_msg = SystemMessage(
        content=(
            "You are a friendly assistant. "
            "If user asks about weather, ask them to phrase as 'weather in <city> <day>'."
        )
    )
    human_msg = HumanMessage(content=user_query)

    resp = llm.invoke([system_msg, human_msg])
    answer = resp.content if hasattr(resp, "content") else str(resp)

    return {"response": answer}


@app.get("/")
def root():
    return {"status": "Groq + LangChain Weather Bot running"}
