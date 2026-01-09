import streamlit as st
import os
import base64
import html
import re
import pandas as pd
from fpdf import FPDF
from agent import run_advisor, get_itinerary
from datetime import date as dt_date
from streamlit_extras.stylable_container import stylable_container

# --- 1. CONFIG & CUSTOM STYLING ---
st.set_page_config(page_title="TripMate AI", page_icon="🌏", layout="centered")

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def add_custom_styles():
    bg_file = "background.png" if os.path.exists("background.png") else "background.jpg" if os.path.exists("background.jpg") else None
    if bg_file:
        bin_str = get_base64_of_bin_file(bg_file)
        bg_image_css = f"""
            background-image: linear-gradient(rgba(255,255,255,0.85), rgba(255,255,255,0.85)), url("data:image/png;base64,{bin_str}");
            background-size: 400px;
            background-repeat: repeat;
            background-attachment: fixed;
        """
    else:
        bg_image_css = "background-color: #fefefe;"

    st.markdown(f"""
    <style>
    :root, html, body {{
        color-scheme: light;
    }}

    .stApp {{
        {bg_image_css}
        display: flex;
        flex-direction: column;
        min-height: 100vh;
    }}

    .stApp > .main {{
        flex: 1;
        display: flex;
        flex-direction: column;
    }}

    .block-container {{
        flex: 1;
        display: flex;
        flex-direction: column;
        min-height: 100vh;
    }}
    
    .stMarkdownContainer, .stForm {{
        background-color: rgba(255, 255, 255, 0.92);
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
    }}

    /* FIX NUMBER INPUT (+/-) BUTTONS */
    div[data-testid="stNumberInput"] button {{
        border-color: transparent !important;
        background-color: transparent !important;
    }}
    
    div[data-testid="stNumberInput"] button:hover {{
        border-color: #2a9d8f !important;
        color: #2a9d8f !important;
    }}

    div[data-testid="stNumberInput"] button:active, 
    div[data-testid="stNumberInput"] button:focus {{
        background-color: #2a9d8f !important;
        color: white !important;
        border-color: #2a9d8f !important;
        box-shadow: none !important;
    }}

    input:focus {{
        border-color: #2a9d8f !important;
        box-shadow: none !important;
    }}

    /* Center Download Button */
    div.stDownloadButton {{
        display: flex;
        justify-content: center;
        margin-top: 16px;
    }}

    .css-15zrgzn {{display: none}}

    .result-grid {{
        display: grid;
        grid-template-columns: repeat(2, minmax(260px, 1fr));
        gap: 24px;
        margin-top: 12px;
        position: relative;
    }}

    @media (max-width: 768px) {{
        .result-grid {{
            grid-template-columns: 1fr;
        }}
    }}

    .result-card {{
        background: #ffffff;
        border: 3px dashed var(--card-color, #f2c4c4);
        border-radius: 18px;
        padding: 18px 20px;
        box-shadow: 0 8px 18px rgba(0,0,0,0.08);
        position: relative;
    }}

    .result-card-title {{
        font-weight: 700;
        font-size: 1.05rem;
        margin-bottom: 10px;
        color: #264653;
    }}

    .result-card p {{
        margin: 0 0 10px 0;
        color: #374151;
        line-height: 1.5;
    }}

    .result-card ul {{
        margin: 0 0 10px 20px;
        padding: 0;
        color: #374151;
        line-height: 1.5;
    }}

    .result-card.with-connector::after {{
        content: "";
        position: absolute;
        left: 50%;
        bottom: -52px;
        width: 52px;
        height: 52px;
        border-left: 3px dashed var(--card-color, #f2c4c4);
        border-bottom: 3px dashed var(--card-color, #f2c4c4);
        border-bottom-left-radius: 50px;
        transform: translateX(-50%) rotate(-20deg);
    }}

    .result-card.with-top-connector::before {{
        content: "";
        position: absolute;
        left: 50%;
        top: -22px;
        width: 0;
        height: 22px;
        border-left: 3px dashed var(--card-color, #f2c4c4);
        transform: translateX(-50%);
    }}

    .app-footer {{
        margin-top: auto;
        text-align: center;
        color: #888;
        padding: 16px 0 10px;
    }}
    </style>
    """, unsafe_allow_html=True)

add_custom_styles()

PASTEL_COLORS = [
    "#f2c4c4",
    "#bfe1dd",
    "#f6e1a6",
    "#c9d8ff",
    "#dcc9f2",
    "#cfe8b4",
]

CITIES_CSV_PATH = "cities_geonames_1000.csv"  # same folder as app.py

