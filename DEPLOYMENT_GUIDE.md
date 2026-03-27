# 🚀 Domino's Reporting Suite - Deployment Guide

## Complete Step-by-Step Instructions to Deploy on Streamlit Cloud (FREE)

---

## 📋 Prerequisites

- GitHub account (free at github.com)
- Streamlit Cloud account (free at share.streamlit.io)
- Your updated App.py file
- requirements.txt file (already created)

---

## Step 1: Prepare Your Files for GitHub

### Create a new folder for your project:
```
dominos-reporting-suite/
├── App.py
├── requirements.txt
├── .gitignore (optional, recommended)
└── README.md (optional)
```

### Create a `.gitignore` file (to exclude unnecessary files):
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Data files (DON'T upload Excel files to GitHub)
*.xlsx
*.xls
*.csv
```

---

## Step 2: Upload to GitHub

### Option A: Using GitHub Website (Easiest)

1. **Go to** https://github.com
2. **Sign in** to your GitHub account
3. **Click** the "+" icon (top right) → "New repository"
4. **Repository name:** `dominos-reporting-suite`
5. **Description:** "Domino's Performance Reporting Dashboard"
6. **Visibility:** Public or Private (your choice)
7. **DO NOT** initialize with README (we'll upload existing files)
8. **Click** "Create repository"

### Upload Your Files:

9. **On the next page**, click "uploading an existing file"
10. **Drag and drop** these files:
    - `App.py`
    - `requirements.txt`
    - `.gitignore` (if created)
11. **Add commit message:** "Initial commit - Domino's Reporting Suite"
12. **Click** "Commit changes"

### Option B: Using Git Command Line (Alternative)

```bash
cd "C:\Users\imran.aslam\Desktop\MTD Reports"
git init
git add App.py requirements.txt .gitignore
git commit -m "Initial commit - Domino's Reporting Suite"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/dominos-reporting-suite.git
git push -u origin main
```

---

## Step 3: Deploy to Streamlit Cloud

### Create Streamlit Cloud Account:

1. **Go to** https://share.streamlit.io
2. **Click** "Sign up" or "Login"
3. **Choose** "Sign in with GitHub" (recommended) or email
4. **Complete** the registration process

### Deploy Your App:

5. **Click** "New app" button
6. **Fill in the deployment form:**

   **Repository:** 
   - Select your GitHub account
   - Choose `dominos-reporting-suite`
   
   **Branch:** 
   - Select `main` (or `master`)
   
   **File path:** 
   - Type: `App.py`
   
   **Advanced Settings** (click to expand):
   
   ✅ **Enable "Use custom command"** (optional, usually not needed)
   
   ✅ **Python version:** 3.11 (or latest available)
   
   ✅ **App settings:**
   - App title: `Domino's Reporting Suite`
   - Icon: 📊
   - Layout: Wide
   
   ✅ **Secrets** (if you want to add credentials later):
   ```toml
   [general]
   admin_password = "your_secure_password"
   ```

7. **Click** "Deploy!" button

### Wait for Deployment:

8. **Deployment takes 2-5 minutes**
9. **Watch the logs** to see progress
10. **Once complete**, you'll see: "✅ Your app is ready!"
11. **Click** "Open app" to view your live dashboard

---

## Step 4: Access Your Live Dashboard

### Your app URL will be:
```
https://dominos-reporting-suite-app-xxxxxx.streamlit.app/
```

### Share this URL with your team!

---

## Step 5: Update Data Files (After Deployment)

### Method 1: Upload Through Admin Panel (Recommended)

1. **Login** to your deployed app as admin:
   - Username: `admin`
   - Password: `admin123`

2. **In the sidebar**, find "⚙️ Admin Panel"

3. **Click** "📁 Upload New Data File"

4. **Select** your new Performance MTD.xlsx file

5. **Click** "🔄 Refresh Dashboard Now"

✅ **Done!** Your dashboard updates immediately!

### Method 2: Update via GitHub (For Code Changes)

1. **Make changes** to App.py locally
2. **Commit and push** to GitHub:
   ```bash
   git add App.py
   git commit -m "Updated feature XYZ"
   git push
   ```
3. **Streamlit Cloud auto-deploys** within 1-2 minutes

---

## 🔧 Troubleshooting

### ❌ App won't deploy / Shows errors:

**Check logs in Streamlit Cloud:**
- Click "Logs" tab in your app dashboard
- Look for error messages
- Common issues:
  - Missing dependencies → Update requirements.txt
  - File path errors → Check DEFAULT_FILE path in code
  - Import errors → Ensure all packages are in requirements.txt

### ❌ File upload doesn't work:

**Note:** Streamlit Cloud has temporary storage. Files may be deleted when:
- App restarts (happens automatically every few hours)
- You redeploy the app
- After 24 hours of inactivity

**Solution:** For permanent storage, consider:
- Google Drive integration
- AWS S3 bucket
- Dropbox integration
- Upgrade to Streamlit Cloud paid plan with persistent storage

### ❌ Login credentials don't work:

**Remember:**
- Username: `admin`
- Password: `admin123`
- Case-sensitive!

---

## 🎯 Best Practices

### Security:
✅ Change default passwords in production
✅ Use environment variables for sensitive data
✅ Keep GitHub repo private if possible
✅ Don't commit Excel files with sensitive data

### Performance:
✅ Use caching (@st.cache_data) - already implemented
✅ Optimize large Excel files before upload
✅ Clear cache when refreshing data

### Maintenance:
✅ Test locally before deploying
✅ Keep requirements.txt updated
✅ Monitor app usage in Streamlit dashboard
✅ Set up email notifications for deployment failures

---

## 📊 Your Dashboard Features (Live)

✅ User Authentication (Login/Logout)
✅ Admin Panel with File Upload
✅ Auto-loading from backend
✅ Multiple sheet support
✅ Interactive charts and tables
✅ Export functionality
✅ Real-time data refresh
✅ Mobile-responsive design

---

## 🆘 Need Help?

### Streamlit Resources:
- Documentation: https://docs.streamlit.io
- Community Forum: https://discuss.streamlit.io
- Gallery: https://streamlit.io/gallery

### GitHub Resources:
- Docs: https://docs.github.com
- Support: https://support.github.com

---

## 🎉 Congratulations!

Your **Domino's Reporting Suite** is now live and accessible from anywhere!

### What you've accomplished:
✅ Deployed a professional dashboard
✅ Added secure authentication
✅ Enabled easy file updates
✅ Created a scalable solution

### Next Steps:
1. Share the app URL with your team
2. Upload your first data file through admin panel
3. Explore analytics and insights
4. Customize branding as needed

---

**Happy Analyzing! 📊✨**
