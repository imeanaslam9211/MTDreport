import io
import re
import os
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

def generate_auto_insights(filtered, actual_sales, target_sales, actual_txn, target_txn, 
                           sales_ach, txn_ach, avg_ticket, repeat_share, store_col):
    """
    Generate automatic AI-powered business commentary and actionable insights.
    """
    insights = []
    actions = []
    
    # Calculate additional metrics
    total_stores = filtered[store_col].nunique() if store_col else 0
    sales_gap = actual_sales - target_sales
    sales_gap_pct = safe_div(sales_gap, target_sales)
    txn_gap = actual_txn - target_txn
    top_performers = filtered.nlargest(3, 'Actual_Sales')[store_col].dropna().astype(str).tolist() if store_col else []
    bottom_performers = filtered.nsmallest(3, 'Actual_Sales')[store_col].dropna().astype(str).tolist() if store_col in filtered.columns else []
    
    # ========== PERFORMANCE COMMENTARY ==========
    insights.append("### 📊 Overall Performance Commentary")
    
    # Sales performance
    if sales_ach >= 1.0:
        insights.append(f"✅ **Strong Performance:** Achieved {pct(sales_ach)} of sales target, exceeding goals by {pct(abs(sales_gap_pct))}. This represents {pkr(abs(sales_gap))} above target.")
    elif sales_ach >= 0.9:
        insights.append(f"🟡 **Near Target:** Achieved {pct(sales_ach)} of sales target, with a gap of {pkr(abs(sales_gap))} ({pct(abs(sales_gap_pct))}) remaining.")
    else:
        insights.append(f"🔴 **Below Target:** Achieved only {pct(sales_ach)} of sales target, falling short by {pkr(abs(sales_gap))} ({pct(abs(sales_gap_pct))}).")
    
    # Transaction performance
    if txn_ach >= 1.0:
        insights.append(f"✅ **Transaction Excellence:** Completed {int(actual_txn):,} transactions vs target {int(target_txn):,}, achieving {pct(txn_ach)}.")
    elif txn_ach >= 0.9:
        insights.append(f"🟡 **Transaction Performance:** Completed {int(actual_txn):,} transactions, slightly below target of {int(target_txn):,} ({pct(txn_ach)} achievement).")
    else:
        insights.append(f"🔴 **Transaction Gap:** Only {int(actual_txn):,} transactions completed against target {int(target_txn):,}, requiring immediate recovery focus.")
    
    # Store count context
    insights.append(f"📍 **Coverage:** Performance across {total_stores} stores in the selected view.")
    
    # ========== KEY DRIVERS ==========
    insights.append("\n### 🎯 Key Performance Drivers")
    
    # Top stores
    if top_performers:
        insights.append(f"⭐ **Top Contributors:** {', '.join(top_performers[:3])} are leading performance.")
    
    # Average ticket analysis
    if avg_ticket > 500:
        insights.append(f"💰 **High Ticket Value:** Average transaction value of {pkr(avg_ticket)} indicates strong basket size.")
    elif avg_ticket > 300:
        insights.append(f"💰 **Moderate Ticket Value:** Average transaction of {pkr(avg_ticket)} shows room for upselling opportunities.")
    else:
        insights.append(f"💰 **Ticket Focus Needed:** Average transaction of {pkr(avg_ticket)} suggests need for basket-building initiatives.")
    
    # Repeat customer analysis
    if repeat_share >= 0.6:
        insights.append(f"🔄 **Strong Loyalty:** Repeat customers represent {pct(repeat_share)} of traffic, indicating healthy retention.")
    elif repeat_share >= 0.45:
        insights.append(f"🔄 **Moderate Retention:** Repeat share at {pct(repeat_share)} is acceptable but could be strengthened.")
    else:
        insights.append(f"🔄 **Retention Alert:** Low repeat customer share ({pct(repeat_share)}) requires CRM intervention.")
    
    # ========== CRITICAL INSIGHTS ==========
    insights.append("\n### ⚠️ Critical Business Insights")
    
    # Gap analysis
    if sales_gap < -target_sales * 0.15:
        insights.append(f"🚨 **Significant Gap:** Sales shortfall of {pkr(abs(sales_gap))} requires urgent leadership attention and daily monitoring.")
    elif sales_gap < 0:
        insights.append(f"⚠️ **Recovery Needed:** Current gap of {pkr(abs(sales_gap))} is recoverable with focused execution.")
    
    # Trend indicators
    if sales_ach >= 1 and txn_ach >= 1:
        insights.append("📈 **Positive Momentum:** Both sales and transactions on track, indicating balanced growth.")
    elif sales_ach >= 1 and txn_ach < 1:
        insights.append("📊 **Mixed Signals:** Sales achievement strong but transactions lagging - likely driven by ticket size improvements.")
    elif sales_ach < 1 and txn_ach >= 1:
        insights.append("💵 **Conversion Challenge:** Transactions on target but sales conversion needs improvement - review pricing/promotion strategy.")
    else:
        insights.append("🔴 **Dual Challenge:** Both sales and transactions behind - requires comprehensive recovery plan.")
    
    # ========== ACTIONABLE RECOMMENDATIONS ==========
    insights.append("\n### 🎯 Recommended Actions")
    
    # Priority 1: Sales recovery
    if sales_ach < 0.85:
        actions.append({
            "priority": "🔴 CRITICAL",
            "area": "Sales Recovery",
            "action": f"Implement daily sales war room to address {pkr(abs(sales_gap))} gap. Focus on top 20% underperforming stores with targeted interventions.",
            "timeline": "Immediate (This Week)"
        })
    elif sales_ach < 1:
        actions.append({
            "priority": "🟡 HIGH",
            "area": "Sales Acceleration",
            "action": f"Accelerate sales momentum through promotional activity and local store marketing to close {pkr(abs(sales_gap))} remaining gap.",
            "timeline": "Next 7-10 Days"
        })
    
    # Priority 2: Transaction focus
    if txn_ach < 0.9:
        actions.append({
            "priority": "🔴 CRITICAL",
            "area": "Transaction Generation",
            "action": "Launch frequency-driving campaigns, optimize delivery times, and activate local community engagement to boost customer visits.",
            "timeline": "Immediate"
        })
    elif txn_ach < 1:
        actions.append({
            "priority": "🟡 MEDIUM",
            "area": "Traffic Building",
            "action": "Enhance visibility campaigns and consider daypart-specific promotions to increase transaction count.",
            "timeline": "Next 2 Weeks"
        })
    
    # Priority 3: Customer retention
    if repeat_share < 0.5:
        actions.append({
            "priority": "🟡 HIGH",
            "area": "Customer Retention",
            "action": "Activate CRM campaigns, introduce loyalty incentives, and strengthen follow-marketing to improve repeat customer ratio.",
            "timeline": "This Month"
        })
    
    # Priority 4: Store-specific actions
    if bottom_performers and len(bottom_performers) > 0:
        actions.append({
            "priority": "🟡 FOCUSED",
            "area": "Store Turnaround",
            "action": f"Priority coaching for lowest performers: {', '.join(bottom_performers[:3])}. Deploy area managers for on-ground support.",
            "timeline": "Weekly Reviews"
        })
    
    # Priority 5: Operational excellence
    if avg_ticket < 350:
        actions.append({
            "priority": "🟢 OPPORTUNITY",
            "area": "Basket Building",
            "action": "Introduce combo deals, suggestive selling training, and check-adder contests to improve average transaction value.",
            "timeline": "Ongoing"
        })
    
    return insights, actions

