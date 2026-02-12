# Changelog

All notable changes to TripMate AI are documented in this file.

## [2.0.0] - 2024-02-08

### 🎉 Major Feature Additions

#### New Core Features
- **Budget Estimator** 💰
  - Detailed breakdown: accommodation, food, transport, activities, miscellaneous
  - Multi-traveler calculations
  - Travel style adjustment (Budget/Moderate/Luxury)
  - Currency information with exchange rates
  - Money-saving tips

- **Public Transportation Guide** 🚇
  - Metro/subway/bus/tram system details
  - Ticket purchasing information
  - Operating hours and passes
  - Airport connections
  - Tourist-specific navigation tips

- **Cultural Tips & Etiquette** 🌍
  - Local greetings and customs
  - Dress code recommendations
  - Dining etiquette
  - Essential local phrases (10+)
  - Do's and Don'ts (5-7 each)
  - Religious sensitivity guidelines

- **Restaurant Recommendations with Dietary Filters** 🍴
  - 7 dietary options: Vegetarian, Vegan, Halal, Kosher, Gluten-Free, Dairy-Free, Nut Allergies
  - Budget/mid-range/upscale categories
  - Must-try local dishes
  - Food markets and street food recommendations
  - Dining tips and reservation advice

### 🎨 UI/UX Enhancements

#### Design & Styling
- **Pastel Color Scheme**
  - Changed all Streamlit red elements to pastel blue (#A8D8EA)
  - Pastel blue gradient sidebar (#D4EBF8 → #A8D8EA)
  - Consistent pastel colors across all components

- **2-Column Grid Layout**
  - Responsive grid display for generated sections
  - White boxes with colorful dashed borders
  - Professional, modern appearance

### 🚀 Performance Improvements

#### Content Optimization
- **50% Output Reduction**
  - Optimized token limits per section
  - Concise prompts with clear instructions
  - Temperature lowered to 0.5-0.6 for factual sections
  - Result: ~3500 tokens vs ~7000 previously

- **API Cost Reduction**
  - 50% reduction in token usage
  - Cost per plan: ~$0.01 (down from ~$0.02)
  - Faster generation time: 2-3 min (down from 3-5 min)

### 🐛 Bug Fixes

- Fixed HTML tags showing as raw text
- Fixed empty currency box
- Fixed download section positioning
- Fixed broken `<br>` tags
- Fixed PDF formatting for headers
- Fixed CSS conflicts with Streamlit defaults

### 📊 Metrics

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Output length | ~3000 words | ~1500 words | 50% |
| Generation time | 3-5 min | 2-3 min | 40% |
| API tokens | ~7000 | ~3500 | 50% |
| Cost per plan | ~$0.02 | ~$0.01 | 50% |

---

## [1.0.0] - Initial Release

### Features
- Basic travel planning functionality
- Packing list generation
- Itinerary creation
- Weather integration
- PDF export

---

*For detailed setup instructions, see [README.md](README.md)*
