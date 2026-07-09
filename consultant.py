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
        padding: 20px;
        border-radius: 4px;
        margin-bottom: 15px;
    }
    .training-names {
        font-size: 13px;
        color: #555;
        background-color: #FFFFFF;
        padding: 10px;
        border-radius: 4px;
        border: 1px solid #E2E8F0;
        margin-top: 8px;
        line-height: 1.6;
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

# State Retention Framework Initialization
if "master_clean_df" not in st.session_state:
    st.session_state.master_clean_df = None
if "audit_calculated" not in st.session_state:
    st.session_state.audit_calculated = False

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
                st.session_state.audit_calculated = False
                st.success(f"🎉 AI segmented roster successfully parsed! Found {len(st.session_state.master_clean_df)} active consultants.")
                
            except Exception as e:
                st.error(f"Error structuring segments: {str(e)}")

# Analytical Processing Workspace
if st.session_state.master_clean_df is not None:
    st.subheader("Verify & Edit Extracted Showroom Roster")
    edited_master_df = st.data_editor(st.session_state.master_clean_df, num_rows="dynamic", width="stretch")
    
    if st.button("📊 Calculate Operational Audits") or st.session_state.audit_calculated:
        st.session_state.audit_calculated = True
        st.header("2. Enterprise Performance Dashboard")
        
        calculated_rows = []
        total_pv_leak = 0; total_cv_leak = 0
        total_pv_enq = 0; total_pv_retails = 0
        total_cv_enq = 0; total_cv_retails = 0
        
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
                
            training_summary[prescription].append((name, leak))
            
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
        
        # Calculate revenue impact aggregates per segment/module block
        pv_upside = sum(item[1] for item in training_summary["Vehicle Demo & Pitching Drills"])
        cv_upside = sum(item[1] for item in training_summary["Commercial Finance & Follow-up Drills"])
        
        # --- PREMIUM WEBPAGE INFOGRAPHIC CARDS ---
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
                <div class="metric-card-red">
                    <p style="margin:0; font-size:13px; color:#781E1E; font-weight:bold;">TOTAL MONTHLY REVENUE LEAKAGE (POTENTIAL UPSIDE)</p>
                    <p style="margin:5px 0; font-size:28px; color:#B41414; font-weight:bold;">Rs. {global_leakage:,}</p>
                    <p style="margin:0; font-size:12px; color:#644646;">Combined cross-segment financial recovery upside if training is fully realized.</p>
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

        # --- WEBPAGE DIVISIONAL TABLES ---
        tab_pv, tab_cv = st.tabs(["🚗 Passenger Vehicle (PV) Fleet Roster", "🚛 Commercial Vehicle (CV) Fleet Roster"])
        
        with tab_pv:
            pv_slice = display_df[display_df["Segment"] == "PV"].drop(columns=["Segment", "Prescription"])
            st.dataframe(pv_slice.style.format({"Revenue Leak (Rs.)": "Rs. {:,}"}), use_container_width=True, hide_index=True)
            
        with tab_cv:
            cv_slice = display_df[display_df["Segment"] == "CV"].drop(columns=["Segment", "Prescription"])
            st.dataframe(cv_slice.style.format({"Revenue Leak (Rs.)": "Rs. {:,}"}), use_container_width=True, hide_index=True)

        # --- REFACTORED MANDATE SUMMARY ROSTER BLOCK (WEBPAGE) ---
        st.subheader("🎯 Standalone Divisional Training Mandate & Roster Summary")
        st.write("Targeted remediation paths with explicit consultant allocations and clear monetary upside forecasts:")
        
        t_col1, t_col2, t_col3 = st.columns(3)
        with t_col1:
            pv_remedial = sorted([item[0] for item in training_summary['Vehicle Demo & Pitching Drills']])
            pv_remedial_str = ", ".join(pv_remedial) if pv_remedial else "None allocated"
            st.markdown(f"""
                <div class="training-card">
                    <p style="margin:0; font-weight:bold; color:#1A2530;">🚗 VEHICLE DEMO & PITCHING DRILLS (PV)</p>
                    <p style="margin:5px 0; font-size:22px; font-weight:bold; color:#D63031;">{len(pv_remedial)} Consultants</p>
                    <p style="margin:2px 0 8px 0; font-size:14px; font-weight:bold; color:#2E7D32;">📈 Potential Upside: Rs. {pv_upside:,}</p>
                    <p style="margin:0; font-size:11px; color:#666; font-style:italic;">Focus: Pipeline conversion acceleration.</p>
                    <div class="training-names"><strong>Roster:</strong> {pv_remedial_str}</div>
                </div>
            """, unsafe_allow_html=True)
            
        with t_col2:
            cv_remedial = sorted([item[0] for item in training_summary['Commercial Finance & Follow-up Drills']])
            cv_remedial_str = ", ".join(cv_remedial) if cv_remedial else "None allocated"
            st.markdown(f"""
                <div class="training-card">
                    <p style="margin:0; font-weight:bold; color:#1A2530;">🚛 COMMERCIAL FINANCE & FOLLOW-UP (CV)</p>
                    <p style="margin:5px 0; font-size:22px; font-weight:bold; color:#E67E22;">{len(cv_remedial)} Consultants</p>
                    <p style="margin:2px 0 8px 0; font-size:14px; font-weight:bold; color:#2E7D32;">📈 Potential Upside: Rs. {cv_upside:,}</p>
                    <p style="margin:0; font-size:11px; color:#666; font-style:italic;">Focus: Deal velocity and commercial closing logic.</p>
                    <div class="training-names"><strong>Roster:</strong> {cv_remedial_str}</div>
                </div>
            """, unsafe_allow_html=True)
            
        with t_col3:
            elite_remedial = sorted([item[0] for item in training_summary['Elite Retention Masterclass']])
            elite_remedial_str = ", ".join(elite_remedial) if elite_remedial else "None allocated"
            st.markdown(f"""
                <div class="training-card">
                    <p style="margin:0; font-weight:bold; color:#1A2530;">⚡ ELITE RETENTION MASTERCLASS (GLOBAL)</p>
                    <p style="margin:5px 0; font-size:22px; font-weight:bold; color:#26A65B;">{len(elite_remedial)} Consultants</p>
                    <p style="margin:2px 0 8px 0; font-size:14px; font-weight:bold; color:#1565C0;">📈 Potential Upside: Stable Baseline</p>
                    <p style="margin:0; font-size:11px; color:#666; font-style:italic;">Focus: Performance baseline preservation.</p>
                    <div class="training-names"><strong>Roster:</strong> {elite_remedial_str}</div>
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
        pdf.set_fill_color(253, 242, 242); pdf.rect(10, 60, 92, 34, 'F')
        pdf.set_fill_color(214, 48, 49); pdf.rect(10, 60, 3, 34, 'F')
        pdf.set_y(63); pdf.set_x(17); pdf.set_font("Arial", 'B', 10); pdf.set_text_color(120, 30, 30)
        pdf.cell(80, 5, "TOTAL POTENTIAL REVENUE UPSIDE", ln=True)
        pdf.set_x(17); pdf.set_font("Arial", 'B', 16); pdf.set_text_color(180, 20, 20)
        pdf.cell(80, 8, f"Rs. {global_leakage:,}", ln=True)
        
        pdf.set_y(60); pdf.set_fill_color(240, 247, 241); pdf.rect(108, 60, 92, 34, 'F')
        pdf.set_fill_color(38, 166, 91); pdf.rect(108, 60, 3, 34, 'F')
        pdf.set_y(63); pdf.set_x(115); pdf.set_font("Arial", 'B', 10); pdf.set_text_color(20, 80, 40)
        pdf.cell(80, 5, "GLOBAL EFFICIENCY RATING", ln=True)
        pdf.set_x(115); pdf.set_font("Arial", 'B', 16); pdf.set_text_color(38, 166, 91)
        pdf.cell(80, 8, f"{global_efficiency} / 100", ln=True)
        
        # Chart and Summary text
        pdf.set_y(102); pdf.set_x(10); pdf.set_font("Arial", 'B', 11); pdf.set_text_color(26, 37, 48)
        pdf.cell(0, 8, "DIVISIONAL PIPELINE REVENUE UPSIDE MAP", ln=True)
        pdf.image(chart_img_path, x=10, y=112, w=105)
        
        pdf.set_y(114); pdf.set_x(122); pdf.set_font("Arial", 'B', 10); pdf.set_text_color(44, 62, 80)
        pdf.cell(75, 5, "PASSENGER (PV) SECTOR PROFILE", ln=True)
        pdf.set_font("Arial", '', 9.5); pdf.set_x(122); pdf.set_text_color(60, 70, 80)
        pdf.cell(75, 5, f"- Pipeline Size: {total_pv_enq:,} Enq", ln=True)
        pdf.set_x(122)
        pdf.cell(75, 5, f"- Revenue Upside: Rs. {total_pv_leak:,}", ln=True)
        
        pdf.ln(4); pdf.set_x(122); pdf.set_font("Arial", 'B', 10); pdf.set_text_color(44, 62, 80)
        pdf.cell(75, 5, "COMMERCIAL (CV) SECTOR PROFILE", ln=True)
        pdf.set_font("Arial", '', 9.5); pdf.set_x(122); pdf.set_text_color(60, 70, 80)
        pdf.cell(75, 5, f"- Pipeline Size: {total_cv_enq:,} Enq", ln=True)
        pdf.set_x(122)
        pdf.cell(75, 5, f"- Revenue Upside: Rs. {total_cv_leak:,}", ln=True)
        
        # --- FIXED & RESTRUCTURED MANDATE ROSTER BLOCK FOR PDF WITH MONETARY VALUES ---
        pdf.set_y(178); pdf.set_x(10); pdf.set_font("Arial", 'B', 11); pdf.set_text_color(26, 37, 48)
        pdf.cell(0, 8, "STANDALONE TEAM REMEDIATION MANDATES, ROSTERS & MONETARY UPSIDES", ln=True)
        
        pdf.set_fill_color(245, 247, 250); pdf.rect(10, 187, 190, 52, 'F')
        current_y = 190
        
        for module_title, list_data in training_summary.items():
            pdf.set_y(current_y); pdf.set_x(14)
            pdf.set_font("Arial", 'B', 9); pdf.set_text_color(26, 37, 48)
            pdf.cell(75, 4.5, f"{module_title.upper()}:")
            
            pdf.set_font("Arial", 'B', 8.5); pdf.set_text_color(100, 110, 120)
            pdf.cell(35, 4.5, f"[{len(list_data)} Registered]")
            
            # Print calculated potential segment financial value targets
            pdf.set_font("Arial", 'B', 8.5)
            if "Elite" in module_title:
                pdf.set_text_color(38, 166, 91)
                pdf.cell(60, 4.5, "Upside: Maintain Baseline Efficiency", ln=True)
            else:
                pdf.set_text_color(46, 125, 50)
                mod_upside = sum(item[1] for item in list_data)
                pdf.cell(60, 4.5, f"Upside Target Value: +Rs. {mod_upside:,}", ln=True)
            
            pdf.set_x(14); pdf.set_font("Arial", '', 8); pdf.set_text_color(80, 85, 95)
            names_chunk = ", ".join(sorted([item[0] for item in list_data])) if list_data else "No allocations."
            
            pdf.set_x(14)
            pdf.multi_cell(182, 3.8, names_chunk, border=0, align='L')
            current_y = pdf.get_y() + 1.5

        # PAGE 2+: GRANULAR ROSTER MATRIX
        pdf.add_page()
        pdf.set_font("Arial", 'B', 13); pdf.set_text_color(26, 37, 48)
        pdf.cell(0, 8, "DETAILED SHOWROOM OPERATIONAL PERFORMANCE MATRIX", ln=True)
        pdf.ln(3)
        
        pdf.set_font("Arial", 'B', 9); pdf.set_text_color(255, 255, 255); pdf.set_fill_color(26, 37, 48)
        pdf.cell(18, 9, " DIV", fill=True, ln=False)
        pdf.cell(60, 9, " CONSULTANT EXECUTIVE ROSTER", fill=True, ln=False)
        pdf.cell(22, 9, "ENQUIRIES", fill=True, ln=False, align='C')
        pdf.cell(24, 9, "DELIVERED", fill=True, ln=False, align='C')
        pdf.cell(22, 9, "TARGET", fill=True, ln=False, align='C')
        pdf.cell(44, 9, "REVENUE LOSS LEAKAGE ", fill=True, ln=True, align='R')
        
        pdf.set_font("Arial", '', 9); pdf.set_text_color(40, 45, 55)
        alternate_row = False
        
        for row in calculated_rows:
            if alternate_row:
                pdf.set_fill_color(246, 249, 252)
            else:
                pdf.set_fill_color(255, 255, 255)
                
            safe_name = str(row['Consultant Name']).encode('ascii', 'ignore').decode('ascii').strip().upper()
            
            pdf.cell(18, 8.5, f" {row['Segment']}", fill=True, ln=False, border="B")
            pdf.cell(60, 8.5, f" {safe_name[:28]}", fill=True, ln=False, border="B")
            pdf.cell(22, 8.5, str(row['Enquiries']), fill=True, ln=False, align='C', border="B")
            pdf.cell(24, 8.5, str(row['Retails']), fill=True, ln=False, align='C', border="B")
            pdf.cell(22, 8.5, str(row['Target Retails']), fill=True, ln=False, align='C', border="B")
            
            if row['Revenue Leak (Rs.)'] > 0:
                pdf.set_text_color(190, 30, 30); pdf.set_font("Arial", 'B', 9)
                pdf.cell(44, 8.5, f"Rs. {row['Revenue Leak (Rs.)']:,} ", fill=True, ln=True, align='R', border="B")
                pdf.set_text_color(40, 45, 55); pdf.set_font("Arial", '', 9)
            else:
                pdf.set_text_color(38, 166, 91); pdf.set_font("Arial", 'B', 9)
                pdf.cell(44, 8.5, "Rs. 0 ", fill=True, ln=True, align='R', border="B")
                pdf.set_text_color(40, 45, 55); pdf.set_font("Arial", '', 9)
                
            alternate_row = not alternate_row
            
        try:
            os.unlink(chart_img_path)
        except:
            pass
            
        pdf_bytes = pdf.output(dest='S').encode('latin-1', errors='ignore')
        st.write("")
        st.download_button("📥 Export Multi-Segment Enterprise Audit (PDF)", data=pdf_bytes, file_name=f"Enterprise_Showroom_Audit_{dealer_name}.pdf", type="primary")