# 📊 Domino's Reporting Suite

Professional performance analytics dashboard with authentication and real-time data updates.

## Features

- 🔐 Secure user authentication
- ⚙️ Admin panel for file uploads
- 📈 Interactive charts and visualizations
- 📱 Mobile-responsive design
- 🔄 Real-time data refresh
- 💾 Export capabilities (Excel)

## Quick Start

### Local Deployment

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the app:
```bash
streamlit run App.py
```

3. Login credentials:
   - Username: `admin`
   - Password: `admin123`

### Cloud Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for complete instructions on deploying to Streamlit Cloud.

## Usage

### For Admin Users:
1. Login with admin credentials
2. Upload new Excel/CSV files via the Admin Panel in sidebar
3. Click "Refresh Dashboard Now" to update

### For Regular Users:
1. Login with provided credentials
2. View interactive dashboard
3. Use filters and search functionality
4. Export data as needed

## Default Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| User | user | user123 |
| Team | dominos | dominos2024 |

**⚠️ Important:** Change these passwords before deploying to production!

## Tech Stack

- **Frontend:** Streamlit
- **Data Processing:** Pandas, NumPy
- **Visualization:** Plotly
- **File Handling:** OpenPyXL
- **Deployment:** Streamlit Cloud

## File Structure

```
dominos-reporting-suite/
├── App.py                 # Main application
├── requirements.txt       # Python dependencies
├── DEPLOYMENT_GUIDE.md   # Deployment instructions
├── README.md             # This file
└── .gitignore            # Git ignore rules
```

## Data File Format

Upload Excel/CSV files with these columns:
- Store Key / Store_Key
- Store Name / Store_Name
- Store Type
- Target Sales / Target_Sales
- Actual Sales / Actual_Sales
- Target Transactions / Target_Txn
- Actual Transactions / Actual_Txn
- Sales Achievement %
- Transaction Achievement %
- Sales GOLY %
- Transaction GOLY %
- New Customers
- Repeat Customers
- Channel performance metrics (DigitalOwn, CallCentre, Outlet, FoodPanda)
- Order mix (Carryout %, Delivery %)

## Support

For issues or questions:
- Check [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- Visit Streamlit documentation: https://docs.streamlit.io
- Review app logs in Streamlit Cloud dashboard

## License

This project is proprietary software developed for Domino's.

---

**Version:** 1.0  
**Last Updated:** March 2026