@st.cache_data(show_spinner=False)
def load_city_options(path: str) -> list[str]:
    df = pd.read_csv(
        path,
        usecols=["city_name", "country_name"],
        dtype={"city_name": "string", "country_name": "string"},
    ).dropna()

    labels = (df["city_name"].str.strip() + ", " + df["country_name"].str.strip())
    # remove duplicates, keep stable ordering
    labels = labels.drop_duplicates().tolist()
    return labels


def _format_markdown_to_html(text):
    safe = html.escape(text)
    safe = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", safe)
    safe = re.sub(r"^[-•]\s*$", "", safe, flags=re.MULTILINE)
    lines = safe.splitlines()
    has_list = any(line.strip().startswith(("-", "•")) for line in lines)
    if not has_list:
        joined = " ".join(line.strip() for line in lines if line.strip())
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", joined) if s.strip()]
        if len(sentences) > 1:
            return "<ul>" + "".join(f"<li>{s}</li>" for s in sentences) + "</ul>"
    out = []
    in_list = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append("<br>")
            continue
        if stripped.startswith(("-", "•")):
            bullet_text = stripped[1:].strip()
            if not bullet_text:
                continue
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{bullet_text}</li>")
        else:
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<p>{stripped}</p>")
    if in_list:
        out.append("</ul>")
    return "\n".join(out)

def _split_by_bold_sections(text):
    parts = re.split(r"\*\*(.+?)\*\*", text)
    sections = []
    if len(parts) < 3:
        return [("Details", text.strip())]
    for i in range(1, len(parts), 2):
        title = parts[i].strip()
        content = parts[i + 1].strip() if i + 1 < len(parts) else ""
        if title or content:
            sections.append((title or "Details", content))
    return sections or [("Details", text.strip())]

def _split_packing_by_headings(text):
    heading_pattern = re.compile(
        r"^(?:\*\*)?\s*(?:🌤️|🎒|🧳|💡|💱)?\s*(Weather Analysis|Weather|Packing Strategy|Packing|Logistics Alert|Local Tips|Currency)\s*:?\s*(?:\*\*)?$",
        re.IGNORECASE,
    )
    sections = []
    current_title = None
    buffer = []
    for line in text.splitlines():
        raw = line.strip()
        match = heading_pattern.match(raw)
        if match:
            if current_title:
                sections.append((current_title, "\n".join(buffer).strip()))
            heading_text = raw.strip("*").strip()
            if not any(ch in heading_text for ch in ["🌤️", "🎒", "💡", "💱"]):
                label = match.group(1).lower()
                if label.startswith("weather"):
                    heading_text = "🌤️ Weather Analysis"
                elif label.startswith("packing"):
                    heading_text = "🎒 Packing Strategy"
                elif label.startswith("logistics"):
                    heading_text = "🧳 Logistics Alert"
                elif label.startswith("local"):
                    heading_text = "💡 Local Tips"
                else:
                    heading_text = "💱 Currency"
            current_title = heading_text
            buffer = []
        else:
            buffer.append(line)
    if current_title:
        sections.append((current_title, "\n".join(buffer).strip()))
    if not sections:
        return _split_by_bold_sections(text)
    return sections

def _split_itinerary_sections(text):
    sections = []
    current_title = None
    buffer = []
    for line in text.splitlines():
        stripped = line.strip().strip("*")
        normalized = re.sub(r"^[#\s]+", "", stripped)
        if re.match(r"^(Day\s+\d+.*|Money Intel.*)$", normalized, re.IGNORECASE):
            if current_title:
                sections.append((current_title, "\n".join(buffer).strip()))
            if re.match(r"^Money Intel.*$", normalized, re.IGNORECASE):
                current_title = "💱 Currency"
            else:
                current_title = normalized
            buffer = []
        else:
            buffer.append(line)
    if current_title:
        sections.append((current_title, "\n".join(buffer).strip()))
    if not sections:
        return [("Itinerary", text.strip())]
    return sections

def render_result_cards(title, sections):
    has_content = any(section[1].strip() for section in sections)
    if not has_content:
        sections = [("Output", "(No content returned. Please try again.)")]
    cards = ['<div class="result-grid">']
    total = len(sections)
    for idx, (section_title, content) in enumerate(sections):
        color = PASTEL_COLORS[idx % len(PASTEL_COLORS)]
        connector_class = ""
        if idx < total - 1:
            connector_class += " with-connector"
        if idx > 0:
            connector_class += " with-top-connector"
        cards.append(
            f'<div class="result-card{connector_class}" style="--card-color: {color};">'
            f'<div class="result-card-title">{html.escape(section_title)}</div>'
            f'{_format_markdown_to_html(content)}'
            "</div>"
        )
    cards.append("</div>")
    st.markdown("\n".join(cards), unsafe_allow_html=True)

