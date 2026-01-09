import os
import requests
from datetime import datetime
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()

def _get_secret(key):
    try:
        return st.secrets.get(key)
    except Exception:
        return None

OPENWEATHER_API_KEY = _get_secret("OPENWEATHER_API_KEY") or os.getenv("OPENWEATHER_API_KEY")
DEEPSEEK_API_KEY = _get_secret("DEEPSEEK_API_KEY") or os.getenv("DEEPSEEK_API_KEY")

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage 

# 1. Setup the Weather Tool
@tool
def get_weather_forecast(city: str, travel_date: str):
    """
    Gets weather for a city. 
    Format travel_date as YYYY-MM-DD.
    Only works for dates within the next 5 days.
    """
    try:
        trip_dt = datetime.strptime(travel_date, "%Y-%m-%d")
        delta = (trip_dt - datetime.now().days) # Current date check
        
        # If API limit is hit or date is far, we return a fallback signal
       
        if not OPENWEATHER_API_KEY:
            return "API_UNAVAILABLE"

        if delta > 5 or delta < 0:
            return "DATE_TOO_FAR"

        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url).json()
        
        if str(response.get("cod")) != "200":
            return "API_LIMIT_OR_ERROR"
            
        forecast_item = response['list'][0]
        desc = forecast_item['weather'][0]['description']
        temp = forecast_item['main']['temp']
        return f"Real-time forecast for {city} on {travel_date}: {desc}, {temp}°C."
    
    except Exception:
        return "FALLBACK_TO_INTERNAL_KNOWLEDGE"

# 2. Setup the DeepSeek Agent
def get_deepseek_agent(temperature=0.7):
    return ChatOpenAI(
        model="deepseek-chat",
        openai_api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com",
        temperature=temperature
    )

# 3. Execution Function (Packing) - UPDATED FOR SMART LOGISTICS
def run_advisor(destination, date, duration):
    llm = get_deepseek_agent(temperature=0.4) 
    agent = llm.bind_tools([get_weather_forecast])
    today_str = datetime.now().strftime('%B %d, %Y')
    
    system_instruction = f"""
    You are TripMate, a strategic travel logistics expert. Today is {today_str}.
    - If weather tools return DATE_TOO_FAR or API errors, do NOT mention it. Silently use historical data.
    - Always assume the user wants to pack efficiently (Smart Casual).
    - Consider the destination's infrastructure:
        1. If a country (like Japan) is known for laundry facilities in hotels, advise packing light.
        2. If a destination has tiny hotel rooms (like London, Paris, NYC, or Japan), warn against large suitcases.
        3. If cobblestone streets or many stairs are common, suggest backpacks or small carry-ons.
    - Provide the destination currency and the USD exchange rate as of today. Do not use external currency APIs.
    """
    
    query = f"""
    I am traveling to {destination} on {date} for {duration} days.
    
    Instructions:
    1. **🌤️ Weather Analysis:** Provide a brief summary only (e.g., "cool and cloudy with a chance of rain"). Include a simple temperature range like "Temp range: 12–18°C." Do NOT include humidity, sunlight, or separate day/night highs.
    2. **🎒 Packing Strategy:** - Scale the quantity of items to exactly {duration} days.
       - Include specific clothing layers based on the climate.
       - **Laundry:** If {destination} has high availability of laundry, tell me to pack for half the trip.
    3. **🧳 Logistics Alert:** Advise on suitcase size based on local hotel room sizes and ease of transport.
    4. **💡 Local Tips:** Mention electricity plug types, safety, and cultural dress codes (e.g., covering shoulders in temples).
    5. **💱 Currency:** State the local currency and today's USD exchange rate.
    
    STRICT: No sightseeing suggestions. No apologies. Use exactly 5 bold section headings with icons (Weather, Packing, Logistics Alert, Local Tips, Currency). Do not use bold text inside sections.
    """
    
    messages = [
        SystemMessage(content=system_instruction),
        HumanMessage(content=query)
    ]
    
    ai_msg = agent.invoke(messages)
    messages.append(ai_msg)
    
    if ai_msg.tool_calls:
        for tool_call in ai_msg.tool_calls:
            tool_output = get_weather_forecast.invoke(tool_call)
            
            # Sanitizing tool outputs so the model doesn't apologize
            if tool_output in ["DATE_TOO_FAR", "API_LIMIT_OR_ERROR", "API_UNAVAILABLE"]:
                tool_output = f"Provide historical climate analysis for {destination} in {date}."

            messages.append(ToolMessage(
                tool_call_id=tool_call["id"],
                content=str(tool_output)
            ))
            
        final_response = agent.invoke(messages)
        return final_response.content
    
    return ai_msg.content

# 4. Execution Function (Itinerary)
def get_itinerary(destination, date, duration):
    agent = get_deepseek_agent(temperature=0.7)
    today_str = datetime.now().strftime('%B %d, %Y')
    
    query = f"""
    Create a {duration}-day itinerary for {destination} starting {date}.
    - Match the duration ({duration} days) exactly.
    - Suggest 2-3 specific restaurants and local dishes.
    - Include specific attractions.
    - At the end, include a 'Money Intel' section with the local currency and the USD exchange rate as of {today_str}. Do not use external currency APIs.
    - DO NOT discuss weather tools or ask questions. 
    - Format Day 1, Day 2, etc.
    """
    
    messages = [HumanMessage(content=query)]
    response = agent.invoke(messages)
    return response.content
