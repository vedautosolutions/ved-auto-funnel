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

# --- 1. CONFIG & API CHECK ---
st.set_page_config(page_title="Tier 2 | Consultant Performance Matrix", layout="wide")

# Monetization gate: Check if they unlocked premium mode
st.sidebar.header("🔑 Premium Authentication")
access_passcode = st.sidebar.text_input("Enter Premium Access Passcode", type="password")

# --- LIVE BRAND MARGINS (TIER 1 MATCH) ---
INDIAN_BRANDS = {
    "4-Wheeler": {
        "Aston Martin": 1200000, "Audi": 250000, "BMW": 250000, "Honda Cars India": 60000,
        "Hyundai India": 55000, "Kia India": 60000, "Mahindra & Mahindra": 75000,
        "Maruti Suzuki": 40000, "Mercedes-Benz": 270000, "Tata Motors": 50000, "Toyota Kirloskar": 85000
    },
    "2-Wheeler": {
        "Ather Energy": 12000, "Bajaj Auto": 7500, "Hero MotoCorp": 5000, "Honda HMSI": 6000,
        "Ola Electric": 9000, "Royal Enfield": 16000, "TVS Motor": 6500, "Yamaha India": 8000
    }
}
BM = {"TD": 0.75, "RETAIL": 0.30}

# Hardcoded passcode check for validation
if access_passcode != "VEDAUTO2026":
    st.title("👥 Tier 2: Consultant-Wise Performance Matrix")
    st.warning("🔒 This workspace contains proprietary consultant-level leak tracking and automated training prescription engines.")
    st.info("To unlock this premium analytical tier for your showroom, please contact Ved Auto Solutions via your representative.")
    
    st.link_button("🚀 Request Premium Access Passcode via WhatsApp", 
                   "https://wa.me/918764628352?text=Hi%20Ved,%20I%20want%20to%20buy%20the%20Premium%20Passcode%20to%20unlock%20the%20Tier%202%20Consultant%20Matrix%20for%20my%20dealership.")
    st.stop()

# --- CONTINUING TO PREMIUM WORKSPACE IF UNLOCKED ---
st.title("👥 Tier 2: Premium Consultant Diagnostics")
st.write("Upload raw DMS trackers or sales spreadsheets. The integrated AI automatically structures the data into your standardized matrix.")

# 1. Showroom Parameters
with st.sidebar:
    st.header("Showroom Profile")
    dealer_name = st.text_input("Dealership Name", "Ved Auto Group")
    vehicle_type = st.radio("Vehicle Category", ["4-Wheeler", "2-Wheeler"])
    brand_list = sorted(list(INDIAN_BRANDS[vehicle_type].keys()))
    selected_brand = st.selectbox("Select Manufacturer", brand_list)
    profit_per_unit = st.number_input("Target Profit Per Unit (Rs.)", value=INDIAN_BRANDS[vehicle_type][selected_brand])

# 2. File Upload & AI Zero-Friction Engine
st.header("1. Data Ingestion")
uploaded_file = st.file_uploader("Drop any messy Excel or CSV file containing consultant sales tallies here:", type=["csv", "xlsx"])

# Initializing data framework state
if "clean_df" not in st.session_state:
    st.session_state.clean_df = None