def render_section_header(title, pdf_data=None, filename=None):
    left, right = st.columns([4, 1])
    with left:
        st.markdown(f"### {title}")
    if pdf_data and filename:
        with right:
            with stylable_container(
                key=f"dl_{title.replace(' ', '_').lower()}",
                css_styles="""
                    button {
                        background-color: #cfe8ff !important;
                        color: #264653 !important;
                        width: 160px !important;
                        border-radius: 10px !important;
                        border: 2px solid #b6d8fb !important;
                        font-weight: 700 !important;
                    }
                """
            ):
                st.download_button("📄 Download", pdf_data, filename)

# --- 2. PDF GENERATION ---
class TripMatePDF(FPDF):
    def header(self):
        if os.path.exists("logo.png"):
            self.image("logo.png", 85, 10, 40)
            self.ln(35) 
        

def create_pdf(destination, text_content, title="Travel Plan"):
    pdf = TripMatePDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    # Preserve section headings by translating **Heading** to bold lines.
    safe_text = text_content.replace("## ", "").encode("latin-1", "ignore").decode("latin-1")
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, f"{title}: {destination}", ln=True)
    pdf.ln(5)
    pdf.set_font("Helvetica", size=11)
    def _split_long_word(word, max_width):
        chunks = []
        chunk = ""
        for ch in word:
            if pdf.get_string_width(chunk + ch) <= max_width:
                chunk += ch
            else:
                if chunk:
                    chunks.append(chunk)
                chunk = ch
        if chunk:
            chunks.append(chunk)
        return chunks

    def _wrap_text_for_pdf(line, first_prefix="", next_prefix=""):
        max_width = pdf.w - pdf.l_margin - pdf.r_margin
        first_width = max_width - pdf.get_string_width(first_prefix)
        next_width = max_width - pdf.get_string_width(next_prefix)
        if not line:
            return [""]
        words = line.split()
        lines = []
        current = ""
        current_width = first_width
        for word in words:
            candidate = f"{current} {word}".strip()
            if pdf.get_string_width(candidate) <= current_width:
                current = candidate
                continue
            if current:
                lines.append(current)
                current = ""
                current_width = next_width
            if pdf.get_string_width(word) <= current_width:
                current = word
            else:
                parts = _split_long_word(word, current_width)
                if parts:
                    current = parts.pop()
                    lines.extend(parts)
                    current_width = next_width
        if current:
            lines.append(current)
        return lines

    def _write_wrapped(text, first_prefix="", next_prefix=""):
        wrapped_lines = _wrap_text_for_pdf(text, first_prefix, next_prefix)
        for i, wrapped in enumerate(wrapped_lines):
            prefix = first_prefix if i == 0 else next_prefix
            if wrapped:
                pdf.cell(0, 7, f"{prefix}{wrapped}", ln=1)
            else:
                pdf.ln(7)

    def _write_bullets_from_text(text):
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
        if len(sentences) <= 1:
            _write_wrapped(text)
            return
        for sentence in sentences:
            _write_wrapped(sentence, first_prefix="- ", next_prefix="  ")

    paragraph_lines = []

    def _flush_paragraph():
        nonlocal paragraph_lines
        if not paragraph_lines:
            return
        joined = " ".join(line.strip() for line in paragraph_lines if line.strip())
        _write_bullets_from_text(joined)
        paragraph_lines = []

    for raw_line in safe_text.splitlines():
        line = raw_line.strip()
        heading_match = re.match(r"^\*\*(.+?)\*\*(.*)$", line)
        if heading_match:
            _flush_paragraph()
            heading = heading_match.group(1).strip()
            remainder = heading_match.group(2).lstrip(": ").strip()
            pdf.set_font("Helvetica", "B", 12)
            _write_wrapped(heading)
            pdf.set_font("Helvetica", size=11)
            if remainder:
                _write_bullets_from_text(remainder)
            pdf.ln(1)
            continue
        if line == "":
            _flush_paragraph()
            pdf.ln(4)
            continue
        is_bullet = line.startswith("- ") or line.startswith("• ")
        if is_bullet:
            _flush_paragraph()
            bullet_text = line[2:].strip()
            _write_wrapped(bullet_text, first_prefix="- ", next_prefix="  ")
            continue
        clean_line = line.replace("**", "")
        paragraph_lines.append(clean_line)

    _flush_paragraph()
    return bytes(pdf.output())

# --- 3. MAIN APP UI ---

if os.path.exists("logo.png"):
    col1, col2, col3 = st.columns([3, 2, 3])
    with col2: st.image("logo.png", use_container_width=True)

