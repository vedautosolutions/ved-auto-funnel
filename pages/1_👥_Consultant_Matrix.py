# pages/1_👥_Consultant_Matrix.py
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
st.set_page_config(page_title="Premium Enterprise | Consultant Performance Matrix", layout="wide")

# Custom CSS injection for premium high-contrast webpage elements
st.markdown("""
    <style>
    .metric-card-red {
        background-color: #FDF2F2;
        border-left: 5px solid #D63031;
        padding: 20px;
        border-radius: 4px;
        margin-bottom: 15px;
    }
    .metric-card-green {
        background-color: #F0F7F1;
        border-left: 5px solid #26A65B;
        padding: 20px;
        border-radius: 4px;
        margin-bottom: 15px;
    }
    .training-card {
        background-color: #F5F7FA;
        border-left: 5px solid #1A2530;
        padding: 15px;
        border-radius: 4px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Monetization Gate
st.sidebar.header("🔑 Premium Enterprise Authentication")
access_passcode = st.sidebar.text_input("Enter Premium Access Passcode", type="password")

# Conversion benchmarks and default configurations
TARGET_RETAIL_RATE = 0.30

if access_passcode != "VEDAUTO2026":
    st.title("👥 Tier 2: Multi-Segment Consultant Performance Matrix")
    st.warning("🔒 This enterprise-tier engine tracks multi-tab showrooms dealing across Personal (PV) and Commercial (CV) vehicle divisions.")
    st.info("To unlock multi-segment capabilities, please contact Ved Auto Solutions.")
    st.stop()

st.title("💎 Tier 2: Enterprise Multi-Segment Diagnostics")
st.write("Upload master DMS trackers or files like `BMPL H2.xlsx`. The system automatically splits data by segment (PV vs. CV) and builds uniform diagnostic matrices.")

# Showroom Configuration Workspace
with st.sidebar:
    st.header("Dealership Configuration")
    dealer_name = st.text_input("Dealership Group Name", "Ved Auto Group")
    
    st.subheader("Segment Profit Weights")
    pv_profit = st.number_input("PV Target Profit Per Unit (Rs.)", value=60000)
    cv_profit = st.number_input("CV Target Profit Per Unit (Rs.)", value=45000)

# File Upload Engine
st.header("1. Unified Data Ingestion")
uploaded_file = st.file_uploader("Upload Master DMS Tracker (xlsx/csv):", type=["csv", "xlsx"])

if "master_clean_df" not in st.session_state:
    st.session_state.master_clean_df = None

if uploaded_file is not None:
    if st.button("🧠 Run Multi-Segment AI Standardizer", type="primary"):
        with st.spinner("Analyzing workforce structures, detecting vehicle segments, and extraction patterns..."):
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
                    sample_payload = raw_df.head(45).to_string()
                    
                    system_instruction = (
                        f"You are an expert automotive data extraction tool parsing metrics for the {seg_tag} showroom division. "
                        "Identify columns mapping to Executive Names, Enquiries, and Retails. Map them dynamically. "
                        "Return ONLY a clean, valid JSON array of objects containing exactly these three keys: "
                        "'Consultant Name', 'Enquiries', 'Retails'. Convert strings to upper numbers. No backticks or explanation text."
                    )
                    
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=f"Raw Segment Frame Data:\n{sample_payload}",
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction, temperature=0.1
                        )
                    )
                    
                    clean_text = response.text.strip().replace("```json", "").replace("```", "").strip()
                    parsed_json = json.loads(clean_text)
                    
                    for row in parsed_json:
                        row["Segment"] = seg_tag
                        consolidated_records.append(row)
                        
                st.session_state.master_clean_df = pd.DataFrame(consolidated_records)
                st.success(f"🎉 AI segmented roster successfully parsed! Found {len(st.session_state.master_clean_df)} active consultants.")
                
            except Exception as e:
                st.error(f"Error structuring segments: {str(e)}")

# Analytical Processing Workspace
if st.session_state.master_clean_df is not None:
    st.subheader("Verify & Edit Extracted Showroom Roster")
    edited_master_df = st.data_editor(st.session_state.master_clean_df, num_rows="dynamic", width="stretch")
    
    if st.button("📊 Calculate Operational Audits"):
        st.header("2. Enterprise Performance Dashboard")
        
        calculated_rows = []
        total_pv_leak = 0; total_cv_leak = 0
        total_pv_enq = 0; total_pv_retails = 0
        total_cv_enq = 0; total_cv_retails = 0
        
        # Training counters for the extracted standalone summary map
        training_summary = {
            "Vehicle Demo & Pitching Drills": [],
            "Commercial Finance & Follow-up Drills": [],
            "Elite Retention Masterclass": []
        }
        
        for index, row in edited_master_df.iterrows():
            name = str(row["Consultant Name"]).upper().strip()
            enq = int(row["Enquiries"])
            retails = int(row["Retails"])
            segment = str(row["Segment"])
            
            target_retails = round(enq * TARGET_RETAIL_RATE)
            gap = max(0, target_retails - retails)
            
            if segment == "PV":
                leak = gap * pv_profit
                total_pv_leak += leak
                total_pv_enq += enq; total_pv_retails += retails
                prescription = "Vehicle Demo & Pitching Drills" if retails < target_retails else "Elite Retention Masterclass"
            else:
                leak = gap * cv_profit
                total_cv_leak += leak
                total_cv_enq += enq; total_cv_retails += retails
                prescription = "Commercial Finance & Follow-up Drills" if retails < target_retails else "Elite Retention Masterclass"
                
            training_summary[prescription].append(name)
            
            calculated_rows.append({
                "Segment": segment,
                "Consultant Name": name,
                "Enquiries": enq,
                "Retails": retails,
                "Target Retails": target_retails,
                "Revenue Leak (Rs.)": leak,
                "Prescription": prescription
            })
            
        display_df = pd.DataFrame(calculated_rows)
        global_leakage = total_pv_leak + total_cv_leak
        
        # --- PREMIUM WEBPAGE INFOGRAPHIC CARDS ---
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
                <div class="metric-card-red">
                    <p style="margin:0; font-size:13px; color:#781E1E; font-weight:bold;">TOTAL MONTHLY REVENUE LEAKAGE</p>
                    <p style="margin:5px 0; font-size:28px; color:#B41414; font-weight:bold;">Rs. {global_leakage:,}</p>
                    <p style="margin:0; font-size:12px; color:#644646;">Combined cross-segment financial recovery capability across all floors.</p>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            pv_target_total = round(total_pv_enq * TARGET_RETAIL_RATE)
            cv_target_total = round(total_cv_enq * TARGET_RETAIL_RATE)
            global_efficiency = round(((total_pv_retails + total_cv_retails) / max(1, (pv_target_total + cv_target_total))) * 100)
            global_efficiency = min(100, max(0, global_efficiency))
            
            st.markdown(f"""
                <div class="metric-card-green">
                    <p style="margin:0; font-size:13px; color:#145028; font-weight:bold;">GLOBAL SHOWROOM EFFICIENCY</p>
                    <p style="margin:5px 0; font-size:28px; color:#26A65B; font-weight:bold;">{global_efficiency} / 100</p>
                    <p style="margin:0; font-size:12px; color:#3C5A46;">Active tracking enabled for {len(edited_master_df)} showroom executives.</p>
                </div>
            """, unsafe_allow_html=True)

        # --- DYNAMIC CHART PRESENTATION FIXED ON THE WEBPAGE ---
        st.subheader("Divisional Revenue Leakage Footprint")
        fig, ax = plt.subplots(figsize=(10, 2.8))
        fig.patch.set_facecolor('#0E1117') 
        ax.set_facecolor('#0E1117')
        
        segments_chart = ['PV Division Leakage', 'CV Division Leakage']
        leaks_chart = [total_pv_leak, total_cv_leak]
        bars = ax.barh(segments_chart, leaks_chart, color=['#2980B9', '#E67E22'], height=0.45)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#31333F')
        ax.spines['bottom'].set_color('#31333F')
        ax.tick_params(colors='#E0E0E0', labelsize=10)
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'Rs. {x*1e-5:.1f} Lakh' if x > 0 else '0'))
        
        for bar in bars:
            width = bar.get_width()
            ax.annotate(f'Rs. {int(width):,}',
                        xy=(width, bar.get_y() + bar.get_height() / 2),
                        xytext=(7, 0), textcoords="offset points",
                        ha='left', va='center', fontsize=9, fontweight='bold', color='#E0E0E0')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        # --- WEBPAGE DIVISIONAL TABS ---
        tab_pv, tab_cv = st.tabs(["🚗 Passenger Vehicle (PV) Fleet Roster", "🚛 Commercial Vehicle (CV) Fleet Roster"])
        
        with tab_pv:
            pv_slice = display_df[display_df["Segment"] == "PV"].drop(columns=["Segment", "Prescription"])
            st.dataframe(pv_slice.style.format({"Revenue Leak (Rs.)": "Rs. {:,}"}), use_container_width=True, hide_index=True)
            
        with tab_cv:
            cv_slice = display_df[display_df["Segment"] == "CV"].drop(columns=["Segment", "Prescription"])
            st.dataframe(cv_slice.style.format({"Revenue Leak (Rs.)": "Rs. {:,}"}), use_container_width=True, hide_index=True)

        # --- STANDALONE MANDATE SUMMARY BLOCK (WEBPAGE) ---
        st.subheader("🎯 Standalone Divisional Training Mandate Summary")
        st.write("Aggregated remediation priorities grouped team-wide for organizational scale:")
        
        t_col1, t_col2, t_col3 = st.columns(3)
        with t_col1:
            st.markdown(f"""
                <div class="training-card">
                    <p style="margin:0; font-weight:bold; color:#1A2530;">📚 VEHICLE DEMO DRILLS</p>
                    <p style="margin:5px 0; font-size:22px; font-weight:bold;">{len(training_summary['Vehicle Demo & Pitching Drills'])} Consultants</p>
                    <p style="margin:0; font-size:11px; color:#666;">Focus: Pipeline conversion acceleration.</p>
                </div>
            """, unsafe_allow_html=True)
        with t_col2:
            st.markdown(f"""
                <div class="training-card">
                    <p style="margin:0; font-weight:bold; color:#1A2530;">🎯 FINANCE & FOLLOW-UP</p>
                    <p style="margin:5px 0; font-size:22px; font-weight:bold;">{len(training_summary['Commercial Finance & Follow-up Drills'])} Consultants</p>
                    <p style="margin:0; font-size:11px; color:#666;">Focus: Commercial deal velocity and scaling.</p>
                </div>
            """, unsafe_allow_html=True)
        with t_col3:
            st.markdown(f"""
                <div class="training-card">
                    <p style="margin:0; font-weight:bold; color:#1A2530;">⚡ ELITE RETENTION</p>
                    <p style="margin:5px 0; font-size:22px; font-weight:bold;">{len(training_summary['Elite Retention Masterclass'])} Consultants</p>
                    <p style="margin:0; font-size:11px; color:#666;">Focus: Target match optimization variance.</p>
                </div>
            """, unsafe_allow_html=True)

        # --- COMPILING MATPLOTLIB PLOT IMAGE FOR PDF EXPORT ---
        fig_pdf, ax_pdf = plt.subplots(figsize=(5.5, 3.2))
        bars_pdf = ax_pdf.bar(segments_chart, leaks_chart, color=['#2980B9', '#E67E22'], width=0.5)
        ax_pdf.spines['top'].set_visible(False)
        ax_pdf.spines['right'].set_visible(False)
        ax_pdf.spines['left'].set_color('#BDC3C7')
        ax_pdf.spines['bottom'].set_color('#BDC3C7')
        ax_pdf.tick_params(axis='both', colors='#2C3E50', labelsize=8)
        ax_pdf.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x*1e-5:.1f}L' if x > 0 else '0'))
        plt.tight_layout()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
            fig_pdf.savefig(tmpfile.name, dpi=300)
            chart_img_path = tmpfile.name
        plt.close(fig_pdf)

        # =========================================================================
        # ==================== ADVANCED ENTERPRISE PDF ENGINE ======================
        # =========================================================================
        # ALL EMOJIS REMOVED FROM TEXT FIELDS IN THIS BLOCK TO PREVENT ENCODING ERRORS
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # PAGE 1: EXECUTIVE BRIEFING
        pdf.add_page()
        pdf.set_fill_color(26, 37, 48) 
        pdf.rect(0, 0, 210, 48, 'F')
        pdf.set_fill_color(197, 160, 89) 
        pdf.rect(0, 48, 210, 2, 'F')
        
        pdf.set_font("Arial", 'B', 18); pdf.set_text_color(255, 255, 255); pdf.set_y(14)
        pdf.cell(0, 10, "ENTERPRISE MULTI-SEGMENT PERFORMANCE AUDIT", ln=True, align='C')
        pdf.set_font("Arial", '', 10); pdf.set_text_color(200, 210, 220)
        pdf.cell(0, 6, f"DEALERSHIP FACILITY: {dealer_name.upper()}  |  CROSS-SEGMENT PIPELINE EVALUATION", ln=True, align='C')
        
        # Financial Cards Block
        pdf.ln(18)
        pdf.set_fill_color(253, 242, 242); pdf.rect