if uploaded_file is not None:
    if st.button("🧠 Run Zero-Friction AI Standardizer", type="primary"):
        with st.spinner("AI scanning sheets, resolving data matrices, and verifying columns..."):
            try:
                raw_df = None
                target_sheet = None
                
                # A. Parse layout variations
                if uploaded_file.name.endswith(".csv"):
                    raw_df = pd.read_csv(uploaded_file)
                else:
                    excel_file = pd.ExcelFile(uploaded_file)
                    sheet_names = excel_file.sheet_names
                    
                    # Keywords to identify the correct performance metrics tab
                    anchor_keywords = ["consultant", "sc name", "enquiry", "retail", "booking", "test drive", "td"]
                    
                    for sheet in sheet_names:
                        df_peek = pd.read_excel(uploaded_file, sheet_name=sheet, nrows=5)
                        sheet_content_sample = " ".join([str(item) for item in df_peek.astype(str).values.flatten()]).lower()
                        
                        if any(keyword in sheet_content_sample for keyword in anchor_keywords):
                            raw_df = pd.read_excel(uploaded_file, sheet_name=sheet)
                            target_sheet = sheet
                            break
                    
                    if raw_df is None:
                        raw_df = pd.read_excel(uploaded_file, sheet_name=0)

                # B. Validation Gateway
                if raw_df is None or raw_df.empty or len(raw_df.columns) < 2:
                    st.error("❌ **Invalid Document Profile:** The system analyzed this file but could not detect a valid Sales Consultant performance matrix. Please upload a raw DMS/ERP performance report.")
                    st.stop()

                if target_sheet:
                    st.toast(f"🎯 AI successfully identified data matrix in tab: '{target_sheet}'", icon="✅")

                file_summary_text = raw_df.to_string()

                # C. API Key Authorization
                api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY"))
                if not api_key:
                    st.error("Missing Gemini API Key configuration. Add GEMINI_API_KEY to your Streamlit secrets control panel.")
                    st.stop()
                
                client = genai.Client(api_key=api_key)
                
                system_instruction = (
                    "You are an expert automotive data extraction tool. Analyze the provided text dataset "
                    "representing an internal automotive dealership sales tracker. Your job is to extract data for "
                    "individual Sales Consultants (SC) and format it into a standardized JSON array.\n\n"
                    "Match column fields dynamically based on context (e.g., 'SC Name', 'Executive', 'Sales Person' -> 'Consultant Name'; "
                    "'Walkin', 'Enq', 'Leads' -> 'Enquiries'; 'TD', 'Test Drive' -> 'Test Drives'; 'Bkg', 'Booking' -> 'Bookings'; "
                    "'Retail', 'Delivery', 'Inv' -> 'Retails').\n\n"
                    "Strict Requirements:\n"
                    "1. Return ONLY a valid JSON array of objects with exactly these 5 keys: 'Consultant Name', 'Enquiries', 'Test Drives', 'Bookings', 'Retails'.\n"
                    "2. Do not include markdown code fences (like ```json), no markdown block formatting, and no conversational text.\n"
                    "3. Convert values to whole numbers. If a value is missing, default it to 0."
                )

                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=f"Raw Data to Parse:\n{file_summary_text}",
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.1
                    )
                )
                
                # Sanitize response string just in case
                clean_json_string = response.text.strip()
                if clean_json_string.startswith("```"):
                    clean_json_string = clean_json_string.split("json")[-1].split("```")[0].strip()
                
                parsed_data = json.loads(clean_json_string)
                st.session_state.clean_df = pd.DataFrame(parsed_data)
                st.success("🎉 Data successfully structured by AI agent!")
                
            except Exception as e:
                st.error(f"Failed to process dataset: {str(e)}")

