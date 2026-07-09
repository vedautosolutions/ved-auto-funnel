# pages/2_👑_Model_Variant_Diagnostics.py
import streamlit as st
import pandas as pd
import json
import os
from google import genai
from google.genai import types
from fpdf import FPDF
import matplotlib.pyplot as plt
import tempfile

# --- 1. CONFIG & APP SETUP ---
st.set_page_config(page_title="Premium Corporate | Model & Variant Diagnostics Suite", layout="wide")

# Custom CSS injection for Tier 3 Premium Dark-Blue Luxury Palette
st.markdown("""
    <style>
    .metric-card-red {
        background-color: #FFF5F5;
        border-left: 5px solid #E53E3E;
        padding: 22px;
        border-radius: 6px;
        margin-bottom: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-card-amber {
        background-color: #FFFDF5;
        border-left: 5px solid #D69E2E;
        padding: 22px;
        border-radius: 6px;
        margin-bottom: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-card-green {
        background-color: #F6FEDF5;
        border-left: 5px solid #38A169;
        padding: 22px;
        border-radius: 6px;
        margin-bottom: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .growth-card {
        background-color: #F8FAFC;
        border-left: 5px solid #2B6CB0;
        padding: 20px;
        border-radius: 6px;
        margin-bottom: 15px;
    }
    .growth-names {
        font-size: 13px;
        color: #2D3748;
        background-color: #FFFFFF;
        padding: 12px;
        border-radius: 4px;
        border: 1px solid #E2E8F0;
        margin-top: 8px;
        line-height: 1.6;
    }
    .tier3-badge {
        background-color: #2B6CB0;
        color: white;
        padding: 4px 10px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# Monetization Gate - Completely Independent Checkpoint
st.sidebar.header("👑 Tier 3 Executive Authentication")
access_passcode = st.sidebar.text_input("Enter Corporate Access Passcode", type="password")

TARGET_RETAIL_RATE = 0.30

if access_passcode != "VEDCORPORATE2026":
    st.title("👑 Tier 3: Model, Variant & Pipeline Velocity Suite")
    st.warning("🔒 This premium-tier operational framework requires a distinct Corporate Access Passcode.")
    st.info("To upgrade your deployment from foundational multi-segment tracking to granular inventory velocity diagnostics, please connect with Ved Auto Solutions.")
    st.stop()

st.title("👑 Tier 3: Inventory Velocity & Pipeline Growth Suite")
st.write("Isolate variant bottlenecks, track touchpoint latency metrics, and trace specific vehicle allocation pipelines to ensure both dealership inventory velocity and consultant competency optimization.")

# Showroom Configuration Workspace
with st.sidebar:
    st.header("Corporate Configuration")
    dealer_name = st.text_input("Dealership Group Name", "Ved Auto Group")
    
    st.subheader("Segment Profit Weights")
    pv_profit = st.number_input("PV Unit Target Margin (Rs.)", value=60000)
    cv_profit = st.number_input("CV Unit Target Margin (Rs.)", value=45000)

# File Ingestion Machine
st.header("1. Granular Data Ingestion Matrix")
uploaded_file = st.file_uploader("Upload Master DMS Tracker File (xlsx/csv):", type=["csv", "xlsx"])

# State Retention Framework Initialization
if "t3_master_df" not in st.session_state:
    st.session_state.t3_master_df = None
if "t3_calculated" not in st.session_state:
    st.session_state.t3_calculated = False

if uploaded_file is not None:
    if st.button("🧠 Execute Premium Deep-Schema Parsing Engine", type="primary"):
        with st.spinner("Extracting model volumes, evaluating status pipelines, and standardizing follow-up scores..."):
            try:
                extracted_segments = []
                
                if uploaded_file.name.endswith(".xlsx"):
                    excel_file = pd.ExcelFile(uploaded_file)
                    for sheet in excel_file.sheet_names:
                        if "summary" in sheet.lower():
                            continue
                        df_sheet = pd.read_excel(uploaded_file, sheet_name=sheet)
                        if not df_sheet.empty:
                            seg_tag = "CV" if "cv" in sheet.lower() or "commercial" in sheet.lower() else "PV"
                            extracted_segments.append((seg_tag, df_sheet))
                else:
                    df_csv = pd.read_csv(uploaded_file)
                    content_str = str(df_csv.to_string()[:2000]).lower()
                    seg_tag = "CV" if "commercial" in content_str or "cv" in content_str else "PV"
                    extracted_segments.append((seg_tag, df_csv))
                
                api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY"))
                client = genai.Client(api_key=api_key)
                consolidated_records = []
                
                for seg_tag, raw_df in extracted_segments:
                    sample_payload = raw_df.head(40).to_string()
                    
                    # Premium Deep Schema System Instructions
                    system_instruction = (
                        f"You are a premium corporate automotive analytics engine parsing detailed records for the {seg_tag} division. "
                        "Identify columns mapping to: Consultant Name, Enquiries, Retails, Follow-Up %, Vehicle Model, Vehicle Variant, and Enquiry Status. "
                        "Return ONLY a clean, valid JSON array of objects with exactly these keys: "
                        "'Consultant Name', 'Enquiries', 'Retails', 'Follow-Up %', 'Model', 'Variant', 'Status'. "
                        "If Follow-Up % is missing from rows, inject realistic values (between 40 and 95) based on conversion performance. "
                        "If Status is missing, derive it from standard pipeline terms: 'Hot', 'Warm', 'Cold', or 'Lost'. "
                        "Format strings clearly. Do not use backticks, markdown markers, or explanatory text."
                    )
                    
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=f"Raw Data Sheet:\n{sample_payload}",
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction, temperature=0.05
                        )
                    )
                    
                    clean_text = response.text.strip().replace("```json", "").replace("```", "").strip()
                    parsed_json = json.loads(clean_text)
                    
                    for row in parsed_json:
                        row["Segment"] = seg_tag
                        consolidated_records.append(row)
                        
                st.session_state.t3_master_df = pd.DataFrame(consolidated_records)
                st.session_state.t3_calculated = False
                st.success(f"🎉 Premium Schema Completed! Processed {len(st.session_state.t3_master_df)} active micro-records.")
                
            except Exception as e:
                st.error(f"Error parsing deep schema structures: {str(e)}")

# Analytical Workspace Processing Block
if st.session_state.t3_master_df is not None:
    st.subheader("Verify & Fine-Tune Parsed Operational Schema")
    edited_t3_df = st.data_editor(st.session_state.t3_master_df, num_rows="dynamic", width="stretch")
    
    if st.button("📊 Calculate Advanced Micro-Velocity Diagnostics") or st.session_state.t3_calculated:
        st.session_state.t3_calculated = True
        st.header("2. Micro-Velocity Management Dashboard")
        
        calculated_rows = []
        total_pv_leak = 0; total_cv_leak = 0
        total_enq = 0; total_retails = 0; sum_followups = 0
        
        growth_summary = {
            "Follow-Up Latency & Touchpoint Drills": [],
            "High-Variant Negotiation & Product Pitching": [],
            "Strategic Deal Closing & Pipeline Recovery": []
        }
        
        for index, row in edited_t3_df.iterrows():
            name = str(row["Consultant Name"]).upper().strip()
            enq = int(row["Enquiries"])
            retails = int(row["Retails"])
            segment = str(row["Segment"])
            f_up = int(row.get("Follow-Up %", 80))
            model = str(row.get("Model", "UNKNOWN")).upper().strip()
            variant = str(row.get("Variant", "STD")).upper().strip()
            status = str(row.get("Status", "Warm")).capitalize().strip()
            
            target_retails = round(enq * TARGET_RETAIL_RATE)
            gap = max(0, target_retails - retails)
            leak = gap * (pv_profit if segment == "PV" else cv_profit)
            
            if segment == "PV":
                total_pv_leak += leak
            else:
                total_cv_leak += leak
                
            total_enq += enq
            total_retails += retails
            sum_followups += f_up
            
            # Tier 3 Prescription Architecture: Helping both Dealership & Consultant grow
            if f_up < 70:
                prescription = "Follow-Up Latency & Touchpoint Drills"
            elif gap > 0 and status in ["Cold", "Lost"]:
                prescription = "Strategic Deal Closing & Pipeline Recovery"
            else:
                prescription = "High-Variant Negotiation & Product Pitching"
                
            growth_summary[prescription].append((name, leak, model))
            
            calculated_rows.append({
                "Segment": segment,
                "Consultant Name": name,
                "Enquiries": enq,
                "Retails": retails,
                "Follow-Up %": f_up,
                "Primary Model": model,
                "Variant": variant,
                "Lead Status": status,
                "Revenue Leak (Rs.)": leak,
                "Prescription": prescription
            })
            
        display_df = pd.DataFrame(calculated_rows)
        global_leakage = total_pv_leak + total_cv_leak
        avg_showroom_followup = round(sum_followups / max(1, len(display_df)))
        
        # --- CARDS LAYOUT ---
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
                <div class="metric-card-red">
                    <p style="margin:0; font-size:12px; color:#9B2C2C; font-weight:bold;">TOTAL REVENUE LEAKAGE FLAG</p>
                    <p style="margin:4px 0; font-size:26px; color:#C53030; font-weight:bold;">Rs. {global_leakage:,}</p>
                    <p style="margin:0; font-size:12px; color:#742A2A;">Leaked margin due to structural funnel gaps.</p>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
                <div class="metric-card-amber">
                    <p style="margin:0; font-size:12px; color:#9C4221; font-weight:bold;">MEAN SHOWROOM FOLLOW-UP RATE</p>
                    <p style="margin:4px 0; font-size:26px; color:#B7791F; font-weight:bold;">{avg_showroom_followup}%</p>
                    <p style="margin:0; font-size:12px; color:#744210;">Pipeline process discipline index.</p>
                </div>
            """, unsafe_allow_html=True)
        with col3:
            conversion_rate = round((total_retails / max(1, total_enq)) * 100, 1)
            st.markdown(f"""
                <div class="metric-card-green">
                    <p style="margin:0; font-size:12px; color:#22543D; font-weight:bold;">NET SHOWROOM CONVERSION</p>
                    <p style="margin:4px 0; font-size:26px; color:#2F855A; font-weight:bold;">{conversion_rate}%</p>
                    <p style="margin:0; font-size:12px; color:#22543D;">Baseline target index is 30.0%.</p>
                </div>
            """, unsafe_allow_html=True)

        # --- PIPELINE BOTTLE-NECK ANALYSIS WORKSPACES ---
        st.subheader("📦 Model & Variant Pipeline Velocity Matrices")
        t3_col1, t3_col2 = st.columns(2)
        
        with t3_col1:
            st.caption("🚨 Stagnant High-Value Product Lines (Cold & Lost Status)")
            stagnant_inv = display_df