NUMERIC_COLS = [
    "Target_Sales","Target_Txn","Actual_Sales","Actual_Txn","Sales_Achievement %","Transaction_Achievement %",
    "Sales_GOLY %","Transaction_GOLY %","New_Customers","Repeat_Customers","NewCustomer_GOLY %","RepeatCustomer_GOLY %",
    "DigitalOwn_Achievement %","DigitalOwn_GOLY %","CallCentre_Achievement %","CallCentre_GOLY %",
    "Outlet_Achievement %","Outlet_GOLY %","FoodPanda_Achievement %","FoodPanda_GOLY %",
    "Carryout_Sales %","Delivery_Sales %","Carryout_GOLY %","Delivery_GOLY %"
]

@st.cache_data
def load_excel_from_path(file_path):
    """Load Excel file from path - cached for performance"""
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
        return {"Sheet1": to_numeric_safe(normalize_columns(df), NUMERIC_COLS)}
    xl = pd.ExcelFile(file_path)
    out = {}
    for s in xl.sheet_names:
        temp = pd.read_excel(xl, sheet_name=s)
        temp = to_numeric_safe(normalize_columns(temp), NUMERIC_COLS)
        out[s] = temp
    return out

def load_excel_from_uploaded_file(uploaded_file):
    """Load Excel from uploaded file object - not cached to get fresh data"""
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
        return {"Sheet1": to_numeric_safe(normalize_columns(df), NUMERIC_COLS)}
    xl = pd.ExcelFile(uploaded_file)
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