# Allow user review and minor editing of AI output to avoid pipeline blocks
if st.session_state.clean_df is not None:
    st.subheader("Verify Processed Sales Consultant Roster:")
    edited_df = st.data_editor(st.session_state.clean_df, num_rows="dynamic", width="stretch")
    
    if st.button("📊 Calculate Individual Leaks & Training Prescriptions"):
        st.header("2. Analytical Breakdown Matrix")
        
        processed_rows = []
        total_showroom_leak = 0
        
        # Lists for tracking graph metrics
        sc_names = []
        sc_leaks = []
        
        for index, row in edited_df.iterrows():
            name = str(row["Consultant Name"])
            enq = int(row["Enquiries"])
            tds = int(row["Test Drives"])
            bkgs = int(row["Bookings"])
            retails = int(row["Retails"])
            
            # Run deep math per consultant
            target_tds = round(enq * BM["TD"])
            target_retails = round(enq * BM["RETAIL"])
            
            sc_retail_gap = max(0, target_retails - retails)
            sc_leakage_val = sc_retail_gap * profit_per_unit
            total_showroom_leak += sc_leakage_val
            
            td_ratio = (tds / enq * 100) if enq > 0 else 0
            bkg_ratio = (bkgs / tds * 100) if tds > 0 else 0
            
            # Select prescriptive module
            if td_ratio < 75:
                prescription = "📚 Vehicle Demo & Pitching Drills"
            elif bkg_ratio < 40:
                prescription = "🎯 Objection Handling & Finance Modules"
            else:
                prescription = "⚡ Urgency Closing Techniques"
                
            processed_rows.append({
                "Consultant Name": name,
                "Enquiries": enq,
                "TD Conversion %": f"{td_ratio:.1f}%",
                "Retails Delivered": retails,
                "Target Retails": target_retails,
                "Revenue Leak (Rs.)": f"Rs. {sc_leakage_val:,}",
                "Training Prescription": prescription,
                "raw_leak": sc_leakage_val
            })
            
            sc_names.append(name)
            sc_leaks.append(sc_leakage_val)
            
        display_results_df = pd.DataFrame(processed_rows)
        st.table(display_results_df.drop(columns=["raw_leak"], errors="ignore"))
        
        st.metric("Total Showroom Monthly Profit Recovery Potential", f"Rs. {total_showroom_leak:,}")
        
        # --- GRAPHING LEAKS PER CONSULTANT ---
        st.subheader("Revenue Leakage Visualization Per Executive")
        chart_data = pd.DataFrame({"Consultant": sc_names, "Revenue Leak (Rs.)": sc_leaks})
        st.bar_chart(chart_data, x="Consultant", y="Revenue Leak (Rs.)", color="#ff4757")
        
        # --- EXPORT REPORT LOGIC (PREMIUM EXECUTIVE LAYOUT) ---
        pdf = FPDF()
        pdf.add_page()
        
        # 1. Premium Header Banner
        pdf.set_fill_color(24, 28, 36) # Deep Slate/Charcoal
        pdf.rect(0, 0, 210, 42, 'F')
        
        pdf.set_font("Arial", 'B', 18)
        pdf.set_text_color(255, 255, 255)
        pdf.set_y(12)
        pdf.cell(0, 10, "PERFORMANCE AUDIT & PROFIT RECOVERY", ln=True, align='C')
        
        pdf.set_font("Arial", 'I', 10)
        pdf.set_text_color(170, 180, 195)
        pdf.cell(0, 5, f"Dealership: {dealer_name}  |  Manufacturer: {selected_brand}", ln=True, align='C')
        
        # 2. Executive Summary Block
        pdf.ln(20)
        pdf.set_fill_color(245, 247, 250) # Light Grey Box
        pdf.rect(10, 50, 190, 22, 'F')
        
        pdf.set_y(53)
        pdf.set_x(15)
        pdf.set_font("Arial", 'B', 11)
        pdf.set_text_color(40, 45, 55)
        pdf.cell(100, 6, "Audit Summary Profile:", ln=False)
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(214, 48, 49) # Premium Crimson Red
        pdf.cell(0, 6, f"Total Recovery Potential: Rs. {total_showroom_leak:,}", ln=True, align='R')
        
        pdf.set_x(15)
        pdf.set_font("Arial", '', 9)
        pdf.set_text_color(100, 110, 125)
        pdf.cell(0, 5, "Metrics evaluated against industry standard benchmarks (75% Test Drive, 30% Retail Conversion).", ln=True)
        
        # 3. Structured Data Table Headers
        pdf.ln(12)
        pdf.set_fill_color(45, 55, 72) # Dark Steel Header Row
        pdf.cell(50, 8, " Consultant Name", border=0, fill=True, ln=False)
        pdf.cell(20, 8, "Enquiries", border=0, fill=True, ln=False, align='C')
        pdf.cell(25, 8, "Delivered", border=0, fill=True, ln=False, align='C')
        pdf.cell(25, 8, "Target", border=0, fill=True, ln=False, align='C')
        pdf.cell(35, 8, "Revenue Leak", border=0, fill=True, ln=False, align='R')
        pdf.cell(35, 8, "   Training Module", border=0, fill=True, ln=True)
        
        # Reset text color and font for data rows
        pdf.set_font("Arial", '', 9)
        pdf.set_text_color(50, 55, 65)
        
        # 4. Populate Matrix Grid Rows cleanly
        alternate_row = False
        for idx, row in display_results_df.iterrows():
            # Stripe background for high readability
            if alternate_row:
                pdf.set_fill_color(248, 250, 252)
            else:
                pdf.set_fill_color(255, 255, 255)
                
            # Safely sanitize names and remove those broken bullet/emoji artifacts entirely
            safe_name = str(row['Consultant Name']).encode('ascii', 'ignore').decode('ascii').strip()
            clean_prescription = str(row['Training Prescription']).replace("📚 ", "").replace("🎯 ", "").replace("⚡ ", "")
            
            # Draw Data Row
            current_y = pdf.get_y()
            pdf.cell(50, 8, f" {safe_name}", fill=True, ln=False)
            pdf.cell(20, 8, str(row['Enquiries']), fill=True, ln=False, align='C')
            pdf.cell(25, 8, str(row['Retails Delivered']), fill=True, ln=False, align='C')
            pdf.cell(25, 8, str(row['Target Retails']), fill=True, ln=False, align='C')
            
            # Highlight non-zero leaks in dark red to emphasize value
            if row['raw_leak'] > 0:
                pdf.set_text_color(180, 40, 40)
                pdf.cell(35, 8, f"Rs. {row['raw_leak']:,} ", fill=True, ln=False, align='R')
                pdf.set_text_color(50, 55, 65)
            else:
                pdf.set_text_color(40, 160, 80) # Clean Green for zero leak
                pdf.cell(35, 8, "Rs. 0 ", fill=True, ln=False, align='R')
                pdf.set_text_color(50, 55, 65)
                
            pdf.cell(35, 8, f"  {clean_prescription}", fill=True, ln=True)
            alternate_row = not alternate_row
            
        # 5. Compile to safe download bytes
        pdf_bytes = pdf.output(dest='S').encode('latin-1', errors='ignore')
        
        st.write("") # Layout Spacing
        st.download_button("📥 Export Premium Consultant Audit (PDF)", data=pdf_bytes, file_name=f"Premium_SC_Audit_{dealer_name}.pdf", type="primary")
