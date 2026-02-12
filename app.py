import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from agent import TripMateAgent
import base64
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import re
import os

# Page configuration
st.set_page_config(
    page_title="TripMate AI - Your Smart Travel Assistant",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()



# Function to set background image
def set_background(image_file):
    try:
        with open(image_file, "rb") as f:
            img_data = f.read()
        b64_encoded = base64.b64encode(img_data).decode()
        style = f"""
            <style>
            .stApp {{
                background-image: linear-gradient(rgba(255,255,255,0.85), rgba(255,255,255,0.85)), url("data:image/png;base64,{b64_encoded}");
                background-size: 400px;
                background-repeat: repeat;
                background-attachment: fixed;
            }}
            </style>
        """
        st.markdown(style, unsafe_allow_html=True)
    except:
        pass

# Set background
set_background('background.png')

# Custom CSS with pastel colors and dashed borders
st.markdown("""
<style>
    /* Change Streamlit's default red to pastel blue */
    :root {
        --primary-color: #A8D8EA !important;
        --background-color: #FFFFFF;
        --secondary-background-color: #F7F9FC;
        --text-color: #2D3561;
    }
    
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #6B9AC4;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.3rem;
        text-align: center;
        color: #2D3561;
        font-weight: 600;
        margin-bottom: 2rem;
    }
    
    /* Container for 2-column layout */
    .box-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
        margin: 1rem 0;
    }
    
    /* Base box style - white background with dashed border */
    .info-box {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
    }
    
    /* Individual box styles with pastel dashed borders */
    .budget-box {
        background: white;
        border: 4px dashed #C7B8EA;
        color: #2D3561;
    }
    .packing-box {
        background: white;
        border: 4px dashed #FFB6C1;
        color: #2D3561;
    }
    .itinerary-box {
        background: white;
        border: 4px dashed #A8D8EA;
        color: #2D3561;
    }
    .transport-box {
        background: white;
        border: 4px dashed #B4E7CE;
        color: #2D3561;
    }
    .culture-box {
        background: white;
        border: 4px dashed #FFD4A3;
        color: #2D3561;
    }
    .restaurant-box {
        background: white;
        border: 4px dashed #B8E6E6;
        color: #2D3561;
    }
    .currency-box {
        background: white;
        border: 4px dashed #E6D5F5;
        color: #2D3561;
        grid-column: 1 / -1;
    }
    
    .section-title {
        font-size: 1.6rem;
        font-weight: bold;
        margin-bottom: 1rem;
        color: #2D3561;
    }
    
    /* Remove extra spacing from HTML elements */
    .info-box h4 {
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        color: #2D3561;
        font-weight: 600;
    }
    
    .info-box strong {
        color: #2D3561;
        font-weight: 600;
    }
    
    .info-box ul {
        margin: 0.5rem 0;
        padding-left: 1.5rem;
    }
    
    .info-box li {
        margin: 0.3rem 0;
        line-height: 1.5;
    }
    
    .info-box p {
        margin: 0.5rem 0;
        line-height: 1.6;
    }
    
    /* Button styling with pastel blue */
    .stButton>button {
        width: 100%;
       background: #429dbd !important;
    color: #fff !important
        font-weight: bold;
        padding: 0.75rem;
        border-radius: 10px;
        border: none !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
     
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.15);
    }
    
    /* Download button specific styling */
  .stDownloadButton>button {
    background: #62b5d5 !important;
    color: #fff !important;
    font-weight: bold;
}
    
    /* Sidebar styling with pastel blue gradient */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #D4EBF8 0%, #A8D8EA 100%) !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background-color: transparent;
    }
    
    /* Sidebar text color */
    [data-testid="stSidebar"] .element-container {
        color: #2D3561;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label {
        color: #2D3561 !important;
    }
    
    /* Progress bar color - pastel blue */
    .stProgress > div > div > div > div {
        background-color: #A8D8EA !important;
    }
    
    /* Checkbox styling - pastel blue */
    .stCheckbox > label > div[data-testid="stMarkdownContainer"] > p {
        color: #2D3561;
    }
    
    input[type="checkbox"] {
        accent-color: #2d3561 !important;
    }
    
    /* Radio button styling - pastel blue */
    input[type="radio"] {
        accent-color: #A8D8EA !important;
    }
    
    /* Select slider (travel style) - pastel blue */
    .stSlider > div > div > div > div {
        background-color: #fff !important;
    }
    
    .stSlider > div > div > div {
         background-color: #fff !important;
            # background: linear-gradient(to right, #2d3561 0%, #2d3561 50%, rgba(151, 166, 195, 0.25) 50%, rgba(151, 166, 195, 0.25) 100%);
    }

    .st-emotion-cache-jigjfz
    {    
        color: rgb(67 109 155);
    }
    /* Slider thumb */
    .stSlider [role="slider"] {
        background-color: #62b5d5 !important;
    }
    /* Checkbox box: unchecked = white, checked = #2d3561 */
    .stCheckbox label[data-baseweb="checkbox"] > span {
        background-color: #fff !important;
        border: 1px solid #2d3561 !important;
    }
    .stCheckbox label[data-baseweb="checkbox"]:has(input:checked) > span {
        background-color: #2d3561 !important;
        border-color: #2d3561 !important;
    }
    .st-emotion-cache-99anic:hover:enabled, .st-emotion-cache-99anic:focus:enabled
            {
             background-color: #2d3561;
            }
    /* Multi-select styling */
    .stMultiSelect > div > div {
        background-color: white;
            border-radius: 8px;
    }
    
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #A8D8EA !important;
        color: #2D3561 !important;
    }
    
    /* Selectbox and input styling in sidebar */
    [data-testid="stSidebar"] .stSelectbox > div > div,
    [data-testid="stSidebar"] .stTextInput > div > div,
    [data-testid="stSidebar"] .stDateInput > div > div,
    [data-testid="stSidebar"] .stMultiSelect > div > div {
        background-color: white;
    }
    
    /* Number input styling */
    [data-testid="stSidebar"] .stNumberInput > div > div {
        background-color: white;
    }
     .logo-wrap {
        display: flex;
        justify-content: center;
    }

    .logo-wrap img {
        display: block;
        width: 240px;
        max-width: 240px;
    }
            
    @media (max-width: 768px) {
        .logo-wrap img {
            width: 190px !important;
            max-width: 190px !important;
        }
    }

    .app-footer {
    position: fixed;           /* Stays at bottom */
    bottom: 0;
    left: 0;
    width: 100%;
    background: linear-gradient(90deg, #D4EBF8 0%, #A8D8EA 100%);
    padding: 1rem;
    text-align: center;
    color: #2D3561;
    box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
    z-index: 999;              /* Always on top */
}

</style>
""", unsafe_allow_html=True)

def load_cities():
    """Load cities data from CSV with City, Country format."""
    try:
        df = pd.read_csv('cities_geonames_1000.csv')
        
        if 'csv_loaded' not in st.session_state:
            st.session_state.csv_loaded = True
            # print(f"CSV columns: {df.columns.tolist()}")
        
        # Find city name column
        city_col = None
        for col in ['name', 'city', 'city_name', 'geoname', 'asciiname']:
            if col in df.columns:
                city_col = col
                break
        
        if city_col is None:
            city_col = df.columns[0]
        
        # Find country column
        country_col = None
        for col in ['country', 'country_name', 'country_code', 'countrycode', 'iso2', 'cc']:
            if col in df.columns:
                country_col = col
                break
        
        # Create display names
        if country_col:
            df['display_name'] = df[city_col].astype(str) + ', ' + df[country_col].astype(str)
            city_mapping = dict(zip(df['display_name'], df[city_col]))
        else:
            df['display_name'] = df[city_col].astype(str)
            city_mapping = dict(zip(df['display_name'], df[city_col]))
        
        display_names = df['display_name'].dropna().unique().tolist()
        display_names_sorted = sorted(display_names)
        
        return display_names_sorted, city_mapping
        
    except FileNotFoundError:
        # No default cities - return empty
        return [], {}
    except Exception as e:
        print(f"Error loading cities: {str(e)}")
        return [], {}

def clean_html_output(text):
    """Clean up HTML output properly - convert markdown to HTML."""
    if not text:
        return ""
    
    text = text.strip()
    # Prevent Streamlit/KaTeX from interpreting currency amounts as math
    text = text.replace('$', '__DOLLAR__')
    
    # CRITICAL FIRST: Unescape HTML entities (&lt; becomes <, &gt; becomes >)
    text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
    text = text.replace('&#60;', '<').replace('&#62;', '>').replace('&#38;', '&')

    # Strip fenced code blocks, inline backticks, and HTML code wrappers
    text = re.sub(r'```[a-zA-Z0-9_-]*\n?', '', text)
    text = text.replace('```', '')
    text = text.replace('`', '')
    text = re.sub(r'</?pre[^>]*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</?code[^>]*>', '', text, flags=re.IGNORECASE)
    
    # If text contains literal "<h4>" strings, we need to remove them completely
    # This is a nuclear option for stubborn cases
    if '<h4>' in text.lower():
        # Remove all h4 tags and their content, replacing with markdown
        text = re.sub(r'<h4[^>]*>(.*?)</h4>', r'**\1**', text, flags=re.IGNORECASE | re.DOTALL)
        # Also catch any orphaned tags
        text = text.replace('<h4>', '').replace('</h4>', '')
        text = text.replace('<H4>', '').replace('</H4>', '')
    
    # First pass: Strip ALL HTML tags and convert to plain text with markdown
    # This prevents double-encoding issues
    text = re.sub(r'<h4[^>]*>(.*?)</h4>', r'**\1**', text, flags=re.IGNORECASE)
    text = re.sub(r'<h3[^>]*>(.*?)</h3>', r'**\1**', text, flags=re.IGNORECASE)
    text = re.sub(r'<h2[^>]*>(.*?)</h2>', r'**\1**', text, flags=re.IGNORECASE)
    text = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', text, flags=re.IGNORECASE)
    text = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', text, flags=re.IGNORECASE)
    text = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', text, flags=re.IGNORECASE)
    text = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', text, flags=re.IGNORECASE)
    
    # Remove any remaining stray HTML tags
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<p[^>]*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</p>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<ul[^>]*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</ul>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<li[^>]*>', '• ', text, flags=re.IGNORECASE)
    text = re.sub(r'</li>', '\n', text, flags=re.IGNORECASE)
    
    # CATCH-ALL: Remove any other HTML tags that might remain
    text = re.sub(r'<[^>]+>', '', text)
    
    # Now process clean markdown into proper HTML
    lines = text.split('\n')
    result_lines = []
    in_list = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check for bold markers with headers (these become h4)
        if line.startswith('**') and line.endswith('**') and len(line) > 4:
            header_text = line.strip('*').strip()
            if in_list:
                result_lines.append('</ul>')
                in_list = False
            result_lines.append(f'<h4>{header_text}</h4>')
        
        # Check for bullet points
        elif line.startswith('•') or line.startswith('-'):
            if not in_list:
                result_lines.append('<ul>')
                in_list = True
            item_text = line[1:].strip()
            # Remove any remaining ** markers
            item_text = item_text.replace('**', '')
            result_lines.append(f'<li>{item_text}</li>')
        
        # Regular paragraph
        else:
            if in_list:
                result_lines.append('</ul>')
                in_list = False
            # Convert ** to strong tags
            line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
            result_lines.append(f'<p>{line}</p>')
    
    if in_list:
        result_lines.append('</ul>')
    
    html_output = '\n'.join(result_lines)
    
    # Final cleanup: unescape any HTML entities that might have been created
    import html as html_module
    html_output = html_module.unescape(html_output)
    html_output = html_output.replace('__DOLLAR__', '&#36;')
    
    # Final check for any literal h4 tags that escaped earlier processing
    # Keep this strictly scoped to a single element to avoid clipping content
    if '<h4>' in html_output and not html_output.startswith('<h4>'):
        html_output = re.sub(r'<p>[^<]*?<h4>(.*?)</h4>[^<]*?</p>', r'<p><strong>\1</strong></p>', html_output, flags=re.IGNORECASE)
        html_output = re.sub(r'<li>[^<]*?<h4>(.*?)</h4>[^<]*?</li>', r'<li><strong>\1</strong></li>', html_output, flags=re.IGNORECASE)

    return html_output

def create_pdf(content_dict, destination, dates):
    """Create a compact PDF without page breaks between sections."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    def _strip_emoji(text: str) -> str:
        if not text:
            return ""
        # Keep ASCII only to avoid broken glyphs in PDF
        return "".join(ch for ch in text if ord(ch) < 128)

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#6B9AC4',
        spaceAfter=6,
        alignment=TA_CENTER
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor='#2D3561',
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='#2D3561',
        spaceAfter=10,
        spaceBefore=16
    )
    
    # Style for bold category headers (like CLOTHING, ELECTRONICS)
    category_style = ParagraphStyle(
        'CategoryHeader',
        parent=styles['Normal'],
        fontSize=11,
        textColor='#2D3561',
        fontName='Helvetica-Bold',
        spaceAfter=6,
        spaceBefore=10
    )
    
    # Style for subheadings (like "Food Markets:", "Key Tips:", "Day 1:")
    subheading_style = ParagraphStyle(
        'Subheading',
        parent=styles['Normal'],
        fontSize=10,
        textColor='#2D3561',
        fontName='Helvetica-Bold',
        spaceAfter=6,
        spaceBefore=10
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=10,
        leading=14
    )
    
    story = []
    
    # Title and dates
    story.append(Paragraph(_strip_emoji(f"TripMate AI - {destination}"), title_style))
    story.append(Spacer(1, 0.08*inch))
    story.append(Paragraph(_strip_emoji(f"{dates}"), subtitle_style))
    
    # Add each section WITHOUT page breaks
    for section_title, content in content_dict.items():
        if content:
            # Add spacing between sections instead of page break
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph(_strip_emoji(section_title), heading_style))
            story.append(Spacer(1, 0.14*inch))
            
            # Split content into lines
            lines = content.split('\n')
            for line in lines:
                line = _strip_emoji(line.strip())
                if not line:
                    continue
                
                # Check if line is a category header (starts and ends with **)
                if line.startswith('**') and line.endswith('**'):
                    # This is a category header - make it bold with spacing
                    category_text = line.strip('*').strip()
                    story.append(Spacer(1, 0.08*inch))  # Space before category
                    story.append(Paragraph(category_text, category_style))
                    story.append(Spacer(1, 0.04*inch))
                
                # Day headings (add extra spacing between days)
                elif line.startswith('Day ') and len(line) < 80:
                    subheading_text = line.replace('**', '')
                    story.append(Spacer(1, 0.16*inch))
                    story.append(Paragraph(subheading_text, subheading_style))
                    story.append(Spacer(1, 0.06*inch))
                
                # Check if line is a subheading (ends with : and is short)
                elif line.endswith(':') and len(line) < 80:
                    subheading_text = line.replace('**', '')
                    story.append(Spacer(1, 0.06*inch))  # Space before subheading
                    story.append(Paragraph(subheading_text, subheading_style))
                    story.append(Spacer(1, 0.04*inch))
                
                # Check if line is a bullet point
                elif line.startswith('•') or line.startswith('-'):
                    # Regular bullet point
                    bullet_text = line[1:].strip()
                    # Remove any remaining ** markers
                    bullet_text = bullet_text.replace('**', '')
                    # Convert any remaining markdown to HTML bold
                    bullet_text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', bullet_text)
                    try:
                        story.append(Paragraph(f"  • {bullet_text}", body_style))
                        story.append(Spacer(1, 0.04*inch))
                    except:
                        continue
                
                # Regular paragraph with bold text
                else:
                    # Convert ** to <b> tags for PDF
                    para_text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', line)
                    try:
                        story.append(Paragraph(para_text, body_style))
                        story.append(Spacer(1, 0.05*inch))
                    except:
                        continue
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def main():
    # Display logo if exists
    if os.path.exists("logo.png"):
        logo_b64 = get_base64_of_bin_file("logo.png")
        st.markdown(
            f"<div class='logo-wrap'><img src='data:image/png;base64,{logo_b64}' alt='TripMate logo'></div>",
            unsafe_allow_html=True,
        )
    
    # Header
   
    st.markdown('<div class="sub-header">Your AI-Powered Travel Planning Assistant</div>', 
                unsafe_allow_html=True)
    
    # Initialize agent
    agent = TripMateAgent()
    
    # Initialize session state
    if 'generated_content' not in st.session_state:
        st.session_state.generated_content = {}
    if 'pdf_content' not in st.session_state:
        st.session_state.pdf_content = {}
    if 'trip_info' not in st.session_state:
        st.session_state.trip_info = {}
    
    # Sidebar
    with st.sidebar:
        st.header("Trip Details")
        
        # Load cities
        city_options, city_mapping = load_cities()
        
        # Destination input
        if city_options and city_mapping:
            destination_display = st.selectbox(
                "Destination",
                options=city_options,
                index=None,
                placeholder="Choose an option",
                help="Select your destination city"
            )
            if destination_display:
                destination = city_mapping.get(destination_display, destination_display.split(',')[0].strip())
            else:
                destination = None
        else:
            # No CSV or empty - require manual input
            destination_display = st.text_input("Destination (City, Country)", 
                                               placeholder="e.g., Paris, France",
                                               help="Enter destination in 'City, Country' format")
            if destination_display:
                destination = destination_display.split(',')[0].strip()
            else:
                destination = None
        
        # Date inputs
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime.now() + timedelta(days=7),
                min_value=datetime.now()
            )
        with col2:
            end_date = st.date_input(
                "End Date",
                value=datetime.now() + timedelta(days=14),
                min_value=start_date
            )
        
        st.markdown("---")
        
        # Travel preferences
        st.header("Preferences")
        
        travel_style = st.select_slider(
            "Travel Style",
            options=["Budget", "Moderate", "Luxury"],
            value="Moderate"
        )
        
        num_travelers = st.number_input(
            "Number of Travelers",
            min_value=1,
            max_value=10,
            value=1
        )
        
        interests = st.multiselect(
            "Interests",
            ["Sightseeing", "Food & Dining", "Adventure", "Culture", "Nightlife", 
             "Shopping", "Nature", "Relaxation"],
            default=["Sightseeing", "Food & Dining"]
        )
        
        # Dietary restrictions
        st.subheader("Dietary Preferences")
        dietary_restrictions = st.multiselect(
            "Select any dietary restrictions",
            ["Vegetarian", "Vegan", "Halal", "Kosher", "Gluten-Free", 
             "Dairy-Free", "Nut Allergies"],
            default=[]
        )
        
        st.markdown("---")
        
        # Feature selection
        st.header("What to Generate")
        generate_budget = st.checkbox("💰 Budget Estimate", value=True)
        generate_packing = st.checkbox("🎒 Packing List", value=True)
        generate_itinerary = st.checkbox("📅 Itinerary", value=True)
        generate_transport = st.checkbox("🚇 Transport Guide", value=True)
        generate_culture = st.checkbox("🌍 Cultural Tips", value=True)
        generate_restaurants = st.checkbox("🍴 Restaurant Guide", value=True)
        
        st.markdown("---")
        
        # Generate button
        generate_button = st.button("🚀 Generate Travel Plan", type="primary")
    
    # Main content area
    if generate_button:
        # Validate inputs
        if not destination:
            st.error("Please enter a destination!")
            return
            
        if end_date < start_date:
            st.error("End date must be after start date!")
            return
        
        # Format dates
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        date_range = f"{start_str} to {end_str}"
        
        interest_str = ", ".join(interests) if interests else "general sightseeing"
        
        # Clear previous content
        st.session_state.generated_content = {}
        st.session_state.pdf_content = {}
        st.session_state.trip_info = {
            'destination': destination_display if 'destination_display' in locals() else destination,
            'destination_city': destination,
            'dates': date_range,
            'dietary': dietary_restrictions
        }
        
        # Progress tracking
        total_tasks = sum([generate_budget, generate_packing, generate_itinerary, 
                          generate_transport, generate_culture, generate_restaurants])
        current_task = 0
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Generate sections
        if generate_budget:
            current_task += 1
            status_text.text(f"💰 Generating budget estimate... ({current_task}/{total_tasks})")
            progress_bar.progress(current_task / total_tasks)
            
            with st.spinner("Creating budget breakdown..."):
                budget_data = agent.estimate_budget(
                    destination, start_str, end_str, 
                    travel_style.lower(), num_travelers
                )
            st.session_state.generated_content['budget'] = budget_data['budget_text']
            st.session_state.pdf_content['Budget Estimate'] = budget_data['budget_text']
        
        if generate_packing:
            current_task += 1
            status_text.text(f"🎒 Generating packing list... ({current_task}/{total_tasks})")
            progress_bar.progress(current_task / total_tasks)
            
            with st.spinner("Creating your packing list..."):
                packing_list = agent.generate_packing_list(
                    destination, start_str, end_str, travel_style.lower()
                )
            st.session_state.generated_content['packing'] = packing_list
            st.session_state.pdf_content['Packing List'] = packing_list
        
        if generate_itinerary:
            current_task += 1
            status_text.text(f"📅 Generating itinerary... ({current_task}/{total_tasks})")
            progress_bar.progress(current_task / total_tasks)
            
            with st.spinner("Planning your itinerary..."):
                itinerary = agent.generate_itinerary(
                    destination, start_str, end_str, interest_str
                )
            st.session_state.generated_content['itinerary'] = itinerary
            st.session_state.pdf_content['Itinerary'] = itinerary
        
        if generate_transport:
            current_task += 1
            status_text.text(f"🚇 Generating transport guide... ({current_task}/{total_tasks})")
            progress_bar.progress(current_task / total_tasks)
            
            with st.spinner("Mapping out transportation..."):
                transport_guide = agent.get_public_transport_guide(destination)
            st.session_state.generated_content['transport'] = transport_guide
            st.session_state.pdf_content['Public Transportation'] = transport_guide
        
        if generate_culture:
            current_task += 1
            status_text.text(f"🌍 Generating cultural tips... ({current_task}/{total_tasks})")
            progress_bar.progress(current_task / total_tasks)
            
            with st.spinner("Learning local customs..."):
                cultural_tips = agent.get_cultural_tips(destination)
            st.session_state.generated_content['culture'] = cultural_tips
            st.session_state.pdf_content['Cultural Tips'] = cultural_tips
        
        if generate_restaurants:
            current_task += 1
            status_text.text(f"🍴 Finding best restaurants... ({current_task}/{total_tasks})")
            progress_bar.progress(current_task / total_tasks)
            
            with st.spinner("Discovering dining spots..."):
                restaurant_guide = agent.get_restaurant_recommendations(
                    destination, 
                    dietary_restrictions if dietary_restrictions else None,
                    "all",
                    travel_style.lower()
                )
            st.session_state.generated_content['restaurants'] = restaurant_guide
            st.session_state.pdf_content['Restaurant Guide'] = restaurant_guide
        
        # Currency info
        with st.spinner("Getting currency information..."):
            currency_info = agent.get_currency_info(destination)
        st.session_state.generated_content['currency'] = currency_info
        st.session_state.pdf_content['Currency Information'] = currency_info
        
        progress_bar.progress(1.0)
        status_text.text("✅ All sections generated successfully!")
    
    # Display content
    if st.session_state.generated_content:
        
        st.markdown('<div class="box-container">', unsafe_allow_html=True)
        
        if 'budget' in st.session_state.generated_content:
            budget_html = clean_html_output(st.session_state.generated_content['budget'])
            st.markdown(f'''
            <div class="info-box budget-box">
                <div class="section-title">💰 Budget Estimate</div>
                {budget_html}
            </div>
            ''', unsafe_allow_html=True)
        
        if 'packing' in st.session_state.generated_content:
            packing_html = clean_html_output(st.session_state.generated_content['packing'])
            st.markdown(f'''
            <div class="info-box packing-box">
                <div class="section-title">🎒 Packing List</div>
                {packing_html}
            </div>
            ''', unsafe_allow_html=True)
        
        if 'itinerary' in st.session_state.generated_content:
            itinerary_html = clean_html_output(st.session_state.generated_content['itinerary'])
            st.markdown(f'''
            <div class="info-box itinerary-box">
                <div class="section-title">📅 Your Itinerary</div>
                {itinerary_html}
            </div>
            ''', unsafe_allow_html=True)
        
        if 'transport' in st.session_state.generated_content:
            transport_html = clean_html_output(st.session_state.generated_content['transport'])
            st.markdown(f'''
            <div class="info-box transport-box">
                <div class="section-title">🚇 Public Transportation</div>
                {transport_html}
            </div>
            ''', unsafe_allow_html=True)
        
        if 'culture' in st.session_state.generated_content:
            culture_html = clean_html_output(st.session_state.generated_content['culture'])
            st.markdown(f'''
            <div class="info-box culture-box">
                <div class="section-title">🌍 Cultural Tips</div>
                {culture_html}
            </div>
            ''', unsafe_allow_html=True)
        
        if 'restaurants' in st.session_state.generated_content:
            dietary_note = f"<p><em>🥗 Filtered for: {', '.join(st.session_state.trip_info['dietary'])}</em></p>" if st.session_state.trip_info.get('dietary') else ""
            restaurant_html = clean_html_output(st.session_state.generated_content['restaurants'])
            restaurant_html = restaurant_html.lstrip()
            
            # Use st.components.html for better HTML rendering
            full_html = (
                f'<div class="info-box restaurant-box">'
                f'<div class="section-title">🍴 Where to Eat</div>'
                f'{dietary_note}'
                f'{restaurant_html}'
                f'</div>'
            )
            st.markdown(full_html, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Currency box - only show if has content
        if 'currency' in st.session_state.generated_content:
            currency_html = clean_html_output(st.session_state.generated_content['currency'])
            if currency_html.strip():  # Only show if not empty
                st.markdown(f'''
                <div class="info-box currency-box">
                    <div class="section-title">💱 Currency & Payments</div>
                    {currency_html}
                </div>
                ''', unsafe_allow_html=True)
        
        # PDF Download - using st.container to wrap everything properly
        with st.container():
            st.markdown('<div class="download-section">', unsafe_allow_html=True)
            st.markdown('<h3 style="color: #2D3561; margin-bottom: 1rem;">📥 Download Your Travel Plan</h3>', unsafe_allow_html=True)
            
            pdf_buffer = create_pdf(
                st.session_state.pdf_content, 
                st.session_state.trip_info['destination'],
                st.session_state.trip_info['dates']
            )
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.download_button(
                    label="Download Complete Travel Plan (PDF)",
                    data=pdf_buffer,
                    file_name=f"TripMate_{st.session_state.trip_info['destination_city'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            
            st.success(f"🎉 Your complete travel plan for **{st.session_state.trip_info['destination']}** is ready!")
            st.markdown('</div>', unsafe_allow_html=True)
        
    else:
        # Welcome screen
        st.markdown("""
        ## Welcome to TripMate AI! 👋
        
        Your intelligent travel companion that helps you plan the perfect trip with:
        
        - 💰 **Budget Estimation** - Know your costs upfront with local currency info
        - 🎒 **Smart Packing Lists** - Never forget the essentials
        - 📅 **Personalized Itineraries** - Day-by-day activity planning
        - 🚇 **Public Transport Guides** - Navigate like a local
        - 🌍 **Cultural Tips** - Respect local customs
        - 🍴 **Restaurant Recommendations** - Find great food with dietary filters
        
        ### How to Get Started:
        1. 📍 Enter your destination in the sidebar
        2. 📅 Set your travel dates
        3. ⚙️ Customize your preferences
        4. ✅ Select which sections to generate
        5. 🚀 Click "Generate Travel Plan"
        
        **Ready? Fill in the sidebar and let's plan your adventure! →**
        """)

        st.markdown(
            "<div class='app-footer'>"
            "Developed by <a href='https://www.linkedin.com/in/hananabukwaider/' target='_blank'>"
            "Hanan Abu Kwaider</a>"
            "</div>",
            unsafe_allow_html=True,
        )

if __name__ == "__main__":
    main()
