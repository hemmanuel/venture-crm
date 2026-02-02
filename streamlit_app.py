import streamlit as st
import pandas as pd
import json
import re
import html
from st_click_detector import click_detector

# --- 1. APP CONFIGURATION ---
st.set_page_config(
    layout="wide",
    page_title="Venture CRM",
    initial_sidebar_state="collapsed"
)

# --- 2. SHARED CSS ---
CARD_CSS = """
    /* Reset & Typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    body {
        font-family: 'Inter', sans-serif;
        color: #1f2937;
        margin: 0;
        padding: 0;
    }

    /* --- COMPACT LAYOUT OVERRIDES --- */
    .block-container {
        padding-top: 6rem !important; 
        padding-bottom: 2rem !important;
        padding-left: 1rem !important; 
        padding-right: 1rem !important; 
        max-width: 100% !important; 
    }

    /* HEADER AS TITLE BAR */
    header[data-testid="stHeader"] {
        background-color: #FFFFFF !important; 
        border-bottom: 1px solid #E5E7EB; 
        z-index: 100000;
        position: fixed !important;
        top: 0 !important;
        height: 5rem !important; 
        pointer-events: none; 
    }

    header[data-testid="stHeader"] > div:first-child {
        pointer-events: auto;
    }

    .fixed-title-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 5rem;
        z-index: 100001; 
        padding-left: 1.5rem;
        display: flex;
        flex-direction: column;
        justify-content: center;
        pointer-events: none; 
    }

    .title-main {
        font-size: 20px;
        font-weight: 700;
        color: #111827;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }

    .title-sub {
        font-size: 13px;
        color: #6B7280;
        font-weight: 400;
        margin-top: 4px;
    }

    [data-testid="stDecoration"] { display: none; }
    div[data-testid="stVerticalBlock"] { gap: 0.5rem !important; }
    .stSelectbox, .stMultiSelect, .stToggle { margin-bottom: 0px !important; }

    /* FORCE WIDER DIALOG (90% width) */
    div[role="dialog"][aria-modal="true"] {
        width: 90vw !important;
        max-width: 1600px !important; 
    }

    /* Card Styling - NOW AN ANCHOR TAG */
    a.crm-card {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 16px; 
        margin-bottom: 8px; 
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        transition: all 0.2s ease;
        min-height: 140px; 
        gap: 12px; 
        cursor: pointer;
        position: relative;
        z-index: 1;

        /* Reset Anchor Styles */
        text-decoration: none !important;
        color: inherit !important;
        width: 100%;
    }

    a.crm-card:hover {
        box-shadow: 0 6px 12px rgba(0,0,0,0.05);
        border-color: #3B82F6;
        transform: translateY(-1px);
        z-index: 10;
    }

    a.crm-card:active {
        transform: scale(0.99);
        background-color: #F9FAFB;
    }

    a.crm-card:focus {
        outline: none;
    }

    /* Pass through clicks to parent container */
    .card-icon, .card-info, .card-dna, .card-meta, .dna-item, .dna-label, .dna-value, .card-title, .card-subtitle, .card-desc, .metric-value, .metric-label { 
        pointer-events: none; 
    }

    .card-icon { width: 50px; flex-shrink: 0; }
    .card-info { flex: 1 1 250px; padding-right: 16px; border-right: 1px solid #F3F4F6; margin-right: 10px; }
    .card-dna { flex: 2 1 400px; display: flex; align-items: center; min-width: 0; }
    .card-meta { flex: 0 0 110px; text-align: right; display: flex; flex-direction: column; justify-content: center; align-items: flex-end; padding-left: 16px; border-left: 1px solid #F3F4F6; }

    .dna-grid { 
        display: grid; 
        grid-template-columns: repeat(4, 1fr); /* Default: 4 columns */
        gap: 8px 16px; 
        width: 100%; 
    }

    /* --- RESPONSIVE BREAKPOINTS --- */

    /* Tablet (Narrower) */
    @media (max-width: 1200px) {
        .card-info { border-right: none; margin-right: 0; }

        /* Stack the Score/Meta section to the bottom */
        .card-meta { 
            border-left: none; 
            padding-left: 0; 
            align-items: center; 
            text-align: left; 
            flex-direction: row; 
            justify-content: space-between; 
            width: 100%; 
            margin-top: 10px; 
            border-top: 1px solid #F3F4F6; 
            padding-top: 10px; 
        }

        /* Reduce grid to 2 columns (Larger items) */
        .dna-grid { grid-template-columns: repeat(2, 1fr) !important; }
    }

    /* Mobile (Small Screens) */
    @media (max-width: 768px) {
        /* Stack everything vertically */
        a.crm-card {
            flex-direction: column;
            align-items: flex-start;
        }

        .card-icon {
            margin-bottom: 12px;
        }

        .card-info {
            width: 100%;
            padding-right: 0;
            margin-bottom: 16px;
            border-right: none;
        }

        .card-dna {
            width: 100%;
            margin-bottom: 16px;
        }

        /* 1 Column Grid: Maximum visibility for each item */
        .dna-grid { 
            grid-template-columns: 1fr !important; 
            gap: 12px;
        }

        .dna-item {
            border-bottom: 1px solid #F9FAFB;
            padding-bottom: 8px;
        }

        .dna-label {
            font-size: 11px; /* Slightly larger label */
        }

        .dna-value {
            font-size: 13px; /* Larger value text */
            white-space: normal; /* Allow wrapping on small screens */
        }

        .card-meta {
            width: 100%;
            background-color: #F9FAFB;
            padding: 12px;
            border-radius: 8px;
            margin-top: 0;
            border: 1px solid #F3F4F6;
        }
    }

    /* UTILITIES FOR PROFILE */
    .profile-label {
        font-size: 11px;
        font-weight: 600;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }

    .profile-value {
        font-size: 14px;
        font-weight: 600;
        color: #111827;
        line-height: 1.4;
    }

    .card-title { font-size: 17px; font-weight: 700; color: #111827; margin-bottom: 4px; letter-spacing: -0.01em; line-height: 1.2; }
    .card-subtitle { font-size: 12px; color: #6B7280; display: flex; align-items: center; gap: 6px; margin-bottom: 6px; font-weight: 500; }
    .card-desc { font-size: 12px; color: #4B5563; margin-top: 4px; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }

    .metric-value { font-size: 22px; font-weight: 700; color: #1F2937; letter-spacing: -0.02em; }
    .metric-label { font-size: 10px; font-weight: 600; text-transform: uppercase; color: #9CA3AF; letter-spacing: 0.5px; margin-top: 4px; }

    .dna-item { display: flex; flex-direction: column; min-width: 0; }
    .dna-label { font-size: 10px; color: #6B7280; font-weight: 600; margin-bottom: 2px; }
    .dna-value { font-size: 12px; color: #111827; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
"""

