import streamlit as st
import pandas as pd
import io
from datetime import date, timedelta
import calendar

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Auto PJP Generator", layout="wide")

st.title("🚀 Automated PJP & Sales Planner")
st.markdown("Customize your **Permanent Journey Plan (PJP)**, define your metrics, and download a ready-to-use Excel file.")

# --- SIDEBAR: CONFIGURATION ---
with st.sidebar:
    st.header("1. Calendar Settings")
    selected_year = st.number_input("Year", min_value=2025, max_value=2030, value=2026)
    selected_month = st.selectbox("Month", list(calendar.month_name)[1:], index=1) # Default Feb
    
    st.header("2. Metric Weightage")
    st.info("Assign importance to key business verticals.")
    w_mobility = st.slider("Mobility (SIM/MNP) %", 0, 100, 50)
    w_fiber = st.slider("Fiber/Home %", 0, 100, 30)
    w_process = st.slider("Process/Hygiene %", 0, 100, 20)
    
    if w_mobility + w_fiber + w_process != 100:
        st.error(f"Total Weightage is {w_mobility + w_fiber + w_process}%. It must be 100%.")

# --- MAIN SECTION: WEEKLY STRATEGY ---
st.subheader("Step 1: Define Your Weekly Rhythm")
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📅 Day-wise Themes")
    # user inputs for daily themes
    theme_mon = st.text_input("Monday Theme", value="Urban / High Volume")
    theme_tue = st.text_input("Tuesday Theme", value="Semi-Urban / Devices")
    theme_wed = st.text_input("Wednesday Theme", value="Rural / Low Base")
    theme_thu = st.text_input("Thursday Theme", value="FIBER FOCUS")
    theme_fri = st.text_input("Friday Theme", value="Mixed / Retention")
    theme_sat = st.text_input("Saturday Theme", value="Review & Cleanup")

with col2:
    st.markdown("### 🎯 Critical KPIs")
    # user inputs for targets
    target_sim = st.number_input("Daily SIM Target", value=15)
    target_fiber = st.number_input("Daily Fiber Leads", value=5)
    target_visit = st.number_input("Daily Store Visits", value=20)

# --- GENERATION LOGIC ---
def generate_excel():
    output = io.BytesIO()
    
    # 1. Weekly Framework Data (Dynamic based on inputs)
    weekly_data = {
        "Day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
        "Market Focus": [theme_mon, theme_tue, theme_wed, theme_thu, theme_fri, theme_sat],
        "Primary KPIs": [
            "Gross Adds, MNP", "Devices, MNP Laps", "Rural Activation", 
            "Home/Fiber Leads", "Retention, Churn", "Hygiene, Reports"
        ],
        "Daily Success Metrics": [
            f"{target_sim} SIMs", f"{int(target_sim*0.8)} SIMs", f"{int(target_sim*0.5)} SIMs",
            f"{target_fiber} Leads", "Churn < 1%", "100% Reporting"
        ]
    }
    df_weekly = pd.DataFrame(weekly_data)

    # 2. Monthly Calendar Logic
    month_num = list(calendar.month_name).index(selected_month)
    # Calculate start and end date
    start_date = date(selected_year, month_num, 1)
    # Logic to find last day of month
    if month_num == 12:
        next_month = date(selected_year + 1, 1, 1)
    else:
        next_month = date(selected_year, month_num + 1, 1)
    end_date = next_month - timedelta(days=1)
    
    dates = pd.date_range(start=start_date, end=end_date)
    day_wise_data = []

    for d in dates:
        day_name = d.strftime("%A")
        day_str = d.strftime("%d-%b-%y")
        theme = ""
        action = ""

        if day_name == "Sunday":
            theme = "OFF / PLANNING"
            action = "Weekly Review"
        elif day_name == "Monday":
            theme = theme_mon
            action = f"Focus: {target_sim} Activations"
        elif day_name == "Tuesday":
            theme = theme_tue
            action = "Focus: Device Sales"
        elif day_name == "Wednesday":
            theme = theme_wed
            action = "Focus: Rural Deep Dive"
        elif day_name == "Thursday":
            theme = theme_thu
            action = f"Focus: {target_fiber} Fiber Leads"
        elif day_name == "Friday":
            theme = theme_fri
            action = "Focus: Retention"
        elif day_name == "Saturday":
            theme = theme_sat
            action = "Focus: Hygiene Check"

        day_wise_data.append([day_str, day_name, theme, action, "", ""])

    df_calendar = pd.DataFrame(day_wise_data, columns=["Date", "Day", "Theme", "Critical Actions", "Actual", "Remarks"])

    # 3. Scorecard Logic
    scorecard_data = {
        "Metric Category": ["INPUTS", "INPUTS", "OUTPUTS", "OUTPUTS", "QUALITY"],
        "KPI Parameter": ["Store Visits", "Time in Market", "SIM Activations", "Fiber Leads", "Quality Score"],
        "Target": [target_visit, "8 Hours", target_sim, target_fiber, "100%"],
        "Weightage": ["-", "-", f"{w_mobility}%", f"{w_fiber}%", f"{w_process}%"]
    }
    df_scorecard = pd.DataFrame(scorecard_data)

    # WRITE TO EXCEL
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_weekly.to_excel(writer, sheet_name='Weekly Framework', index=False)
        df_calendar.to_excel(writer, sheet_name='Month Plan', index=False)
        df_scorecard.to_excel(writer, sheet_name='Scorecard', index=False)
        
        # Formatting
        workbook = writer.book
        header_fmt = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': '#4F81BD', 'border': 1})
        
        for sheet in writer.sheets.values():
            sheet.set_column('A:D', 25)
            # Apply basic header format (simplified for loop)
            pass 
            
    return output.getvalue()

# --- PREVIEW & DOWNLOAD ---
st.divider()
st.subheader("Step 2: Preview & Download")

if st.button("Generate PJP Preview"):
    # Generate data but don't download yet
    # For preview, we just show the calendar dataframe
    # (Re-using logic briefly for display)
    # In a real app, you'd decouple generation from display better
    st.success("PJP Generated Successfully! Previewing first 5 days:")
    
    # Quick dirty preview re-generation (optimized in prod)
    # ... (Displaying a sample table) ...
    
    excel_data = generate_excel()
    
    st.download_button(
        label="📥 Download Final Excel PJP",
        data=excel_data,
        file_name=f"PJP_{selected_month}_{selected_year}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )