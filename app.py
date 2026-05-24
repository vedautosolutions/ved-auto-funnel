import streamlit as st
from fpdf import FPDF
import urllib.parse
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import os

# --- 1. LIVE INDIAN BRAND MARKET BENCHMARKS ---
INDIAN_BRANDS = {
    "4-Wheeler": {
        "Aston Martin": 1200000, "Audi": 250000, "Bentley": 1500000, "BMW": 250000,
        "BYD": 100000, "Citroen": 50000, "Ferrari": 2000000, "Force Motors": 45000,
        "Honda Cars India": 60000, "Hyundai India": 55000, "Isuzu": 75000,
        "Jaguar Land Rover": 450000, "Jeep": 110000, "Kia India": 60000,
        "Lamborghini": 2000000, "Lexus": 350000, "Mahindra & Mahindra": 75000,
        "Maruti Suzuki": 40000, "Mercedes-Benz": 270000, "MG Motor India": 65000,
        "Nissan India": 45000, "Porsche": 800000, "Renault India": 35000,
        "Rolls-Royce": 2500000, "Skoda India": 80000, "Tata Motors": 50000,
        "Toyota Kirloskar": 85000, "Volkswagen India": 80000, "Volvo India": 300000
    },
    "2-Wheeler": {
        "Ather Energy": 12000, "Aprilia": 25000, "Bajaj Auto": 7500, "Benelli": 35000,
        "BGauss": 10000, "BMW Motorrad": 70000, "Ducati": 180000, "Harley-Davidson": 120000,
        "Hero MotoCorp": 5000, "Honda HMSI": 6000, "Indian Motorcycle": 250000,
        "Java / Yezdi": 14000, "Kawasaki": 60000, "KTM India": 18000, "Keeway": 25000,
        "Ola Electric": 9000, "Piaggio (Vespa)": 11000, "Royal Enfield": 16000,
        "Suzuki Two-Wheelers": 7500, "Triumph India": 45000, "TVS Motor": 6500, "Yamaha India": 8000
    }
}

BM = {"TD": 0.75, "RETAIL": 0.30, "CAPACITY": 20}

# --- URL PARAMETER DETECTION ---
query_params = st.query_params
url_category = query_params.get("category", "4-Wheeler")
default_index = 0 if url_category == "4-Wheeler" else 1

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="AutoLogic Pro", layout="wide")
st.title("🚗 AutoLogic Diagnostic Suite")
st.write("Professional Sales Funnel Audit & Revenue Recovery Engine")

# --- 3. SIDEBAR INPUTS ---
with st.sidebar:
    st.header("1. Audit Details")
    rep_name = st.text_input("Representative Name", value="Rajesh Kumar")
    dealer_name = st.text_input("Dealership Name", value="Om Sai Suzuki")
    
    st.divider()
    st.header("🏢 Live OEM Matrix")
    vehicle_type = st.radio("Vehicle Category", ["4-Wheeler", "2-Wheeler"], index=default_index, horizontal=True)
    brand_list = sorted(list(INDIAN_BRANDS[vehicle_type].keys()))
    selected_brand = st.selectbox("Select Manufacturer", brand_list)
    
    base_profit = INDIAN_BRANDS[vehicle_type][selected_brand]
    profit_per_unit = st.number_input("Target Profit Per Unit (Rs.)", value=base_profit, step=500 if vehicle_type == "2-Wheeler" else 5000)
    
    st.divider()
    st.header("2. Funnel Data")
    sc_count = st.number_input("Total Sales Consultants", min_value=1, value=10)
    enq = st.number_input("Total Enquiries", min_value=0, value=400)
    tds = st.number_input("Total Test Drives", min_value=0, value=100)
    bkgs = st.number_input("Total Bookings", min_value=0, value=50)
    retails = st.number_input("Total Retails", min_value=0, value=30)
    st.divider()
    user_phone = st.text_input("WhatsApp Number (Optional)", value="")

# --- 4. SESSION STATE LOGIC ---
if "audit_run" not in st.session_state:
    st.session_state.audit_run = False