# Backend file loading - auto-load from workspace
WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_FILE = os.path.join(WORKSPACE_DIR, "Performance MTD.xlsx")

# Initialize session state for file tracking
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None

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
        
        try:
            # Read and save based on file type
            if uploaded_file.name.endswith('.csv'):
                df_temp = pd.read_csv(uploaded_file)
                save_path_csv = save_path.replace('.xlsx', '.csv')
                df_temp.to_csv(save_path_csv, index=False)
                st.session_state.uploaded_file_name = save_path_csv
            else:
                # Read ALL sheets from uploaded Excel file
                xl_upload = pd.ExcelFile(uploaded_file)
                
                # Save all sheets to new file
                with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
                    for sheet_name in xl_upload.sheet_names:
                        df_temp = pd.read_excel(xl_upload, sheet_name=sheet_name)
                        df_temp.to_excel(writer, index=False, sheet_name=sheet_name)
                
                st.session_state.uploaded_file_name = save_path
            
            st.sidebar.success("✅ File uploaded successfully!")
            st.sidebar.info(f"📄 Saved: {save_path}")
            
            # Show sheet info
            if not uploaded_file.name.endswith('.csv'):
                xl_temp = pd.ExcelFile(uploaded_file)
                st.sidebar.success(f"📊 Sheets detected: {', '.join(xl_temp.sheet_names)}")
                st.sidebar.info(f"📋 Total sheets: {len(xl_temp.sheet_names)}")
            
            st.sidebar.warning("⚠️ Click 'Refresh Dashboard' button below to load new data")
            # Add a refresh button after successful upload
            if st.sidebar.button("🔄 Refresh Dashboard Now", key="upload_refresh", use_container_width=True):
                st.cache_data.clear()
                st.rerun()
        except Exception as e:
            st.sidebar.error(f"❌ Error uploading file: {str(e)}")