# Apply CSS
st.markdown(f"<style>{CARD_CSS} .stApp {{ background-color: #F3F4F6; }} </style>", unsafe_allow_html=True)


# --- 3. HELPER FUNCTIONS ---
def render_profile(data):
    """
    Renders a professional company profile inside a dialog.
    """
    dossier = data.get('vc_dossier')
    is_prospect = dossier is not None

    # --- HEADER ---
    st.markdown(f"## {data.get('name', 'Unknown')}")
    hq = dossier.get('hq_location', 'Global') if is_prospect else 'Global'
    l1 = data.get('taxonomy', {}).get('l1', '')
    st.caption(f"📍 {hq} | {l1}")

    st.divider()

    # --- CONTENT LAYOUT ---
    # Use 'gap' to create distinct visual separation between narrative and stats
    c1, c2 = st.columns([2, 1.2], gap="large")

    with c1:
        # 1. Executive Summary
        st.markdown("#### Executive Summary")
        desc = data.get('pitch_summary') or data.get('full_description') or "No description available."
        st.write(desc)
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

        # 2. VC Alignment (Custom Card)
        st.markdown(f"""
        <div style="background-color: #F9FAFB; border-left: 4px solid #3B82F6; padding: 20px; border-radius: 4px; border-top: 1px solid #E5E7EB; border-right: 1px solid #E5E7EB; border-bottom: 1px solid #E5E7EB; margin-bottom: 30px;">
            <div style="font-size: 13px; font-weight: 700; color: #1F2937; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.5px;">VC Alignment</div>
            <div style="font-size: 15px; color: #374151; line-height: 1.6;">{data.get('rationale', 'No specific rationale provided.')}</div>
        </div>
        """, unsafe_allow_html=True)

        if is_prospect:
            # 3. Strategic DNA (Grouped Insights)
            st.markdown("#### Strategic DNA")

            insights_html = ""

            # Big Picture Fit
            if dossier.get('macro_trend'):
                insights_html += f"""
                <div style="margin-bottom: 16px;">
                    <div class="profile-label">Big Picture Fit</div>
                    <div style="font-size: 15px; color: #111827;">{dossier.get('macro_trend')}</div>
                </div>
                """

            # ELI5
            if dossier.get('analogy'):
                insights_html += f"""
                <div style="margin-bottom: 16px;">
                    <div class="profile-label">The "ELI5" Analogy</div>
                    <div style="font-size: 15px; color: #111827; font-style: italic;">"{dossier.get('analogy')}"</div>
                </div>
                """

            # MOAT
            if dossier.get('moat_description'):
                insights_html += f"""
                <div style="margin-bottom: 16px;">
                    <div class="profile-label">Competitive Moat</div>
                    <div style="font-size: 15px; color: #111827;">{dossier.get('moat_description')}</div>
                </div>
                """

            st.markdown(insights_html, unsafe_allow_html=True)

    with c2:
        # --- SCORE CARD ---
        score = data.get('venture_scale_score', 0)
        score_color = "#10B981" if score >= 0.7 else ("#F59E0B" if score >= 0.5 else "#EF4444")

        st.markdown(f"""
        <div style="background-color: #FFFFFF; padding: 24px; border-radius: 12px; border: 1px solid #E5E7EB; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); text-align: center; margin-bottom: 30px;">
            <div style="font-size: 11px; font-weight: 700; color: #6B7280; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 1px;">AI Venture Score</div>
            <div style="font-size: 48px; font-weight: 800; color: {score_color}; line-height: 1;">{score:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

        if is_prospect:
            # --- VITALS GRID ---
            vitals = [
                ("Stage", data.get('stage_estimate', '—')),
                ("Founded", dossier.get('year_founded', '—')),
                ("Raised", dossier.get('total_raised', '—')),
                ("Team", dossier.get('headcount_estimate', '—')),
                ("Last Raise", dossier.get('latest_round', '—')),
                ("Status", dossier.get('corporate_status', '—'))
            ]

            # Construct HTML on one line to avoid Markdown indent issues
            grid_html = '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px;">'
            for label, val in vitals:
                grid_html += f'<div><div class="profile-label">{label}</div><div class="profile-value">{val}</div></div>'
            grid_html += "</div>"
            st.markdown(grid_html, unsafe_allow_html=True)

            st.markdown('<div style="border-top: 1px solid #E5E7EB; margin-bottom: 24px;"></div>',
                        unsafe_allow_html=True)

            # --- NETWORK (Pills) ---

            # Helper for pills
            def make_pills(items, bg_color, text_color, border_color):
                return " ".join([
                    f"<span style='background-color: {bg_color}; color: {text_color}; padding: 4px 12px; border-radius: 99px; font-size: 11px; font-weight: 600; display: inline-block; margin-right: 6px; margin-bottom: 8px; border: 1px solid {border_color};'>{i}</span>"
                    for i in items
                ])

            # Investors
            st.markdown('<div class="profile-label" style="margin-bottom: 8px;">Key Investors</div>',
                        unsafe_allow_html=True)
            investors = dossier.get('key_investors', [])
            if isinstance(investors, str): investors = [i.strip() for i in investors.split(',') if i.strip()]

            if investors:
                st.markdown(make_pills(investors, '#F3F4F6', '#374151', '#E5E7EB'), unsafe_allow_html=True)
            else:
                st.caption("—")

            st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

            # Customers
            st.markdown('<div class="profile-label" style="margin-bottom: 8px;">Key Customers</div>',
                        unsafe_allow_html=True)
            customers = dossier.get('key_customers', [])
            if isinstance(customers, str): customers = [c.strip() for c in customers.split(',') if c.strip()]

            if customers:
                st.markdown(make_pills(customers, '#ECFDF5', '#047857', '#A7F3D0'), unsafe_allow_html=True)
            else:
                st.caption("—")

        else:
            # Fallback
            st.markdown("**Business Model**")
            st.write(data.get('business_model', 'N/A'))
            st.markdown("**Type**")
            st.write(data.get('stage_estimate', 'Corporate'))


# --- 4. DATA LOADING ---
@st.cache_data
def load_data():
    try:
        with open('companies_scored_v2.json', 'r') as f:
            data = json.load(f)

        rows = []
        for item in data:
            l1 = item.get('taxonomy', {}).get('l1', 'Unknown')
            l3 = item.get('taxonomy', {}).get('l3', 'Unknown')
            dossier = item.get('vc_dossier') or {}

            dims = item.get('dimension_scores', {})
            tech_leverage = dims.get('Tech Leverage')
            if tech_leverage is None:
                tech_leverage = 0.0

            def get_list_str(key, limit=2):
                val = dossier.get(key, [])
                if isinstance(val, list):
                    return ", ".join(val[:limit])
                return str(val) if val else "—"

            # Parse Money
            def parse_money(s):
                if not isinstance(s, str): return 0
                s_clean = s.upper().replace('$', '').replace('~', '')
                match = re.search(r'[\d,.]+', s_clean)
                if not match: return 0
                try:
                    num = float(match.group().replace(',', ''))
                    if 'B' in s_clean:
                        num *= 1e9
                    elif 'M' in s_clean:
                        num *= 1e6
                    elif 'K' in s_clean:
                        num *= 1e3
                    return num
                except:
                    return 0

            # Parse Headcount
            def parse_headcount(s):
                if not isinstance(s, str): return 0
                match = re.search(r'[\d,]+', s)
                if not match: return 0
                try:
                    return int(match.group().replace(',', ''))
                except:
                    return 0

            # Parse Stage
            stage_raw = item.get('stage_estimate', 'Unknown')

            def parse_stage_score(s):
                s = str(s).lower()
                if 'seed' in s: return 1
                if 'series a' in s: return 2
                if 'series b' in s: return 3
                if 'growth' in s: return 4
                if 'late' in s: return 5
                if 'public' in s or 'mature' in s: return 6
                return 0

            meta = {
                "Total Raised": dossier.get('total_raised', '—'),
                "Key Investors": get_list_str('key_investors'),
                "Current Stage": stage_raw,
                "Last Raise": dossier.get('latest_round', '—'),
                "Year Founded": dossier.get('year_founded', '—'),
                "Headcount": dossier.get('headcount_estimate', '—'),
                "Status": dossier.get('corporate_status', 'Active'),
                "Key Customers": get_list_str('key_customers')
            }

            hq = dossier.get('hq_location', 'Global')
            status = dossier.get('corporate_status', 'Independent')

            rows.append({
                "name": item['name'],
                "desc": item.get('investment_thesis_one_liner', ''),
                "hq": hq,
                "score": item.get('venture_scale_score', 0),
                "status": status,
                "l1": l1,
                "l3": l3,
                "meta": meta,
                "tech_leverage": tech_leverage,
                "stage": stage_raw,
                "sort_raised": parse_money(meta['Total Raised']),
                "sort_headcount": parse_headcount(meta['Headcount']),
                "sort_stage": parse_stage_score(meta['Current Stage']),
                "raw": item  # Save raw data for profile
            })

        df = pd.DataFrame(rows)
        return df[df['score'] >= 0.6]

    except FileNotFoundError:
        return pd.DataFrame()


df = load_data()

# --- 5. MAIN CONTENT & TOOLBAR ---
st.markdown("""
    <div class="fixed-title-container">
        <div class="title-main">University Experiential Learning - Venture Capital Prospects</div>
        <div class="title-sub">AI-assisted analytics for companies exhibiting booth at 2026 Distributech Conference</div>
    </div>
""", unsafe_allow_html=True)

with st.container():
    c1, c2, c3, c4, c5, c6 = st.columns([2, 1.5, 1.5, 1.5, 1.5, 1.2], vertical_alignment="bottom")
    with c1:
        sectors = df['l1'].unique().tolist()
        sel_sectors = st.multiselect("Industry", sectors, placeholder="All")
    with c2:
        stages = df['stage'].unique().tolist()
        sel_stages = st.multiselect("Stage", stages, placeholder="All")
    with c3:
        statuses = df['status'].unique().tolist()
        sel_statuses = st.multiselect("Status", statuses, placeholder="All")
    with c4:
        sort_by = st.selectbox("Sort By", ["Venture Score", "Amount Raised", "Headcount", "Stage"])
    with c5:
        sort_order = st.selectbox("Order", ["High to Low", "Low to High"])
    with c6:
        ai_focus = st.toggle("AI-Focused", help="Tech Leverage Score ≥ 0.8")

# Filter Logic
filtered_df = df.copy()
if sel_sectors: filtered_df = filtered_df[filtered_df['l1'].isin(sel_sectors)]
if sel_stages: filtered_df = filtered_df[filtered_df['stage'].isin(sel_stages)]
if sel_statuses: filtered_df = filtered_df[filtered_df['status'].isin(sel_statuses)]
if ai_focus: filtered_df = filtered_df[filtered_df['tech_leverage'] >= 0.8]

# Sort Logic
ascending = sort_order == "Low to High"
if not filtered_df.empty:
    if sort_by == "Venture Score":
        filtered_df = filtered_df.sort_values('score', ascending=ascending)
    elif sort_by == "Amount Raised":
        filtered_df = filtered_df.sort_values('sort_raised', ascending=ascending)
    elif sort_by == "Headcount":
        filtered_df = filtered_df.sort_values('sort_headcount', ascending=ascending)
    elif sort_by == "Stage":
        filtered_df = filtered_df.sort_values('sort_stage', ascending=ascending)

st.markdown(
    f"<div style='color: #6B7280; font-size: 13px; font-weight: 500; margin-bottom: 12px; margin-top: -15px; margin-left: 2px;'>Showing {len(filtered_df)} companies</div>",
    unsafe_allow_html=True)


# --- 6. RENDER LIST ---
def generate_card_html(row, idx):
    # Escape all dynamic data to prevent HTML breakage
    name = html.escape(str(row['name']))
    hq = html.escape(str(row['hq']))
    l3 = html.escape(str(row['l3']))
    desc = html.escape(str(row['desc']))

    initials = "".join([n[0] for n in name.split()[:2]])
    colors = ['#EF4444', '#F59E0B', '#10B981', '#3B82F6', '#6366F1', '#8B5CF6']
    bg_color = colors[hash(name) % len(colors)]

    meta_html = "<div class='dna-grid'>"
    fields = [
        ("Total Raised", row['meta']['Total Raised']),
        ("Key Investors", row['meta']['Key Investors']),
        ("Current Stage", row['meta']['Current Stage']),
        ("Last Raise", row['meta']['Last Raise']),
        ("Year Founded", row['meta']['Year Founded']),
        ("Headcount", row['meta']['Headcount']),
        ("Status", row['meta']['Status']),
        ("Key Customers", row['meta']['Key Customers'])
    ]
    for label, value in fields:
        # Escape label and value
        safe_label = html.escape(str(label))
        safe_value = html.escape(str(value))
        meta_html += f"<div class='dna-item'><div class='dna-label'>{safe_label}</div><div class='dna-value' title='{safe_value}'>{safe_value}</div></div>"
    meta_html += "</div>"

    # Use ANCHOR TAG wrapper for robust click detection
    # Use simple index number as ID
    return f"""
    <a class="crm-card" href="#" id="{idx}">
        <div class="card-icon">
            <div style="width: 48px; height: 48px; background-color: {bg_color}; color: white; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 16px;">
                {initials}
            </div>
        </div>
        <div class="card-info">
            <div class="card-title">{name}</div>
            <div class="card-subtitle">📍 {hq} &nbsp;&bull;&nbsp; {l3}</div>
            <div class="card-desc">{desc}</div>
        </div>
        <div class="card-dna">{meta_html}</div>
        <div class="card-meta">
            <div class="metric-value">{row['score']:.2f}</div>
            <div class="metric-label">Venture Score</div>
        </div>
    </a>
    """


full_html_content = f"<style>{CARD_CSS}</style>"
if not filtered_df.empty:
    for idx, row in filtered_df.iterrows():
        # Pass the Index (idx) to the generator
        full_html_content += generate_card_html(row, idx)
else:
    full_html_content += "<div style='padding:40px; text-align:center; color:#6B7280; font-family: Inter;'>No companies match the current filters.</div>"

# Use a fixed key to prevent remounting issues
clicked_id = click_detector(full_html_content, key="company_click_detector")

# --- DEBUGGER (SIDEBAR) ---
# Print to console for verification
if clicked_id:
    print(f"DEBUG: Click Detected! ID = {clicked_id}")

with st.sidebar:
    with st.expander("🐞 Debugger", expanded=True):
        st.write(f"**Clicked ID:** `{clicked_id}`")


# Define the dialog function OUTSIDE the interaction loop
@st.dialog("Company Profile", width="large")
def open_company_modal(row_data):
    render_profile(row_data)


if clicked_id:
    try:
        # ID is now just a plain number string "5", "10", etc.
        selected_index = int(clicked_id)

        # The DataFrame (df) stores the original indices
        selected_row = df.loc[selected_index]
        raw_data = selected_row['raw']

        # Call the dialog
        open_company_modal(raw_data)

    except Exception as e:
        st.sidebar.error(f"Error loading profile: {e}")