if st.button("🚀 Run Sales Funnel Audit") or st.session_state.audit_run:
    st.session_state.audit_run = True

    if not rep_name or not dealer_name:
        st.error("⚠️ Please provide Representative and Dealer names in the sidebar.")
        st.session_state.audit_run = False
    else:
        # --- MATH ENGINE ---
        target_tds = round(enq * BM["TD"])
        target_retails = round(enq * BM["RETAIL"])
        target_bkgs = round(target_tds * 0.40)

        retail_gap = max(0, target_retails - retails)
        revenue_leak = retail_gap * profit_per_unit
        leak_per_sc = round(revenue_leak / sc_count) if sc_count > 0 else 0

        td_ratio = (tds / enq) * 100 if enq > 0 else 0
        booking_ratio = (bkgs / tds) * 100 if tds > 0 else 0
        retail_ratio = (retails / enq) * 100 if enq > 0 else 0
        score = min(round((retail_ratio / (BM["RETAIL"] * 100)) * 100), 100) if enq > 0 else 0

        # --- DISPLAY SECTION 1: FINANCIALS ---
        st.header("1. Financial Opportunity Cost")
        f1, f2, f3 = st.columns(3)
        f1.metric("Efficiency Score", f"{score}/100")
        f2.metric("Monthly Revenue Leak", f"Rs. {revenue_leak:,}", delta=f"-{retail_gap} Units", delta_color="inverse")
        f3.metric("Loss Per Consultant", f"Rs. {leak_per_sc:,}")
        
        # --- DISPLAY SECTION 2: BENCHMARKS ---
        st.header("2. Funnel Conversion Benchmarks")
        col_table, col_chart = st.columns([1.2, 0.8])
        
        with col_table:
            comparison_df = pd.DataFrame({
                "Metric": ["Enquiry to Test Drive", "Test Drive to Booking", "Overall Retail Conversion"],
                "Actual (Vol / %)": [f"{tds} ({td_ratio:.1f}%)", f"{bkgs} ({booking_ratio:.1f}%)", f"{retails} ({retail_ratio:.1f}%)"],
                "Benchmark (Vol / %)": [f"{target_tds} (75.0%)", f"{target_bkgs} (40.0%)", f"{target_retails} (30.0%)"],
                "Status": ["✅ OK" if td_ratio >= 75 else "⚠️ CHECK", "✅ OK" if booking_ratio >= 40 else "⚠️ CHECK", "✅ OK" if retail_ratio >= 30 else "⚠️ CHECK"]
            })
            st.table(comparison_df)
        
        with col_chart:
            chart_data = pd.DataFrame({"Stage": ["Enq", "TD", "Bkg", "Ret"], "Count": [enq, tds, bkgs, retails]})
            st.bar_chart(chart_data, x="Stage", y="Count", color="#1f497d")

        # GENERATE STATIC CHART FOR THE PDF
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.bar(["Enq", "TD", "Bkg", "Ret"], [enq, tds, bkgs, retails], color="#1f497d")
        ax.set_ylabel("Volume")
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.tight_layout()
        chart_filename = "temp_chart.png"
        plt.savefig(chart_filename, dpi=200)
        plt.close()

        # --- DISPLAY SECTION 3: STRATEGIC ACTIONS ---
        st.header("3. Strategic Action Plan")
        actions = []
        if td_ratio < 75:
            actions.append(f"ENQUIRY MANAGEMENT: Low TD ratio ({td_ratio:.1f}%). Customers aren't experiencing the product.")
        if booking_ratio < 40:
            actions.append(f"CLOSING RATIO: Low Booking conversion ({booking_ratio:.1f}%). Team needs closing skill intervention.")
        if enq > (sc_count * BM["CAPACITY"]):
            hiring_need = round((enq / BM["CAPACITY"]) - sc_count)
            actions.append(f"MANPOWER ALERT: Volume suggests a need for {hiring_need} additional consultants.")
        
        for a in actions:
            st.warning(a)

        # --- DISPLAY SECTION 4: GROWTH PROJECTION ---
        st.header("4. Growth Projection")
        g1, g2 = st.columns(2)
        with g1:
            st.write(f"**Current State Gross Profit:** Rs. {retails * profit_per_unit:,} / Month")
        with g2:
            st.write(f"**Optimized State Gross Profit:** Rs. {target_retails * profit_per_unit:,} / Month")
        st.success(f"### Potential Monthly Growth: +Rs. {revenue_leak:,}")

        # --- PDF GENERATOR LOGIC ---
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(31, 73, 125); pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_font("Arial", 'B', 20); pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 18, "SALES FUNNEL AUDIT", ln=True, align='C')
        pdf.set_font("Arial", '', 10); pdf.cell(0, 5, f"Brand Portfolio Focus: {selected_brand} ({vehicle_type})", ln=True, align='C')
        pdf.ln(20); pdf.set_text_color(51, 51, 51); pdf.set_font("Arial", 'B', 11)
        pdf.cell(100, 10, f"CLIENT: {dealer_name.upper()}")
        pdf.cell(90, 10, f"REPRESENTATIVE: {rep_name.upper()}", ln=True, align='R')
        pdf.ln(5); pdf.set_fill_color(248, 249, 250); pdf.set_font("Arial", 'B', 12); pdf.set_text_color(31, 73, 125)
        pdf.cell(0, 10, " 1. FINANCIAL OPPORTUNITY COST", ln=True, fill=True)
        pdf.set_font("Arial", '', 10); pdf.set_text_color(51, 51, 51); pdf.ln(2)
        pdf.cell(0, 7, f"Efficiency Score: {score}/100", ln=True)
        pdf.cell(0, 7, f"Monthly Revenue Leak: Rs. {revenue_leak:,} (-{retail_gap} Units)", ln=True)
        pdf.cell(0, 7, f"Loss Per Consultant: Rs. {leak_per_sc:,}", ln=True)
        pdf.ln(5); pdf.set_font("Arial", 'B', 12); pdf.set_text_color(31, 73, 125)
        pdf.cell(0, 10, " 2. FUNNEL CONVERSION BENCHMARKS", ln=True, fill=True)
        pdf.set_font("Arial", 'B', 9); pdf.set_text_color(255, 255, 255); pdf.set_fill_color(31, 73, 125); pdf.ln(2)
        pdf.cell(55, 10, " METRIC", 1, 0, 'L', True)
        pdf.cell(50, 10, " ACTUAL (VOL / %)", 1, 0, 'L', True)
        pdf.cell(50, 10, " BENCHMARK (VOL / %)", 1, 0, 'L', True)
        pdf.cell(35, 10, " STATUS", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 9); pdf.set_text_color(51, 51, 51)
        pdf.cell(55, 9, " Enquiry to Test Drive", 1)
        pdf.cell(50, 9, f" {tds} ({td_ratio:.1f}%)", 1)
        pdf.cell(50, 9, f" {target_tds} (75.0%)", 1)
        pdf.cell(35, 9, f"  {'CHECK' if td_ratio < 75 else 'OK'}", 1, 1)
        pdf.cell(55, 9, " Test Drive to Booking", 1)
        pdf.cell(50, 9, f" {bkgs} ({booking_ratio:.1f}%)", 1)
        pdf.cell(50, 9, f" {target_bkgs} (40.0%)", 1)
        pdf.cell(35, 9, f"  {'CHECK' if booking_ratio < 40 else 'OK'}", 1, 1)
        pdf.cell(55, 9, " Overall Retail Conversion", 1)
        pdf.cell(50, 9, f" {retails} ({retail_ratio:.1f}%)", 1)
        pdf.cell(50, 9, f" {target_retails} (30.0%)", 1)
        pdf.cell(35, 9, f"  {'CHECK' if retail_ratio < 30 else 'OK'}", 1, 1)
        pdf.ln(4)
        pdf.image(chart_filename, x=55, y=pdf.get_y(), w=100)
        pdf.ln(58)
        pdf.set_font("Arial", 'B', 12); pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 10, " 3. STRATEGIC ACTION PLAN", ln=True, fill=True)
        pdf.set_font("Arial", '', 10); pdf.set_text_color(51, 51, 51); pdf.ln(2)
        for a in actions:
            pdf.multi_cell(0, 6, f"- {a}")
        pdf.ln(3); pdf.set_font("Arial", 'B', 12); pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 10, " 4. GROWTH PROJECTION", ln=True, fill=True)
        pdf.set_font("Arial", '', 10); pdf.set_text_color(51, 51, 51); pdf.ln(2)
        pdf.cell(0, 6, f"Current State Gross Profit: Rs. {retails * profit_per_unit:,} / Month", ln=True)
        pdf.cell(0, 6, f"Optimized State Gross Profit: Rs. {target_retails * profit_per_unit:,} / Month", ln=True)
        pdf.set_font("Arial", 'B', 10); pdf.set_text_color(31, 73, 125)
        pdf.cell(0, 8, f"Potential Monthly Growth: +Rs. {revenue_leak:,}", ln=True)

        st.divider()
        st.subheader("📤 Distribute Document & Next Steps")
        
        c1, c2, c3 = st.columns([1, 1, 2])
        with c1:
            pdf_data = pdf.output(dest='S').encode('latin-1', errors='ignore')
            st.download_button("📥 Download PDF Report", data=pdf_data, file_name=f"Funnel_Audit_{dealer_name}.pdf", type="primary")
        with c2:
            if user_phone:
                wa_msg = f"Sales Funnel Audit for {dealer_name} ({selected_brand}) is ready. Score: {score}/100. Potential Growth: Rs. {revenue_leak:,}."
                st.link_button("📲 Share via WhatsApp", f"https://wa.me/{user_phone}?text={urllib.parse.quote(wa_msg)}")
            else:
                st.info("💡 Add number for WhatsApp sharing.")
        with c3:
            if st.button("🔄 Reset Audit"):
                if os.path.exists(chart_filename): os.remove(chart_filename)
                st.session_state.audit_run = False
                st.rerun()

        if os.path.exists(chart_filename): os.remove(chart_filename)

        # --- NEW CONVERSION HUB DESIGN (Item 1 & 2) ---
        st.write("---")
        st.subheader("💼 Ready to Plug the Revenue Leaks?")
        st.write("Take the next step to deploy custom Training Prescriptions and SC-wise performance logic in your showroom.")
        
        button_col1, button_col2, button_col3 = st.columns(3)
        
        with button_col1:
            # 1. Dynamic Email Builder
            email_target = "vedautosolutions@gmail.com"  # Change to your real agency email address
            email_subject = urllib.parse.quote(f"Full-Fledged Funnel Audit Request - {dealer_name}")
            email_body = urllib.parse.quote(
                f"Hi Ved Auto Solutions Team,\n\n"
                f"We just ran our initial health check for {dealer_name} and identified an estimated monthly leakage of Rs. {revenue_leak:,}.\n\n"
                f"We want to schedule a full-fledged audit to look into our SC-wise data, training gaps, and process fixes.\n\n"
                f"Best regards,\n"
                f"Management Team"
            )
            mail_url = f"mailto:{email_target}?subject={email_subject}&body={email_body}"
            st.link_button("📧 Request Full Audit via Email", mail_url, use_container_width=True)
            
        with button_col2:
            # 2. Return to Top of Landing Page (Uses JS execution via iframe target parent)
            # Instructs the browser window to hop back to the master page home banner
            st.link_button("🏠 Return to Landing Home", "javascript:window.parent.location.hash=''; window.parent.scrollTo(0,0);", use_container_width=True)
            
        with button_col3:
            # 3. Future Audit Deep Dive Target Route Link
            # While building, this loops straight to your direct booking channel/WhatsApp
            st.link_button("📊 Explore Premium Corporate Solutions", "https://wa.me/918764628352?text=I%20want%20to%20know%20more%20about%20the%20premium%20retainer%20and%20full%20audit%20models.", use_container_width=True)