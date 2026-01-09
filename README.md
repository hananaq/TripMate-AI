# TripMate-AI

TripMate-AI is a Streamlit travel assistant that generates a smart packing guide and a multi-day itinerary in one click. It focuses on practical logistics (packing, luggage size, laundry, plugs, safety) and pairs the output with a simple currency note and downloadable PDFs.

## How it works
- **Base model:** DeepSeek (`deepseek-chat`) accessed through an OpenAI-compatible endpoint.
- **Weather API:** OpenWeather is used only when the travel date is within the next 5 days. If the date is beyond that window or the API is unavailable, the app falls back to seasonal/climatological knowledge .
- **Currency:** The model estimates today's USD exchange rate without calling external currency APIs.

## Project structure
- `app.py` - Streamlit UI, output rendering, and PDF export.
- `agent.py` - Prompting logic, weather tool, and model wiring.
- `requirements.txt` - Python dependencies.

## Setup
1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Create a `.env` with your API keys:
   ```
   OPENWEATHER_API_KEY=your_openweather_key
   DEEPSEEK_API_KEY=your_deepseek_key
   ```
3. Run the app:
   ```
   streamlit run app.py
   ```
