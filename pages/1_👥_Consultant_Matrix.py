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
st.set_page_config(page_title="Premium | Consultant Performance Matrix", layout="wide")

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
st.title("💎 Tier 2: Premium Consultant Diagnostics")
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
                
                if uploaded_file.name.endswith(".csv"):
                    raw_df = pd.read_csv(uploaded_file)
                else:
                    excel_file = pd.ExcelFile(uploaded_file)
                    sheet_names = excel_file.sheet_names
                    
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

                if raw_df is None or raw_df.empty or len(raw_df.columns) < 2:
                    st.error("❌ **Invalid Document Profile:** The system analyzed this file but could not detect a valid Sales Consultant performance matrix. Please upload a raw DMS/ERP performance report.")
                    st.stop()

                if target_sheet:
                    st.toast(f"🎯 AI successfully identified data matrix in tab: '{target_sheet}'", icon="✅")

                file_summary_text = raw_df.to_string()

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
                
                clean_json_string = response.text.strip()
                if clean_json_string.startswith("```"):
                    clean_json_string = clean_json_string.split("json")[-1].split("```")[0].strip()
                
                parsed_data = json.loads(clean_json_string)
                st.session_state.clean_df = pd.DataFrame(parsed_data)
                st.success("🎉 Data successfully structured by AI agent!")
                
            except Exception as e:
                st.error(f"Failed to process dataset: {str(e)}")