st.markdown("""
<div style='text-align: center; color: #555; margin-bottom: 25px;'>
    <p style='font-size: 1rem; color: #888;'>Smart Packing & Perfect Itineraries</p>
</div>
""", unsafe_allow_html=True)


with st.form("trip_form"):
    # dest = st.text_input("Where to?", placeholder="Tokyo, Japan")
    city_options = load_city_options(CITIES_CSV_PATH)

    dest = st.selectbox(
        "Where to?",
        options=city_options,
        index=None,  # nothing selected by default
        placeholder="Search city…",
    )

    c1, c2 = st.columns(2)
    with c1: travel_date = st.date_input("When?", min_value=dt_date.today())
    with c2: days = st.number_input("How long?", min_value=1, value=5)
    
    st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True) 
    
    b_col1, b_col2 = st.columns(2)
    
    with b_col1:
        with stylable_container(
            key="teal_btn",
            css_styles="""
                button {
                    background-color: #2a9d8f !important;
                    color: white !important;
                    border: none !important;
                    height: 2.8em !important;
                    width: 100% !important;
                    font-weight: 700 !important;
                    border-radius: 10px !important;
                }
                button:hover {
                    background-color: #1e877b !important;
                    color: white !important;
                    box-shadow: 0 4px 12px rgba(30, 135, 123, 0.3) !important;
                }
            """,
        ):
            submit_pack = st.form_submit_button("Packing Guide")

    with b_col2:
        with stylable_container(
            key="yellow_btn",
            css_styles="""
                button {
                    background-color: #f6e1a6 !important;
                    color: #264653 !important;
                    border: none !important;
                    height: 2.8em !important;
                    width: 100% !important;
                    font-weight: 700 !important;
                    border-radius: 10px !important;
                }
                button:hover {
                  
                }
            """,
        ):
            submit_places = st.form_submit_button("Visit Ideas")
    
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

# --- 4. LOGIC ---
if "packing_result" not in st.session_state:
    st.session_state.packing_result = None
if "itinerary_result" not in st.session_state:
    st.session_state.itinerary_result = None
if "last_inputs" not in st.session_state:
    st.session_state.last_inputs = None
if "last_dest" not in st.session_state:
    st.session_state.last_dest = None
if "last_date" not in st.session_state:
    st.session_state.last_date = None
if "last_days" not in st.session_state:
    st.session_state.last_days = None

inputs_key = (dest, str(travel_date), days)

if submit_pack or submit_places:
    if not dest:
        st.warning("Please tell us where you're going!")
    else:
        if (travel_date - dt_date.today()).days <= 5:
            st.success("Using Live Weather.")
        else:
            st.info("Using Seasonal History.")

        st.session_state.last_inputs = inputs_key
        st.session_state.last_dest = dest
        st.session_state.last_date = str(travel_date)
        st.session_state.last_days = days

        if submit_pack:
            st.session_state.itinerary_result = None
            with st.spinner("Analyzing Packing Needs..."):
                try:
                    result = run_advisor(dest, str(travel_date), days)
                    result = str(result or "").strip()
                    st.session_state.packing_result = result or "(No content returned. Please try again.)"
                except Exception as exc:
                    st.session_state.packing_result = None
                    st.error(f"Packing guide failed: {exc}")

        if submit_places:
            st.session_state.packing_result = None
            with st.spinner("Curating Itinerary..."):
                try:
                    result = get_itinerary(dest, str(travel_date), days)
                    result = str(result or "").strip()
                    st.session_state.itinerary_result = result or "(No content returned. Please try again.)"
                except Exception as exc:
                    st.session_state.itinerary_result = None
                    st.error(f"Itinerary failed: {exc}")

display_dest = st.session_state.last_dest or dest

if st.session_state.packing_result:
    pdf_data = create_pdf(display_dest, st.session_state.packing_result, "Packing List")
    render_section_header("Your Packing Guide", pdf_data, f"Packing_{display_dest}.pdf")
    packing_sections = _split_by_bold_sections(st.session_state.packing_result)
    render_result_cards("Your Packing Guide", packing_sections)

if st.session_state.itinerary_result:
    pdf_data = create_pdf(display_dest, st.session_state.itinerary_result, "Itinerary")
    render_section_header("Recommended Itinerary", pdf_data, f"Itinerary_{display_dest}.pdf")
    itinerary_sections = _split_itinerary_sections(st.session_state.itinerary_result)
    render_result_cards("Recommended Itinerary", itinerary_sections)

st.markdown(
    "<div class='app-footer'>"
    "Developed by <a href='https://www.linkedin.com/in/hananabukwaider/' target='_blank'>"
    "Hanan Abu Kwaider</a>"
    "</div>",
    unsafe_allow_html=True,
)
