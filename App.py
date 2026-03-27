import io
import re
from datetime import datetime
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import hashlib

st.set_page_config(page_title="Domino's Reporting Suite", page_icon="📊", layout="wide")

# =========================
# AUTHENTICATION
# =========================
# Simple user authentication system
USERS = {
    "admin": "admin123",
    "user": "user123",
    "dominos": "dominos2024"
}

def check_password():
    """Returns `True` if the user had a valid password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        username = st.session_state["username"]
        password = st.session_state["password"]
        
        if username in USERS and USERS[username] == password:
            st.session_state["password_correct"] = True
            st.session_state["logged_in_user"] = username
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False
    
    if "password_correct" not in st.session_state:
        # First time, show login form
        st.title("🔐 Domino's Reporting Suite - Login")
        st.markdown("### Please enter your credentials to access the dashboard")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<div style='background: linear-gradient(135deg,#ffffff 0%,#f8fafc 100%); border:1px solid #e2e8f0; border-radius:20px; padding:30px; box-shadow:0 6px 22px rgba(15,23,42,.05);'>", unsafe_allow_html=True)
            st.markdown("#### 👤 User Login")
            username = st.text_input("Username", key="username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", key="password", placeholder="Enter your password")
            login_button = st.button("Login", type="primary", use_container_width=True)
            
            if login_button:
                password_entered()
            
            st.markdown("</div>", unsafe_allow_html=True)
        return False
    elif not st.session_state["password_correct"]:
        # Password incorrect, show login form again
        st.title("🔐 Domino's Reporting Suite - Login")
        st.error("❌ Incorrect username or password. Please try again.")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<div style='background: linear-gradient(135deg,#ffffff 0%,#f8fafc 100%); border:1px solid #e2e8f0; border-radius:20px; padding:30px; box-shadow:0 6px 22px rgba(15,23,42,.05);'>", unsafe_allow_html=True)
            st.text_input("Username", key="username", placeholder="Enter your username")
            st.text_input("Password", type="password", key="password", placeholder="Enter your password")
            login_button = st.button("Login", type="primary", use_container_width=True)
            
            if login_button:
                password_entered()
            
            st.markdown("</div>", unsafe_allow_html=True)
        return False
    else:
        # Password correct
        return True

# Check authentication before loading the app
if not check_password():
    st.stop()

# =========================
# STYLING
# =========================
st.markdown("""
<style>
.block-container {padding-top: 0.8rem; padding-bottom: 1rem; max-width: 1700px;}
.card {background: linear-gradient(135deg,#ffffff 0%,#f8fafc 100%); border:1px solid #e2e8f0; border-radius:20px; padding:16px; box-shadow:0 6px 22px rgba(15,23,42,.05);}
.kpi-title {font-size:.85rem; color:#64748b; margin-bottom:6px;}
.kpi-value {font-size:1.9rem; font-weight:700;}
.section {font-size:1.2rem; font-weight:700; margin:.4rem 0 .8rem 0;}
.note {font-size:.82rem; color:#475569;}
.good {color:#15803d; font-weight:700;}
.warn {color:#b45309; font-weight:700;}
.bad {color:#b91c1c; font-weight:700;}
</style>
""", unsafe_allow_html=True)

# =========================
# HELPERS
# =========================
def normalize_columns(df):
    df = df.copy()
    df.columns = [re.sub(r"\s+", " ", str(c)).strip() for c in df.columns]
    rename_map = {
        "Store Key":"Store_Key","Store Name":"Store_Name","Store Type":"Store Type",
        "Start Date":"Start Date","End Date":"End Date","End  Date":"End Date",
        "Target Sales":"Target_Sales","Target Txn":"Target_Txn",
        "Actual Sales":"Actual_Sales","Actual Txn":"Actual_Txn",
        "Sales Achievement %":"Sales_Achievement %","Transaction Achievement %":"Transaction_Achievement %",
        "Sales GOLY %":"Sales_GOLY %","Transaction GOLY %":"Transaction_GOLY %",
        "New Customers":"New_Customers","Repeat Customers":"Repeat_Customers",
        "NewCustomer GOLY %":"NewCustomer_GOLY %","RepeatCustomer GOLY %":"RepeatCustomer_GOLY %",
        "DigitalOwn Achievement %":"DigitalOwn_Achievement %","DigitalOwn GOLY %":"DigitalOwn_GOLY %",
        "CallCentre Achievement %":"CallCentre_Achievement %","CallCenter Achievement %":"CallCentre_Achievement %",
        "CallCentre GOLY %":"CallCentre_GOLY %","CallCenter GOLY %":"CallCentre_GOLY %",
        "Outlet Achievement %":"Outlet_Achievement %","Outlet GOLY %":"Outlet_GOLY %",
        "FoodPanda Achievement %":"FoodPanda_Achievement %","FoodPanda GOLY %":"FoodPanda_GOLY %",
        "Carryout Sales %":"Carryout_Sales %","Delivery Sales %":"Delivery_Sales %",
        "Carryout GOLY %":"Carryout_GOLY %","Delivery GOLY %":"Delivery_GOLY %",
    }
    return df.rename(columns=rename_map)

def to_numeric_safe(df, cols):
    df = df.copy()
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    return df

def pkr(x): return f"PKR {x:,.0f}"
def pct(x): return f"{x*100:,.1f}%"
def safe_div(a,b): return a/b if b else 0
def avg(s): return float(s.mean()) if len(s) else 0

def rag_label(x):
    if x >= 1: return "Green"
    if x >= .9: return "Amber"
    return "Red"

def rag_icon(x):
    if x >= 1: return "🟢"
    if x >= .9: return "🟠"
    return "🔴"

def find_col(df, options, default=None):
    for o in options:
        if o in df.columns: return o
    return default

NUMERIC_COLS = [
    "Target_Sales","Target_Txn","Actual_Sales","Actual_Txn","Sales_Achievement %","Transaction_Achievement %",
    "Sales_GOLY %","Transaction_GOLY %","New_Customers","Repeat_Customers","NewCustomer_GOLY %","RepeatCustomer_GOLY %",
    "DigitalOwn_Achievement %","DigitalOwn_GOLY %","CallCentre_Achievement %","CallCentre_GOLY %",
    "Outlet_Achievement %","Outlet_GOLY %","FoodPanda_Achievement %","FoodPanda_GOLY %",
    "Carryout_Sales %","Delivery_Sales %","Carryout_GOLY %","Delivery_GOLY %"
]

@st.cache_data
def load_excel(file_or_path):
    # Handle both file objects and file paths
    if isinstance(file_or_path, str):
        # It's a file path
        file_path = file_or_path
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
            return {"Sheet1": to_numeric_safe(normalize_columns(df), NUMERIC_COLS)}
        xl = pd.ExcelFile(file_path)
    else:
        # It's a file object
        if file_or_path.name.endswith('.csv'):
            df = pd.read_csv(file_or_path)
            return {"Sheet1": to_numeric_safe(normalize_columns(df), NUMERIC_COLS)}
        xl = pd.ExcelFile(file_or_path)
    
    out = {}
    for s in xl.sheet_names:
        temp = pd.read_excel(xl, sheet_name=s)
        temp = to_numeric_safe(normalize_columns(temp), NUMERIC_COLS)
        out[s] = temp
    return out

# =========================
# SIDEBAR
# =========================
st.sidebar.title("🏢 Domino's Reporting Suite")

# Show logged in user info and logout button
st.sidebar.markdown("---")
st.sidebar.markdown(f"**👤 Logged in as:** `{st.session_state.get('logged_in_user', 'User')}`")

# Admin panel for file management
if st.session_state.get('logged_in_user') == 'admin':
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ Admin Panel")
    
    uploaded_file = st.sidebar.file_uploader("📁 Upload New Data File", type=["xlsx", "xls", "csv"], help="Upload a new Excel/CSV file to update the dashboard data")
    
    if uploaded_file is not None:
        # Save the uploaded file to workspace
        save_path = os.path.join(WORKSPACE_DIR, "Performance MTD.xlsx")
        
        # Read and save based on file type
        if uploaded_file.name.endswith('.csv'):
            df_temp = pd.read_csv(uploaded_file)
            df_temp.to_excel(save_path.replace('.xlsx', '.csv'), index=False)
        else:
            df_temp = pd.read_excel(uploaded_file)
            with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
                df_temp.to_excel(writer, index=False, sheet_name='Sheet1')
        
        st.sidebar.success("✅ File uploaded successfully!")
        st.sidebar.info(f"📄 Saved: {save_path}")
        
        # Reload data with new file
        if st.sidebar.button("🔄 Refresh Dashboard Now", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

if st.sidebar.button("🚪 Logout", use_container_width=True):
    # Clear session state
    for key in ["password_correct", "username", "password", "logged_in_user"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# Backend file loading - auto-load from workspace
import os
WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_FILE = os.path.join(WORKSPACE_DIR, "Performance MTD.xlsx")

st.sidebar.markdown("### 📁 Data Source")
st.sidebar.info("ℹ️ Auto-loading from backend workspace")
st.sidebar.caption(f"📄 File: Performance MTD.xlsx")

# Add refresh button for all users
if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# Always use backend file
if not os.path.exists(DEFAULT_FILE):
    st.error(f"❌ File not found: {DEFAULT_FILE}")
    st.info("Please ensure 'Performance MTD.xlsx' exists in the workspace folder.")
    st.stop()

file = DEFAULT_FILE  # Pass the path directly
sheets = load_excel(file)
sheet_names = list(sheets.keys())
selected_sheet = st.sidebar.selectbox("Select Sheet", sheet_names)
df = sheets[selected_sheet].copy()

if df.empty:
    st.error("No valid data found in the selected sheet.")
    st.stop()

store_col = find_col(df,["Store_Name","Store Name"])
store_key_col = find_col(df,["Store_Key","Store Key"])
store_type_col = find_col(df,["Store Type"],"Store Type")

st.sidebar.markdown("---")
search = st.sidebar.text_input("Search Store")
store_types = ["All"] + sorted(df[store_type_col].dropna().astype(str).unique().tolist()) if store_type_col in df.columns else ["All"]
selected_type = st.sidebar.selectbox("Store Type", store_types)
store_names = ["All"] + sorted(df[store_col].dropna().astype(str).unique().tolist()) if store_col else ["All"]
selected_store = st.sidebar.selectbox("Store Name", store_names)
view_mode = st.sidebar.radio("View Mode", ["Executive View","Store Drilldown","Channel View","Exception View"])

filtered = df.copy()
if search and store_col:
    m = filtered[store_col].astype(str).str.contains(search, case=False, na=False)
    if store_key_col in filtered.columns:
        m = m | filtered[store_key_col].astype(str).str.contains(search, case=False, na=False)
    filtered = filtered[m]
if selected_type != "All" and store_type_col in filtered.columns:
    filtered = filtered[filtered[store_type_col].astype(str) == selected_type]
if selected_store != "All" and store_col:
    filtered = filtered[filtered[store_col].astype(str) == selected_store]
if filtered.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

# =========================
# METRICS
# =========================
actual_sales = filtered.get("Actual_Sales", pd.Series([0])).sum()
target_sales = filtered.get("Target_Sales", pd.Series([0])).sum()
actual_txn = filtered.get("Actual_Txn", pd.Series([0])).sum()
target_txn = filtered.get("Target_Txn", pd.Series([0])).sum()
new_cust = filtered.get("New_Customers", pd.Series([0])).sum()
repeat_cust = filtered.get("Repeat_Customers", pd.Series([0])).sum()
sales_ach = safe_div(actual_sales, target_sales)
txn_ach = safe_div(actual_txn, target_txn)
sales_goly = avg(filtered.get("Sales_GOLY %", pd.Series([0])))
avg_ticket = safe_div(actual_sales, actual_txn)
repeat_share = safe_div(repeat_cust, new_cust + repeat_cust)
report_date = datetime.now().strftime("%d %b %Y")

st.title("📊 Enterprise Reporting Suite")
st.caption(f"Generated on {report_date} • Sheet: {selected_sheet} • Executive-ready reporting, drilldowns, exceptions, and exports")

# KPI strip
c1,c2,c3,c4,c5,c6 = st.columns(6)
for col, title, value, note in [
    (c1,"Actual Sales",pkr(actual_sales),pct(sales_goly)),
    (c2,"Transactions",f"{int(actual_txn):,}",pct(txn_ach)),
    (c3,"Sales Achievement",pct(sales_ach),rag_icon(sales_ach)+" "+rag_label(sales_ach)),
    (c4,"Target Gap",pkr(actual_sales-target_sales),"Actual - Target"),
    (c5,"Avg Ticket",pkr(avg_ticket),"Sales / Txn"),
    (c6,"Repeat Share",pct(repeat_share),"Retention mix"),
]:
    col.markdown(f"<div class='card'><div class='kpi-title'>{title}</div><div class='kpi-value'>{value}</div><div class='note'>{note}</div></div>", unsafe_allow_html=True)

# Prepare core table
base_cols = [c for c in [
    store_key_col,store_col,store_type_col,"Start Date","End Date",
    "Target_Sales","Actual_Sales","Sales_Achievement %","Sales_GOLY %",
    "Target_Txn","Actual_Txn","Transaction_Achievement %","Transaction_GOLY %",
    "New_Customers","NewCustomer_GOLY %","Repeat_Customers","RepeatCustomer_GOLY %",
    "DigitalOwn_Achievement %","DigitalOwn_GOLY %",
    "CallCentre_Achievement %","CallCentre_GOLY %",
    "Outlet_Achievement %","Outlet_GOLY %",
    "FoodPanda_Achievement %","FoodPanda_GOLY %",
    "Carryout_Sales %","Carryout_GOLY %","Delivery_Sales %","Delivery_GOLY %"
] if c in filtered.columns]
rank = filtered[base_cols].copy()
rank["Target_Gap"] = rank.get("Actual_Sales",0) - rank.get("Target_Sales",0)
rank["RAG"] = rank.get("Sales_Achievement %",pd.Series([0]*len(rank))).apply(rag_label)

# Tabs
exec_tab, drill_tab, exception_tab, export_tab = st.tabs(["Executive Deck","Store Drilldown","Exceptions & Alerts","Export Center"])

with exec_tab:
    st.markdown("## 📌 Leadership Summary")
    a,b,c,d = st.columns(4)
    a.markdown(f"<div class='card'><b>Total Stores</b><br><span class='kpi-value'>{rank[store_col].nunique() if store_col else len(rank)}</span><br><span class='note'>Visible stores</span></div>", unsafe_allow_html=True)
    b.markdown(f"<div class='card'><b>Performance Status</b><br><span class='kpi-value'>{rag_icon(sales_ach)} {rag_label(sales_ach)}</span><br><span class='note'>Based on sales achievement</span></div>", unsafe_allow_html=True)
    c.markdown(f"<div class='card'><b>Customer Base</b><br><span class='kpi-value'>{int(new_cust+repeat_cust):,}</span><br><span class='note'>{int(new_cust):,} New | {int(repeat_cust):,} Repeat</span></div>", unsafe_allow_html=True)
    d.markdown(f"<div class='card'><b>Store Types</b><br><span class='kpi-value'>{filtered[store_type_col].nunique() if store_type_col in filtered.columns else 1}</span><br><span class='note'>Segment coverage</span></div>", unsafe_allow_html=True)

    x1,x2 = st.columns(2)
    with x1:
        st.markdown("### 🎯 Target vs Actual")
        fig = go.Figure()
        fig.add_bar(x=rank[store_col], y=rank["Target_Sales"], name="Target")
        fig.add_bar(x=rank[store_col], y=rank["Actual_Sales"], name="Actual")
        fig.update_layout(height=420, barmode='group')
        st.plotly_chart(fig, use_container_width=True)
    with x2:
        st.markdown("### 📍 Target Gap by Store")
        fig = px.bar(rank.sort_values("Target_Gap"), x=store_col, y="Target_Gap", text_auto=True)
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)

    # channel view
    channel_rows = []
    for ch, ach in [("DigitalOwn","DigitalOwn_Achievement %"),("CallCenter","CallCentre_Achievement %"),("Outlet","Outlet_Achievement %"),("FoodPanda","FoodPanda_Achievement %")]:
        if ach in filtered.columns:
            channel_rows.append({"Channel":ch,"Achievement":avg(filtered[ach])})
    channel_df = pd.DataFrame(channel_rows)
    y1,y2 = st.columns(2)
    with y1:
        st.markdown("### 📱 Channel Achievement")
        if not channel_df.empty:
            fig = px.bar(channel_df, x="Channel", y="Achievement", text=channel_df["Achievement"].map(lambda x: f"{x*100:.1f}%"))
            fig.update_layout(height=420, yaxis_tickformat='.0%')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Channel columns available نہیں ہیں۔")
    with y2:
        st.markdown("### 🚚 Carryout vs Delivery")
        order_mix = pd.DataFrame([
            {"Type":"Carryout","Share":avg(filtered.get("Carryout_Sales %", pd.Series([0])))},
            {"Type":"Delivery","Share":avg(filtered.get("Delivery_Sales %", pd.Series([0])))}
        ])
        fig = px.pie(order_mix, names="Type", values="Share", hole=.45)
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📝 Leadership Narrative")
    best = rank.sort_values("Actual_Sales", ascending=False).iloc[0]
    worst = rank.sort_values("Actual_Sales", ascending=True).iloc[0]
    narrative = f"""Performance review shows sales of {pkr(actual_sales)} against a target of {pkr(target_sales)}, delivering {pct(sales_ach)} achievement. Transactions stand at {int(actual_txn):,} against target {int(target_txn):,}, with average ticket at {pkr(avg_ticket)}. {best[store_col]} is currently the top-performing store, while {worst[store_col]} remains the weakest in the selected view. Management focus should remain on closing target gaps, improving transaction momentum, and strengthening repeat customer contribution."""
    st.text_area("Copy-Paste Executive Summary", narrative, height=170)

with drill_tab:
    st.markdown("## 🏬 Store Drilldown")
    st.dataframe(rank.sort_values("Actual_Sales", ascending=False), use_container_width=True, height=360)

    d1,d2 = st.columns(2)
    with d1:
        st.markdown("### 👥 New vs Repeat Customers")
        fig = go.Figure()
        fig.add_bar(x=rank[store_col], y=rank.get("New_Customers",0), name="New")
        fig.add_bar(x=rank[store_col], y=rank.get("Repeat_Customers",0), name="Repeat")
        fig.update_layout(height=420, barmode='group')
        st.plotly_chart(fig, use_container_width=True)
    with d2:
        st.markdown("### 📈 Sales vs Transaction GOLY")
        if "Sales_GOLY %" in rank.columns and "Transaction_GOLY %" in rank.columns:
            fig = go.Figure()
            fig.add_scatter(x=rank[store_col], y=rank["Sales_GOLY %"], mode='lines+markers', name='Sales GOLY')
            fig.add_scatter(x=rank[store_col], y=rank["Transaction_GOLY %"], mode='lines+markers', name='Txn GOLY')
            fig.update_layout(height=420, yaxis_tickformat='.0%')
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🌡️ Heatmap")
    heat_cols = [c for c in ["Sales_Achievement %","Transaction_Achievement %","Sales_GOLY %","Transaction_GOLY %","DigitalOwn_Achievement %","CallCentre_Achievement %","Outlet_Achievement %","FoodPanda_Achievement %"] if c in rank.columns]
    if heat_cols and store_col:
        heat = rank[[store_col] + heat_cols].copy()
        heat = heat.dropna(subset=[store_col])
        heat = heat.set_index(store_col)
        if not heat.empty and len(heat.columns) > 0:
            fig = px.imshow(heat.T, aspect='auto', text_auto='.0%', color_continuous_scale='Blues')
            fig.update_layout(height=460)
            st.plotly_chart(fig, use_container_width=True)

with exception_tab:
    st.markdown("## 🚨 Exceptions & Alerts")
    exc = rank[
        (rank.get("Sales_Achievement %",0) < .90) |
        (rank.get("Transaction_Achievement %",0) < .90) |
        (rank.get("DigitalOwn_Achievement %",0) < .90) |
        (rank.get("CallCentre_Achievement %",0) < .90) |
        (rank.get("Outlet_Achievement %",0) < .90) |
        (rank.get("FoodPanda_Achievement %",0) < .90)
    ].copy()
    if exc.empty:
        st.success("Current filtered view میں کوئی major exception نہیں ہے۔")
    else:
        st.markdown("### Full Exception Reporting Table")
        st.dataframe(exc.sort_values(["Sales_Achievement %","Transaction_Achievement %"]), use_container_width=True, height=360)
        st.markdown("### Exception Summary")
        e1,e2,e3,e4 = st.columns(4)
        e1.metric("Exception Stores", len(exc))
        e2.metric("Sales < 90%", int((exc.get("Sales_Achievement %",0) < .90).sum()))
        e3.metric("Txn < 90%", int((exc.get("Transaction_Achievement %",0) < .90).sum()))
        e4.metric("Channel Exceptions", int(((exc.get("DigitalOwn_Achievement %",0) < .90) | (exc.get("CallCentre_Achievement %",0) < .90) | (exc.get("Outlet_Achievement %",0) < .90) | (exc.get("FoodPanda_Achievement %",0) < .90)).sum()))
        st.markdown("### Recommended Actions")
        actions = []
        if sales_ach < 1:
            actions.append("Prepare a daily recovery plan for under-target stores.")
        if txn_ach < 1:
            actions.append("Implement frequency-driving offers and local activation initiatives to recover transactions.")
        if repeat_share < 0.55:
            actions.append("Strengthen CRM and repeat customer campaigns, as the repeat customer mix is currently soft.")
        for a in actions:
            st.markdown(f"- {a}")

    st.markdown("## 📋 Channel Wise Detailed Table")
    channel_table_cols = [c for c in [store_key_col, store_col, store_type_col, "DigitalOwn_Achievement %","DigitalOwn_GOLY %","CallCentre_Achievement %","CallCentre_GOLY %","Outlet_Achievement %","Outlet_GOLY %","FoodPanda_Achievement %","FoodPanda_GOLY %"] if c in rank.columns]
    if channel_table_cols:
        st.dataframe(rank[channel_table_cols], use_container_width=True, height=320)

    st.markdown("## 🚚 Carryout / Delivery Detailed Table")
    order_table_cols = [c for c in [store_key_col, store_col, store_type_col, "Carryout_Sales %","Carryout_GOLY %","Delivery_Sales %","Delivery_GOLY %"] if c in rank.columns]
    if order_table_cols:
        st.dataframe(rank[order_table_cols], use_container_width=True, height=320)

    st.markdown("## 👥 Customer Detailed Table")
    customer_table_cols = [c for c in [store_key_col, store_col, store_type_col, "New_Customers","NewCustomer_GOLY %","Repeat_Customers","RepeatCustomer_GOLY %"] if c in rank.columns]
    if customer_table_cols:
        st.dataframe(rank[customer_table_cols], use_container_width=True, height=320)

with export_tab:
    st.markdown("## ⬇️ Export Center")
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine='openpyxl') as writer:
        filtered.to_excel(writer, index=False, sheet_name='Filtered_Data')
        rank.to_excel(writer, index=False, sheet_name='Store_Ranking')
        if 'exc' in locals(): exc.to_excel(writer, index=False, sheet_name='Exceptions')
        if 'channel_df' in locals() and not channel_df.empty: channel_df.to_excel(writer, index=False, sheet_name='Channel_Summary')
        if 'channel_table_cols' in locals() and channel_table_cols: rank[channel_table_cols].to_excel(writer, index=False, sheet_name='Channel_Detail')
        if 'order_table_cols' in locals() and order_table_cols: rank[order_table_cols].to_excel(writer, index=False, sheet_name='Carryout_Delivery')
        if 'customer_table_cols' in locals() and customer_table_cols: rank[customer_table_cols].to_excel(writer, index=False, sheet_name='Customer_Detail')
        # write sheet list info
        pd.DataFrame({"Available_Sheets": sheet_names}).to_excel(writer, index=False, sheet_name='Workbook_Index')
    out.seek(0)
    st.download_button("Download Enterprise Excel Output", data=out, file_name="enterprise_reporting_suite_output.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.markdown("### What this export includes")
    st.markdown("- Filtered data\n- Store ranking\n- Exceptions\n- Channel summary\n- Workbook index")

st.success("Domino's Reporting Suite ready.")
