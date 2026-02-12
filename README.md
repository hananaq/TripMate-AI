# TripMate AI ✈️

**Your AI-Powered Travel Planning Assistant**

TripMate AI is an intelligent travel planning application that generates comprehensive, personalized travel plans in minutes. Built with Streamlit and powered by DeepSeek AI, it creates detailed itineraries, packing lists, budget estimates, and cultural guides tailored to your destination and preferences.

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

---

## 🌟 Features

### Core Planning Tools

#### 💰 **Budget Estimator**
- Detailed cost breakdown by category (accommodation, food, transport, activities)
- Multi-traveler calculations
- Travel style adjustment (Budget/Moderate/Luxury)
- **Currency information** with exchange rates and local payment tips
- Money-saving recommendations

#### 🎒 **Smart Packing Lists**
- **Clothing-focused** recommendations (appears first)
- Weather-appropriate suggestions with real-time forecasts
- **Laundry-smart packing** - adjusts quantities based on laundry availability
- Electronics with adapter specifications
- Travel style considerations
- Luggage recommendations (carry-on vs checked)

#### 📅 **Personalized Itineraries**
- Day-by-day activity planning
- Interest-based recommendations (sightseeing, food, adventure, culture, etc.)
- Time-efficient routing
- Local insider tips
- Weather integration for outdoor activities

#### 🚇 **Public Transportation Guides**
- Metro/subway/bus/tram system details
- Ticket purchasing and pass information
- Operating hours and frequency
- Airport connection guides
- Tourist-specific navigation tips
- Ride-sharing app recommendations

#### 🌍 **Cultural Tips & Etiquette**
- Local greetings and customs
- Dress code recommendations
- Dining etiquette
- **10+ essential local phrases**
- Do's and Don'ts (5-7 each)
- Religious sensitivity guidelines
- Tipping culture and bargaining norms

#### 🍴 **Restaurant Recommendations**
- **7 dietary filter options**: Vegetarian, Vegan, Halal, Kosher, Gluten-Free, Dairy-Free, Nut Allergies
- Budget ($), mid-range ($$), and upscale ($$$) categories
- Must-try local dishes
- Food markets and street food spots
- Dining tips and reservation advice

### UI/UX Features

#### 🎨 **Beautiful Pastel Design**
- Modern pastel blue color scheme
- 2-column responsive grid layout
- Color-coded sections with dashed borders:
  - 💜 Budget (Purple)
  - 💗 Packing (Pink)
  - 💙 Itinerary (Blue)
  - 💚 Transport (Green)
  - 🧡 Culture (Orange)
  - 💚 Restaurant (Teal)
  - 💜 Currency (Lavender)

#### 🗺️ **Dynamic City Selection**
- Dropdown with "City, Country" format
- Reads from `cities_geonames_1000.csv`
- Smart column detection
- Fallback to manual text input

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- DeepSeek API key ([Get one here](https://platform.deepseek.com))
- OpenWeather API key ([Get one here](https://openweathermap.org/api)) - Optional

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/tripmate-ai.git
   cd tripmate-ai
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   DEEPSEEK_API_KEY=your_deepseek_api_key_here
   OPENWEATHER_API_KEY=your_openweather_api_key_here
   ```

4. **Add optional assets** (optional but recommended)
   
   Place these files in the root directory:
   - `background.png` - Background pattern image
   - `logo.png` - Your logo (displayed at top)
   - `cities_geonames_1000.csv` - City database for dropdown

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Open in browser**
   
   Navigate to `http://localhost:8501`

---

## 📖 Usage Guide

### Step 1: Enter Trip Details
1. Open the sidebar
2. Select or enter your **destination** (City, Country format)
3. Choose **start and end dates**
4. Set **travel style** (Budget/Moderate/Luxury)
5. Enter **number of travelers**

### Step 2: Customize Preferences
1. Select your **interests** (multiple choices):
   - Sightseeing
   - Food & Dining
   - Adventure
   - Culture
   - Nightlife
   - Shopping
   - Nature
   - Relaxation

2. Choose any **dietary restrictions**:
   - Vegetarian
   - Vegan
   - Halal
   - Kosher
   - Gluten-Free
   - Dairy-Free
   - Nut Allergies

### Step 3: Select Sections
Choose which sections to generate (all enabled by default):
- ☑️ Budget Estimate
- ☑️ Packing List
- ☑️ Itinerary
- ☑️ Transport Guide
- ☑️ Cultural Tips
- ☑️ Restaurant Guide

### Step 4: Generate Plan
1. Click **"🚀 Generate Travel Plan"**
2. Watch the progress bar (2-3 minutes)
3. Review your personalized travel plan

### Step 5: Download PDF
1. Scroll to the download section
2. Click **"⬇️ Download Complete Travel Plan (PDF)"**
3. Save to your device

---

## 🏗️ Project Structure

```
tripmate-ai/
├── app.py                      # Main Streamlit application
├── agent.py                    # TripMate AI agent (DeepSeek integration)
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this)
├── README.md                   # This file
├── CHANGELOG.md               # Version history and changes
├── background.png             # Optional: Background image
├── logo.png                   # Optional: Logo image
└── cities_geonames_1000.csv  # Optional: City database
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DEEPSEEK_API_KEY` | Yes | Your DeepSeek API key |
| `OPENWEATHER_API_KEY` | No | OpenWeather API key for weather data |

### Optional Files

| File | Purpose | Format |
|------|---------|--------|
| `cities_geonames_1000.csv` | City dropdown data | CSV with `name` and `country` columns |
| `background.png` | Background pattern | PNG image (400x400px recommended) |
| `logo.png` | App logo | PNG image (150px width recommended) |

### CSV Format Example

```csv
name,country
Paris,France
London,United Kingdom
Tokyo,Japan
New York,United States
```

---

## 🎨 Customization

### Changing Colors

Edit the CSS in `app.py` to customize colors:

```python
# Change primary color (line ~58)
--primary-color: #A8D8EA;  # Your color here

# Change sidebar gradient (line ~197)
background: linear-gradient(180deg, #D4EBF8 0%, #A8D8EA 100%);

# Change box border colors (lines ~98-133)
.budget-box { border: 4px dashed #C7B8EA; }  # Your color
```

### Adjusting Output Length

Modify token limits in `agent.py`:

```python
# Budget section (line ~86)
max_tokens=900  # Increase/decrease

# Packing section (line ~122)
max_tokens=800  # Increase/decrease
```

### Adding New Sections

1. Create a new method in `TripMateAgent` class (agent.py)
2. Add checkbox in sidebar (app.py)
3. Add generation logic in main function
4. Add display section with custom styling

---

## 📊 Performance

### Metrics (v2.0.0)

| Metric | Value |
|--------|-------|
| Generation time | 2-3 minutes |
| API tokens used | ~3,500 tokens |
| Cost per plan | ~$0.01 USD |
| Output length | ~1,500 words |
| Sections available | 6 core + 1 currency |

### API Usage

- **Model**: DeepSeek Chat
- **Average tokens per section**: 500-900
- **Temperature**: 0.5-0.6 (factual) / 0.7 (creative)
- **Total API calls**: 7 per complete plan

---

## 🐛 Troubleshooting

### Common Issues

**Q: "Please enter a destination!" error**
- A: Make sure you've entered a destination in the sidebar, or select one from the dropdown if CSV is loaded.

**Q: API key error**
- A: Check that your `.env` file exists and contains valid API keys. Restart the app after adding keys.

**Q: City dropdown is empty**
- A: The `cities_geonames_1000.csv` file is missing or has incorrect columns. Use manual text input instead or add the CSV file.

**Q: PDF won't download**
- A: Check browser popup blocker. Try a different browser. Ensure ReportLab is installed (`pip install reportlab`).

**Q: Weather data not showing**
- A: Weather API only works for trips within 5 days. Add `OPENWEATHER_API_KEY` to `.env` file.

**Q: Sections not generating**
- A: Check that checkboxes are enabled in sidebar. Verify API key is valid. Check internet connection.

**Q: HTML tags showing in output**
- A: This has been fixed in v2.0.0. Update to the latest version.

---

## 🔄 Updates & Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version history and updates.

### Latest Version: 2.0.0
- ✅ Added 4 new core features
- ✅ Redesigned UI with pastel theme
- ✅ 50% performance improvement


---

## 💡 Tips for Best Results

### General Tips
- ✨ Be specific with interests for better recommendations
- 📅 Choose realistic travel dates (not too far in future for weather data)
- 👥 Accurate traveler count affects budget calculations
- 🍴 Select dietary restrictions for personalized restaurant suggestions

### Budget Estimates
- Select appropriate travel style (Budget/Moderate/Luxury)
- Review currency exchange rates provided
- Check money-saving tips for discounts

### Packing Lists
- Weather data is most accurate within 5 days of travel
- Laundry availability affects clothing quantities
- Check adapter type carefully for your electronics

### Restaurant Recommendations
- Book ahead based on AI suggestions, especially for upscale dining
- Try recommended food markets for authentic experiences
- Use provided local phrases when ordering

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👨‍💻 Developer

**Hanan Abu Kwaider**

- LinkedIn: [linkedin.com/in/hananabukwaider](https://www.linkedin.com/in/hananabukwaider/)


---

## 🙏 Acknowledgments

- **DeepSeek AI** for the powerful language model
- **Streamlit** for the amazing web framework
- **OpenWeather** for weather data integration
- **ReportLab** for PDF generation capabilities

---

## ⭐ Support

If you find TripMate AI helpful, please consider:
- ⭐ Starring the repository
- 🐛 Reporting bugs
- 💡 Suggesting new features
- 📢 Sharing with friends

---

## 📧 Contact

For questions, feedback, or support:
- Open an issue on GitHub
- Connect on LinkedIn


---

<div align="center">

**Made with ❤️ for travelers worldwide**

[⬆ Back to Top](#tripmate-ai-)

</div>
