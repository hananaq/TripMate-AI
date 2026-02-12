import os
import requests
from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st
from datetime import datetime, timedelta

load_dotenv()
def _get_secret(key):
    try:
        return st.secrets.get(key)
    except Exception:
        return None

OPENWEATHER_API_KEY = _get_secret("OPENWEATHER_API_KEY") or os.getenv("OPENWEATHER_API_KEY")
DEEPSEEK_API_KEY = _get_secret("DEEPSEEK_API_KEY") or os.getenv("DEEPSEEK_API_KEY")


class TripMateAgent:
    def __init__(self):
        self.client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com"
        )
        self.weather_api_key = OPENWEATHER_API_KEY 
        
    def get_weather_data(self, city: str, travel_date: str) -> dict:
        """Fetch weather data if within 5-day forecast window."""
        try:
            travel_dt = datetime.strptime(travel_date, "%Y-%m-%d")
            days_until = (travel_dt - datetime.now()).days
            
            if days_until < 0 or days_until > 5 or not self.weather_api_key:
                return None
                
            url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={self.weather_api_key}&units=metric"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "temp": data["list"][0]["main"]["temp"],
                    "description": data["list"][0]["weather"][0]["description"],
                    "humidity": data["list"][0]["main"]["humidity"]
                }
        except Exception as e:
            print(f"Weather API error: {e}")
        return None

    def generate_packing_list(self, destination: str, start_date: str, end_date: str, 
                                travel_style: str = "moderate") -> str:
        """Generate smart packing list based on destination and dates."""
        
        weather_info = self.get_weather_data(destination, start_date)
        if weather_info:
            weather_context = f"Current forecast: {weather_info['temp']}°C, {weather_info['description']}"
        else:
            weather_context = self._seasonal_weather_hint(destination, start_date)
        weather_line = f"**WEATHER**: {weather_context}"
        
        prompt = f"""Create a CONCISE packing list for {destination}, {start_date} to {end_date}.

Provide in this compact format (IMPORTANT: Each bullet point MUST be on its own line):

{weather_line}

**CLOTHING** ({travel_style} style)
• Item 1
• Item 2
• Item 3
• Item 4
• Item 5
• Item 6

**ELECTRONICS**
• Adapter type: [Type X (country, plug type details)]
• Phone charger
• Power bank

**LAUNDRY**: [Available/Not readily available] - [brief note on where/how to do laundry if available, or pack more if not]

**LUGGAGE**: [Carry-on/Checked] - [brief reason]

**SPECIAL NOTES**: [1-2 cultural/climate considerations]

CRITICAL: 
- Put each item on a separate line
- Start with CLOTHING section first
- Be SHORT and practical
- Include weather-appropriate clothing based on the season
- IMPORTANT: If laundry facilities are available (laundromats, hotel service, or Airbnb washer), recommend fewer clothing items since traveler can wash during trip
- If laundry not readily available, recommend packing more clothing items
- Adjust clothing quantity based on trip length and laundry access"""

        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=800
        )
        content = response.choices[0].message.content
        if "**WEATHER**:" not in content:
            content = f"{weather_line}\n\n{content}"

        def _packing_list_valid(text: str) -> bool:
            if not text:
                return False
            if "**WEATHER**:" not in text:
                return False
            if "**CLOTHING**" not in text or "**ELECTRONICS**" not in text:
                return False
            if "Adapter type:" not in text:
                return False
            if "**LAUNDRY**" not in text or "**LUGGAGE**" not in text or "**SPECIAL NOTES**" not in text:
                return False
            try:
                clothing_block = text.split("**CLOTHING**", 1)[1].split("**ELECTRONICS**", 1)[0]
                clothing_bullets = [l for l in clothing_block.splitlines() if l.strip().startswith(("•", "-"))]
                if len(clothing_bullets) < 6:
                    return False
                electronics_block = text.split("**ELECTRONICS**", 1)[1]
                electronics_lines = [l for l in electronics_block.splitlines() if l.strip().startswith(("•", "-"))]
                if len(electronics_lines) < 3:
                    return False
            except Exception:
                return False
            return True

        if _packing_list_valid(content):
            return content

        repair_prompt = f"""Rewrite the packing list BELOW to EXACTLY follow the required format and include ALL sections.
Do NOT add extra sections. Use only markdown (**, •). Each bullet on its own line.

REQUIRED FORMAT:
{weather_line}

**CLOTHING** ({travel_style} style)
• Item 1
• Item 2
• Item 3
• Item 4
• Item 5
• Item 6

**ELECTRONICS**
• Adapter type: [Type X (country, plug type details)]


**LAUNDRY**: [Available/Not readily available] - [brief note]

**LUGGAGE**: [Carry-on/Checked] - [brief reason]

**SPECIAL NOTES**: [1-2 cultural/climate considerations]
"""

        repair_response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": repair_prompt}],
            temperature=0.3,
            max_tokens=800
        )
        repaired = repair_response.choices[0].message.content
        if "**WEATHER**:" not in repaired:
            repaired = f"{weather_line}\n\n{repaired}"
        if _packing_list_valid(repaired):
            return repaired

        return f"""{weather_line}

**CLOTHING** ({travel_style} style)
• Weather-appropriate outer layer
• 2-3 tops
• 1-2 bottoms
• Warm layer (sweater/fleece)
• Comfortable walking shoes
• Sleepwear/underwear
**ELECTRONICS**
• Adapter type: [Type X for {destination}]


**LAUNDRY**: Unknown - Pack a few extra basics just in case

**LUGGAGE**: Carry-on - Flexible and easy to manage

**SPECIAL NOTES**: Check local forecasts and dress in layers."""

    def _seasonal_weather_hint(self, destination: str, start_date: str) -> str:
        """Fallback: estimate typical weather for that time of year using historical norms."""
        try:
            month = int(start_date.split("-")[1])
        except Exception:
            month = None

        month_name = datetime.strptime(str(month), "%m").strftime("%B") if month else "that month"
        prompt = f"""Estimate the TYPICAL weather for {destination} in {month_name} based on historical averages.
Return a single short sentence with temperature range in °C and a brief description.
Example: "Typical range 5–12°C with chilly, damp days."
No extra text."""

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=60
            )
            text = response.choices[0].message.content.strip()
            return text if text else "Typical conditions vary; expect seasonal weather"
        except Exception:
            return "Typical conditions vary; expect seasonal weather"

    def generate_itinerary(self, destination: str, start_date: str, end_date: str,
                          interests: str = "general sightseeing") -> str:
        """Generate day-by-day itinerary."""
        
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        num_days = (end - start).days + 1
        
        prompt = f"""Create a {num_days}-day itinerary for {destination} ({interests}).

For each day provide (each bullet on separate line):

**Day X**: [One-line theme]
• Morning (9-12): [1 main activity] 
• Afternoon (12-5): [1 main activity + lunch spot] 
• Evening (5-9): [dinner + 1 activity] 

Keep descriptions to 1 line each. Focus on must-sees. 
Maximum 4 activities per day. Each bullet point on its own line."""

        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1200
        )
        
        return response.choices[0].message.content

    def estimate_budget(self, destination: str, start_date: str, end_date: str,
                       travel_style: str = "moderate", num_travelers: int = 1) -> dict:
        """Generate detailed budget estimation with breakdown."""
        
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        num_days = (end - start).days + 1
        
        prompt = f"""Provide budget estimate for {destination}, {num_days} days, {num_travelers} person(s), {travel_style} style.

IMPORTANT: Start your response with the local currency and exchange rate on the FIRST line like this:
💱 Currency: [Currency Name] ([CODE]) | 1 USD = X [CODE]

Then provide this breakdown IN USD (each section on separate lines):

**Accommodation** ({num_days} nights)
• $XX-XX/night → Total: $XXX-XXX

**Food** (per person/day)
• Breakfast: $X-X
• Lunch: $X-X
• Dinner: $XX-XX
• Daily: $XX-XX → Total ({num_days} days): $XXX-XXX

**Transport**
• Airport transfer: $XX-XX
• Daily local: $X-X/day → Total: $XX-XX
• Total: $XXX-XXX

**Activities**
• Entry fees & tours: $XXX-XXX

**Other**
• SIM/WiFi: $XX
• Tips: $XX
• Buffer: $XX
• Total: $XXX-XXX

**TOTAL: $X,XXX - $X,XXX** ({num_travelers} person(s))
**Per person/day: $XXX-XXX**

**Money Tips**:
• [Tip 1]
• [Tip 2]  
• [Tip 3]

Keep it SHORT. Use current 2026 prices. All amounts in USD. Each item on separate line."""

        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=900
        )
        content = response.choices[0].message.content

        def _budget_valid(text: str) -> bool:
            if not text:
                return False
            required = [
                "💱 Currency:",
                "**Accommodation**",
                "**Food**",
                "**Transport**",
                "**Activities**",
                "**Other**",
                "**TOTAL:",
                "**Per person/day:",
                "**Money Tips**"
            ]
            if not all(k in text for k in required):
                return False
            # Basic bullet presence checks per section
            try:
                acc_block = text.split("**Accommodation**", 1)[1].split("**Food**", 1)[0]
                food_block = text.split("**Food**", 1)[1].split("**Transport**", 1)[0]
                transport_block = text.split("**Transport**", 1)[1].split("**Activities**", 1)[0]
                activities_block = text.split("**Activities**", 1)[1].split("**Other**", 1)[0]
                other_block = text.split("**Other**", 1)[1].split("**TOTAL:", 1)[0]
                tips_block = text.split("**Money Tips**", 1)[1]
                def has_bullets(block):
                    return any(l.strip().startswith(("•", "-")) for l in block.splitlines())
                if not all([
                    has_bullets(acc_block),
                    has_bullets(food_block),
                    has_bullets(transport_block),
                    has_bullets(activities_block),
                    has_bullets(other_block),
                    has_bullets(tips_block),
                ]):
                    return False
            except Exception:
                return False
            return True

        if not _budget_valid(content):
            repair_prompt = f"""Rewrite the budget estimate below to EXACTLY follow the required format.
Do NOT add extra sections. Use only markdown (**, •). Each bullet on its own line.

REQUIRED FORMAT:
💱 Currency: [Currency Name] ([CODE]) | 1 USD = X [CODE]

**Accommodation** ({num_days} nights)
• $XX-XX/night → Total: $XXX-XXX

**Food** (per person/day)
• Breakfast: $X-X
• Lunch: $X-X
• Dinner: $XX-XX
• Daily: $XX-XX → Total ({num_days} days): $XXX-XXX

**Transport**
• Airport transfer: $XX-XX
• Daily local: $X-X/day → Total: $XX-XX
• Total: $XXX-XXX

**Activities**
• Entry fees & tours: $XXX-XXX

**Other**
• SIM/WiFi: $XX
• Tips: $XX
• Buffer: $XX
• Total: $XXX-XXX

**TOTAL: $X,XXX - $X,XXX** ({num_travelers} person(s))
**Per person/day: $XXX-XXX**

**Money Tips**:
• [Tip 1]
• [Tip 2]
• [Tip 3]
"""
            repair_response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": repair_prompt}],
                temperature=0.3,
                max_tokens=900
            )
            content = repair_response.choices[0].message.content

        if not _budget_valid(content):
            content = f"""💱 Currency: [Local Currency] ([CODE]) | 1 USD = X [CODE]

**Accommodation** ({num_days} nights)
• $XX-XX/night → Total: $XXX-XXX

**Food** (per person/day)
• Breakfast: $X-X
• Lunch: $X-X
• Dinner: $XX-XX
• Daily: $XX-XX → Total ({num_days} days): $XXX-XXX

**Transport**
• Airport transfer: $XX-XX
• Daily local: $X-X/day → Total: $XX-XX
• Total: $XXX-XXX

**Activities**
• Entry fees & tours: $XXX-XXX

**Other**
• SIM/WiFi: $XX
• Tips: $XX
• Buffer: $XX
• Total: $XXX-XXX

**TOTAL: $X,XXX - $X,XXX** ({num_travelers} person(s))
**Per person/day: $XXX-XXX**

**Money Tips**:
• Book in advance for better rates.
• Use local transit passes when available.
• Carry a small cash buffer for tips/fees."""

        return {
            "budget_text": content,
            "num_days": num_days,
            "num_travelers": num_travelers
        }

    def get_public_transport_guide(self, destination: str) -> str:
        """Generate comprehensive public transportation guide."""
        
        prompt = f"""Public transport guide for {destination} - BE CONCISE (each item on separate line):

**Metro/Subway**
• Lines & coverage: [1 sentence]
• Tickets: [How to buy, price range]
• Hours: [Typical operating hours]

**Bus**
• Coverage: [1 sentence]
• Payment: [Method & price]

**Taxis/Rideshare**
• Apps: [List 2-3]
• Airport to city: $XX-XX, [time]

**Tourist Passes**
• Best option: [Name] - $XX for [duration]
• Where to buy: [Location/app]

**Key Tips** (each on separate line):
• [Tip 1]
• [Tip 2]
• [Tip 3]
• Apps: [2-3 essential transportation apps]
• Airport options: [Train/metro/bus/taxi, typical time & cost]

Keep under 200 words total. Each bullet on its own line."""

        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=600
        )
        
        return response.choices[0].message.content

    def get_cultural_tips(self, destination: str) -> str:
        """Generate cultural etiquette and local tips."""
        
        prompt = f"""Cultural tips for {destination} - CONCISE format (each item on separate line):

CRITICAL: Use markdown only (** for headers, • for bullets). NO HTML tags.

**Greetings**: [1 sentence on how to greet]

**Dress**: [1 sentence on dress norms]

**Dining**
• Tipping: [X%] - [where applies]
• Table manners: [1 key point]

**Essential Phrases**
• Hello/Bye: [phrase]
• Thank you: [phrase]
• How much?: [phrase]

**DO** ✅ (each on separate line)
• [Point 1]
• [Point 2]
• [Point 3]
• [Point 4]

**DON'T** ❌ (each on separate line)
• [Point 1]
• [Point 2]
• [Point 3]
• [Point 4]

**Religious Sites**: [1 sentence on requirements]

Keep total under 150 words. Use markdown only, NO HTML. Each bullet on its own line."""

        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=500
        )
        
        return response.choices[0].message.content

    def get_restaurant_recommendations(self, destination: str, 
                                      dietary_restrictions: list = None,
                                      meal_type: str = "all",
                                      budget: str = "moderate") -> str:
        """Generate restaurant recommendations with dietary filters."""
        
        dietary_str = ", ".join(dietary_restrictions) if dietary_restrictions else "all diets"
        
        prompt = f"""Restaurant guide for {destination} ({dietary_str}, {budget} budget):

CRITICAL: Use ONLY markdown format. Headers with **, bullets with •. DO NOT use HTML tags like <h4>, <strong>, etc.

**Must-Try Local Dishes** (each on separate line)
• [Dish 1]: [1-line description]
• [Dish 2]: [1-line description]
• [Dish 3]: [1-line description]

**Budget ($)** - 2-3 spots (each on separate line)
• [Name/Type]: [Specialty] - $X-XX
• [Name/Type]: [Specialty] - $X-XX

**Mid-Range ($$)** - 2-3 spots (each on separate line)
• [Name/Type]: [Specialty] - $X-XX
• [Name/Type]: [Specialty] - $X-XX

**Upscale ($$$)** - 1-2 spots (each on separate line)
• [Name/Type]: [Specialty] - $XX+

{f"**{dietary_str} Options** (each on separate line)" if dietary_restrictions else ""}
{f"• [Spot 1]" if dietary_restrictions else ""}
{f"• [Spot 2]" if dietary_restrictions else ""}

**Food Markets**: [1-2 best markets]

**Key Tips** (each on separate line):
• [Tip 1]
• [Tip 2]
• [Tip 3]

IMPORTANT: Use markdown only (** and •), NO HTML. Keep under 200 words. Each bullet on separate line."""

        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=700
        )
        
        return response.choices[0].message.content

    def get_currency_info(self, destination: str) -> str:
        """Get currency and payment information."""
        
        prompt = f"""Currency info for {destination} - ULTRA CONCISE (each item on separate line):

💱 **[Currency name]** ([CODE])
• 1 USD = X [CODE] (2026 estimate)
• Best exchange: [Where]
• Cards: [Widely/Moderately/Rarely accepted]
• ATM fees: [Typical amount]

Keep to 3-4 lines max. Each point on separate line."""

        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=200
        )
        
        return response.choices[0].message.content