if st.sidebar.button("🚪 Logout", use_container_width=True):
    # Clear session state
    for key in ["password_correct", "username", "password", "logged_in_user"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# Backend file loading - auto-load from workspace
st.sidebar.markdown("### 📁 Data Source")

# Determine which file to load
if st.session_state.uploaded_file_name and os.path.exists(st.session_state.uploaded_file_name):
    file_to_load = st.session_state.uploaded_file_name
    st.sidebar.info("ℹ️ Using uploaded file")
    st.sidebar.caption(f"📄 File: {os.path.basename(file_to_load)}")
else:
    file_to_load = DEFAULT_FILE
    st.sidebar.info("ℹ️ Auto-loading from backend workspace")
    st.sidebar.caption(f"📄 File: Performance MTD.xlsx")

# Add refresh button for all users
if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# Load the Excel file
if not os.path.exists(file_to_load):
    st.error(f"❌ File not found: {file_to_load}")
    if file_to_load == DEFAULT_FILE:
        st.info("Please ensure 'Performance MTD.xlsx' exists in the workspace folder.")
    else:
        st.info("Please upload a valid Excel/CSV file.")
    st.stop()

# Clear cache before loading to ensure fresh data
st.cache_data.clear()
sheets = load_excel_from_path(file_to_load)
sheet_names = list(sheets.keys())

# Show available sheets in sidebar
if len(sheet_names) > 1:
    st.sidebar.success(f"✅ {len(sheet_names)} sheets loaded successfully!")
elif len(sheet_names) == 1:
    st.sidebar.info(f"ℹ️ 1 sheet loaded")

# Use a unique key for selectbox to force refresh when sheets change
selectbox_key = f"sheet_select_{len(sheet_names)}_{file_to_load}"
selected_sheet = st.sidebar.selectbox("Select Sheet", sheet_names, key=selectbox_key)
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

# Format percentage columns for display
pct_cols = ["Sales_Achievement %", "Transaction_Achievement %", "Sales_GOLY %", "Transaction_GOLY %", 
            "NewCustomer_GOLY %", "RepeatCustomer_GOLY %", "DigitalOwn_Achievement %", "DigitalOwn_GOLY %",
            "CallCentre_Achievement %", "CallCentre_GOLY %", "Outlet_Achievement %", "Outlet_GOLY %",
            "FoodPanda_Achievement %", "FoodPanda_GOLY %", "Carryout_Sales %", "Carryout_GOLY %",
            "Delivery_Sales %", "Delivery_GOLY %"]

# Create a display copy with formatted percentages
rank_display = rank.copy()
for col in pct_cols:
    if col in rank_display.columns:
        rank_display[col] = (rank_display[col] * 100).round(1).astype(str) + '%'

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

# ========== AUTOMATED AI INSIGHTS SECTION ==========
st.markdown("---")
st.markdown("## 🧠 Automated Business Intelligence & Commentary")
st.caption("AI-powered analysis generating actionable insights based on current performance data")

# Generate insights
insights_list, action_items = generate_auto_insights(
    filtered, actual_sales, target_sales, actual_txn, target_txn,
    sales_ach, txn_ach, avg_ticket, repeat_share, store_col
)

# Display insights in tabs
insight_tab1, insight_tab2, insight_tab3 = st.tabs(["📊 Performance Commentary", "⚠️ Critical Insights", "🎯 Action Plan"])

with insight_tab1:
    st.markdown("### 📈 Comprehensive Performance Analysis")
    for insight in insights_list:
        if insight.startswith("###"):
            st.markdown(insight)
        else:
            st.markdown(f"<div style='background: #f8fafc; border-left: 4px solid #0f172a; padding: 14px 16px; border-radius: 12px; margin-bottom: 10px;'>{insight}</div>", unsafe_allow_html=True)

with insight_tab2:
    st.markdown("### ⚠️ Key Issues & Opportunities")
    critical_items = [i for i in insights_list if "Critical" in i or "Gap" in i or "Challenge" in i or "Recovery" in i]
    for item in insights_list:
        if any(x in item for x in ["🚨", "⚠️", "🔴", "Critical", "Gap", "Alert"]):
            st.markdown(f"<div style='background: #fef3c7; border-left: 4px solid #f59e0b; padding: 14px 16px; border-radius: 12px; margin-bottom: 10px;'>{item}</div>", unsafe_allow_html=True)

with insight_tab3:
    st.markdown("### 🎯 Prioritized Action Items")
    
    if action_items:
        # Create a nice table for actions
        action_df = pd.DataFrame(action_items)
        
        # Display each action as a card
        for idx, action in enumerate(action_items):
            priority_color = "#ef4444" if "CRITICAL" in action["priority"] else "#f59e0b" if "HIGH" in action["priority"] else "#10b981"
            
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); border: 2px solid {priority_color}; border-radius: 16px; padding: 18px; margin-bottom: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);'>
                <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;'>
                    <span style='font-size: 1.1rem; font-weight: 700; color: {priority_color};'>{action["priority"]} - {action["area"]}</span>
                    <span style='background: {priority_color}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;'>{action["timeline"]}</span>
                </div>
                <p style='color: #334155; line-height: 1.6; margin: 0;'>{action["action"]}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Export button for action plan
        st.markdown("---")
        col_exp1, col_exp2 = st.columns([3, 1])
        with col_exp1:
            st.info("💡 Tip: Review these actions with your team and assign owners to each initiative.")
        with col_exp2:
            if st.button("📋 Export Actions", use_container_width=True):
                # Create downloadable action plan
                action_export = pd.DataFrame(action_items)
                csv = action_export.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"action_plan_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
    else:
        st.success("✅ No critical actions required - performance is on track!")
        st.info("Continue monitoring and maintaining current execution standards.")

with drill_tab:
    st.markdown("## 🏬 Store Drilldown")
    st.dataframe(rank_display.sort_values("Actual_Sales", ascending=False), use_container_width=True, height=360)

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
        st.success("Current filtered view has no major exceptions.")
    else:
        # Format exception table with percentages
        exc_display = exc.copy()
        for col in pct_cols:
            if col in exc_display.columns:
                exc_display[col] = (exc_display[col] * 100).round(1).astype(str) + '%'
        
        st.markdown("### Full Exception Reporting Table")
        st.dataframe(exc_display.sort_values(["Sales_Achievement %","Transaction_Achievement %"]), use_container_width=True, height=360)
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
        st.dataframe(rank_display[channel_table_cols], use_container_width=True, height=320)

    st.markdown("## 🚚 Carryout / Delivery Detailed Table")
    order_table_cols = [c for c in [store_key_col, store_col, store_type_col, "Carryout_Sales %","Carryout_GOLY %","Delivery_Sales %","Delivery_GOLY %"] if c in rank.columns]
    if order_table_cols:
        st.dataframe(rank_display[order_table_cols], use_container_width=True, height=320)

    st.markdown("## 👥 Customer Detailed Table")
    customer_table_cols = [c for c in [store_key_col, store_col, store_type_col, "New_Customers","NewCustomer_GOLY %","Repeat_Customers","RepeatCustomer_GOLY %"] if c in rank.columns]
    if customer_table_cols:
        st.dataframe(rank_display[customer_table_cols], use_container_width=True, height=320)

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