if st.session_state.clean_df is not None:
    st.subheader("Verify Processed Sales Consultant Roster:")
    edited_df = st.data_editor(st.session_state.clean_df, num_rows="dynamic", width="stretch")
    
    if st.button("📊 Calculate Individual Leaks & Training Prescriptions"):
        st.header("2. Analytical Breakdown Matrix")
        
        processed_rows = []
        total_showroom_leak = 0
        total_enq = 0
        total_tds = 0
        total_bkgs = 0
        total_retails = 0
        total_target_retails = 0
        
        sc_names = []
        sc_leaks = []
        
        for index, row in edited_df.iterrows():
            name = str(row["Consultant Name"])
            enq = int(row["Enquiries"])
            tds = int(row["Test Drives"])
            bkgs = int(row["Bookings"])
            retails = int(row["Retails"])
            
            total_enq += enq
            total_tds += tds
            total_bkgs += bkgs
            total_retails += retails
            
            target_tds = round(enq * BM["TD"])
            target_retails = round(enq * BM["RETAIL"])
            total_target_retails += target_retails
            
            sc_retail_gap = max(0, target_retails - retails)
            sc_leakage_val = sc_retail_gap * profit_per_unit
            total_showroom_leak += sc_leakage_val
            
            td_ratio = (tds / enq * 100) if enq > 0 else 0
            bkg_ratio = (bkgs / tds * 100) if tds > 0 else 0
            
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
        
        overall_td_percentage = (total_tds / total_enq * 100) if total_enq > 0 else 0
        overall_retail_percentage = (total_retails / total_enq * 100) if total_enq > 0 else 0
        showroom_efficiency = round((total_retails / max(1, total_target_retails)) * 100)
        showroom_efficiency = min(100, max(0, showroom_efficiency))
        
        current_gross_profit = total_retails * profit_per_unit
        optimized_gross_profit = max(total_retails, total_target_retails) * profit_per_unit
        
        st.subheader("Revenue Leakage Visualization Per Executive")
        chart_data = pd.DataFrame({"Consultant": sc_names, "Revenue Leak (Rs.)": sc_leaks})
        st.bar_chart(chart_data, x="Consultant", y="Revenue Leak (Rs.)", color="#ff4757")
        
        # --- GRAPHING NATIVE FUNNEL CHART FOR EXECUTIVE DASHBOARD ---
        fig, ax = plt.subplots(figsize=(5.5, 3.8))
        funnel_labels = ['Enquiries', 'Test Drives', 'Bookings', 'Retails']
        funnel_volumes = [total_enq, total_tds, total_bkgs, total_retails]
        
        # Clean corporate layout colors for infographic aesthetics
        bars = ax.bar(funnel_labels, funnel_volumes, color=['#2c3e50', '#34495e', '#2980b9', '#16a085'], width=0.6)
        ax.set_ylabel('Pipeline Volume', fontsize=9, fontweight='bold', color='#2c3e50')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#bdc3c7')
        ax.spines['bottom'].set_color('#bdc3c7')
        ax.tick_params(axis='both', colors='#34495e', labelsize=8)
        
        # Add values cleanly on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:,}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8, fontweight='bold', color='#2c3e50')
                        
        plt.tight_layout()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
            fig.savefig(tmpfile.name, dpi=300)
            chart_img_path = tmpfile.name
        plt.close(fig)

        # =========================================================================
        # ==================== ADVANCED PREMIUM PDF ENGINE =========================
        # =========================================================================
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # --- PAGE 1: DOSSIER INFOGRAPHIC EXECUTIVE OVERVIEW ---
        pdf.add_page()
        
        # 1. Premium Geometric Top Header Banner
        pdf.set_fill_color(26, 37, 48) # Luxury Midnight Navy
        pdf.rect(0, 0, 210, 48, 'F')
        
        # Accent Gold Bar
        pdf.set_fill_color(197, 160, 89) # Premium Dealer Gold Accent
        pdf.rect(0, 48, 210, 2, 'F')
        
        pdf.set_font("Arial", 'B', 20)
        pdf.set_text_color(255, 255, 255)
        pdf.set_y(14)
        pdf.cell(0, 10, "EXECUTIVE CONVERSION AUDIT & PROFIT RECOVERY", ln=True, align='C')
        
        pdf.set_font("Arial", 'M', 10)
        pdf.set_text_color(200, 210, 220)
        pdf.cell(0, 6, f"NETWORK ID: {dealer_name.upper()}   |   PORTFOLIO TARGET MANUFACTURER: {selected_brand.upper()}", ln=True, align='C')
        
        # 2. Infographic Row: Macro Dashboard Cards (Left: Opportunity Cost, Right: Efficiency Status)
        pdf.ln(18)
        
        # Left Block: Financial Liability Card
        pdf.set_fill_color(253, 242, 242) # Crimson Tint
        pdf.rect(10, 62, 92, 34, 'F')
        pdf.set_fill_color(214, 48, 49) # Deep Red Sidebar Line
        pdf.rect(10, 62, 3, 34, 'F')
        
        pdf.set_y(65)
        pdf.set_x(17)
        pdf.set_font("Arial", 'B', 10)
        pdf.set_text_color(120, 30, 30)
        pdf.cell(80, 5, "TOTAL MONTHLY REVENUE LEAKAGE", ln=True)
        pdf.set_x(17)
        pdf.set_font("Arial", 'B', 15)
        pdf.set_text_color(180, 20, 20)
        pdf.cell(80, 8, f"Rs. {total_showroom_leak:,}", ln=True)
        pdf.set_x(17)
        pdf.set_font("Arial", '', 9)
        pdf.set_text_color(100, 70, 70)
        avg_leak_per_sc = round(total_showroom_leak / max(1, len(edited_df)))
        pdf.cell(80, 5, f"Per Consultant Pro-Rata Loss: Rs. {avg_leak_per_sc:,}", ln=True)
        
        # Right Block: System Efficiency Card
        pdf.set_y(62)
        pdf.set_fill_color(240, 247, 241) # Emerald Tint
        pdf.rect(108, 62, 92, 34, 'F')
        pdf.set_fill_color(38, 166, 91) # Deep Emerald Sidebar Line
        pdf.rect(108, 62, 3, 34, 'F')
        
        pdf.set_y(65)
        pdf.set_x(115)
        pdf.set_font("Arial", 'B', 10)
        pdf.set_text_color(20, 80, 40)
        pdf.cell(80, 5, "SHOWROOM EFFICIENCY RATING", ln=True)
        pdf.set_x(115)
        pdf.set_font("Arial", 'B', 16)
        if showroom_efficiency >= 75:
            pdf.set_text_color(38, 166, 91)
        else:
            pdf.set_text_color(214, 48, 49)
        pdf.cell(80, 8, f"{showroom_efficiency} / 100", ln=True)
        pdf.set_x(115)
        pdf.set_font("Arial", '', 9)
        pdf.set_text_color(60, 90, 70)
        pdf.cell(80, 5, f"Roster Pipeline Size: {len(edited_df)} Consultants Tracked", ln=True)
        
        # 3. Showroom Funnel Conversion Benchmarks Grid
        pdf.set_y(104)
        pdf.set_x(10)
        pdf.set_font("Arial", 'B', 11)
        pdf.set_text_color(26, 37, 48)
        pdf.cell(0, 8, "GLOBAL REPORTING WORKFLOW STATUS & BENCHMARKS", ln=True)
        
        # Header Row
        pdf.set_font("Arial", 'B', 9)
        pdf.set_text_color(255, 255, 255)
        pdf.set_fill_color(44, 62, 80) # Steel Navy
        pdf.cell(70, 8, " METRIC FLOW PROFILE", fill=True, ln=False)
        pdf.cell(40, 8, "ACTUAL CONVERSION", fill=True, ln=False, align='C')
        pdf.cell(40, 8, "TARGET BENCHMARK", fill=True, ln=False, align='C')
        pdf.cell(40, 8, "STATUS ASSESSMENT ", fill=True, ln=True, align='R')
        
        pdf.set_font("Arial", '', 9)
        pdf.set_text_color(40, 45, 55)
        
        # Row 1
        pdf.cell(70, 8.5, " Enquiry to Test Drive Volume", border="B", ln=False)
        pdf.cell(40, 8.5, f"{total_tds:,} ({overall_td_percentage:.1f}%)", border="B", ln=False, align='C')
        pdf.cell(40, 8.5, f"{round(total_enq * BM['TD']):,} (75.0%)", border="B", ln=False, align='C')
        if overall_td_percentage >= 75:
            pdf.set_text_color(38, 166, 91); pdf.set_font("Arial", 'B', 9)
            pdf.cell(40, 8.5, "OPTIMAL ", border="B", ln=True, align='R')
        else:
            pdf.set_text_color(214, 48, 49); pdf.set_font("Arial", 'B', 9)
            pdf.cell(40, 8.5, "CRITICAL LEAK ", border="B", ln=True, align='R')
        pdf.set_text_color(40, 45, 55); pdf.set_font("Arial", '', 9)
        
        # Row 2
        pdf.cell(70, 8.5, " Initial Pipeline to Retail Conversion", border="B", ln=False)
        pdf.cell(40, 8.5, f"{total_retails:,} ({overall_retail_percentage:.1f}%)", border="B", ln=False, align='C')
        pdf.cell(40, 8.5, f"{total_target_retails:,} (30.0%)", border="B", ln=False, align='C')
        if overall_retail_percentage >= 30:
            pdf.set_text_color(38, 166, 91); pdf.set_font("Arial", 'B', 9)
            pdf.cell(40, 8.5, "OPTIMAL ", border="B", ln=True, align='R')
        else:
            pdf.set_text_color(214, 48, 49); pdf.set_font("Arial", 'B', 9)
            pdf.cell(40, 8.5, "CRITICAL LEAK ", border="B", ln=True, align='R')
        pdf.set_text_color(40, 45, 55); pdf.set_font("Arial", '', 9)
        
        # 4. Asymmetric Infographic Content Area (Left Infographic Graph, Right Strategic Text Block)
        pdf.image(chart_img_path, x=8, y=140, w=92)
        
        # Right Side Data Cards
        # Card A: Forward Projections Block
        pdf.set_y(140)
        pdf.set_x(106)
        pdf.set_font("Arial", 'B', 11)
        pdf.set_text_color(26, 37, 48)
        pdf.cell(94, 6, "PIPELINE REVENUE UPSIDE MAP", ln=True)
        
        pdf.set_fill_color(245, 247, 250)
        pdf.rect(106, 148, 94, 26, 'F')
        
        pdf.set_y(151)
        pdf.set_x(110)
        pdf.set_font("Arial", '', 9)
        pdf.set_text_color(80, 90, 100)
        pdf.cell(50, 5, "Current Monthly Pipeline GP:")
        pdf.set_font("Arial", 'B', 9); pdf.set_text_color(40, 45, 50)
        pdf.cell(36, 5, f"Rs. {current_gross_profit:,}", ln=True, align='R')
        
        pdf.set_x(110)
        pdf.set_font("Arial", '', 9); pdf.set_text_color(80, 90, 100)
        pdf.cell(50, 5, "Optimized Benchmark GP:")
        pdf.set_font("Arial", 'B', 9); pdf.set_text_color(40, 45, 50)
        pdf.cell(36, 5, f"Rs. {optimized_gross_profit:,}", ln=True, align='R')
        
        pdf.set_x(110)
        pdf.set_font("Arial", 'B', 9); pdf.set_text_color(38, 166, 91)
        pdf.cell(50, 6, "Net Revenue Growth Upside:")
        pdf.cell(36, 6, f"+Rs. {total_showroom_leak:,}", ln=True, align='R')
        
        # Card B: Strategic Action Diagnosis Text
        pdf.set_y(178)
        pdf.set_x(106)
        pdf.set_font("Arial", 'B', 11); pdf.set_text_color(26, 37, 48)
        pdf.cell(94, 6, "CORE DIAGNOSTIC ACTION MATRIX", ln=True)
        pdf.ln(2)
        
        pdf.set_font("Arial", '', 9); pdf.set_text_color(70, 80, 95)
        if overall_td_percentage < 75:
            pdf.set_x(106)
            pdf.multi_cell(94, 5, "[-] CRITICAL TEST DRIVE LEAKAGE: Total conversion lags benchmark target of 75%. Customers are exiting the ecosystem without experiencing the product. Implement mandatory demo routines immediately.")
            pdf.ln(1)
        if overall_retail_percentage < 30:
            pdf.set_x(106)
            pdf.multi_cell(94, 5, "[-] PIPELINE CLOSING BOTTLENECK: High dropout noted after transaction logging. Deploy strategic objection-handling training models and review finance partner integrations.")

        # =========================================================================
        # ================= PAGE 2+: CUSTOMER LEDGER MATRIX APPENDIX ================
        # =========================================================================
        pdf.add_page()
        
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(26, 37, 48)
        pdf.cell(0, 8, "APPENDIX: GRANULAR PERFORMANCE AUDIT ARRAYS", ln=True)
        pdf.set_font("Arial", 'I', 9)
        pdf.set_text_color(110, 120, 135)
        pdf.cell(0, 5, "Individual matrix extractions mapped down to consultant pipeline ratios.", ln=True)
        pdf.ln(5)
        
        # High Contrast Luxury Matrix Headers
        pdf.set_font("Arial", 'B', 9)
        pdf.set_text_color(255, 255, 255)
        pdf.set_fill_color(26, 37, 48) # Match Midnight Core Profile Title Block
        pdf.cell(46, 9, " CONSULTANT EXECUTIVE ARRAY", fill=True, ln=False)
        pdf.cell(16, 9, "ENQ", fill=True, ln=False, align='C')
        pdf.cell(20, 9, "DELIVERED", fill=True, ln=False, align='C')
        pdf.cell(18, 9, "TARGET", fill=True, ln=False, align='C')
        pdf.cell(32, 9, "REVENUE LEAKAGE", fill=True, ln=False, align='R')
        pdf.cell(58, 9, "  CORE REMEDIATION TARGET FIX", fill=True, ln=True)
        
        pdf.set_font("Arial", '', 9)
        pdf.set_text_color(40, 45, 55)
        
        alternate_row = False
        for idx, row in display_results_df.iterrows():
            # Alternating clean zebra striping for crisp look
            if alternate_row:
                pdf.set_fill_color(246, 249, 252)
            else:
                pdf.set_fill_color(255, 255, 255)
                
            safe_name = str(row['Consultant Name']).encode('ascii', 'ignore').decode('ascii').strip().upper()
            clean_prescription = str(row['Training Prescription']).replace("📚 ", "").replace("🎯 ", "").replace("⚡ ", "")
            
            pdf.cell(46, 8.5, f" {safe_name[:22]}", fill=True, ln=False, border="B")
            pdf.cell(16, 8.5, str(row['Enquiries']), fill=True, ln=False, align='C', border="B")
            pdf.cell(20, 8.5, str(row['Retails Delivered']), fill=True, ln=False, align='C', border="B")
            pdf.cell(18, 8.5, str(row['Target Retails']), fill=True, ln=False, align='C', border="B")
            
            # Highlight non-zero losses dynamically in warning crimson bold text
            if row['raw_leak'] > 0:
                pdf.set_text_color(190, 30, 30); pdf.set_font("Arial", 'B', 9)
                pdf.cell(32, 8.5, f"Rs. {row['raw_leak']:,} ", fill=True, ln=False, align='R', border="B")
                pdf.set_text_color(40, 45, 55); pdf.set_font("Arial", '', 9)
            else:
                pdf.set_text_color(38, 166, 91) # Clean green for 0 leak
                pdf.cell(32, 8.5, "Rs. 0 ", fill=True, ln=False, align='R', border="B")
                pdf.set_text_color(40, 45, 55)
                
            pdf.cell(58, 8.5, f"  {clean_prescription}", fill=True, ln=True, border="B")
            alternate_row = not alternate_row
            
        try:
            os.unlink(chart_img_path)
        except:
            pass
            
        pdf_bytes = pdf.output(dest='S').encode('latin-1', errors='ignore')
        
        st.write("") 
        st.download_button("📥 Export Premium Consultant Audit (PDF)", data=pdf_bytes, file_name=f"Premium_SC_Audit_{dealer_name}.pdf", type="primary")
