# PythonAnywhere Ultimate Deployment Guide

This guide contains everything you need to get your ResumeBuilder.Bot online for free using PythonAnywhere.

## 📁 1. Required Files Overview
Your app is fully ready! I've already ensured your `ResumeBuilderBot` folder has everything required:
- `app.py` (Core logic and web server endpoints)
- `database.db` (Your SQLite Database holding users/resumes)
- `requirements.txt` (Tells PythonAnywhere what packages to install)

## ☁️ 2. Setup PythonAnywhere
1. Go to [PythonAnywhere.com](https://www.pythonanywhere.com/) and create a free Beginners account.
2. Go to the **Files** tab. You'll see you are inside `/home/yourusername/`.
3. Create a new directory called `ResumeBuilderBot`.
4. Upload all the files and folders from your computer to this directory (you can zip the folder on your PC, upload the zip, and use the Bash console to unzip it with `unzip filename.zip` to save time!).

## ⚙️ 3. Configure the Web Server
1. Go to the **Web** tab and click **"Add a new web app"**.
2. Click **Next** on the free domain pop-up.
3. Choose **Manual Configuration** (Do NOT choose Flask to avoid weird automated resets).
4. Select **Python 3.10** (or whatever the latest 3.x is).
5. Once your web app is created, scroll down to the **"Source code"** section and type `/home/yourusername/ResumeBuilderBot`
6. Scroll down to the **"Virtualenv"** section. Click the red text and enter `/home/yourusername/.virtualenvs/venv` (We'll create this next).

## 💻 4. Install Dependencies
1. Open a new tab and go to the **Consoles** page.
2. Click **Bash** to open a black terminal.
3. Run the following three commands exactly:
```bash
mkvirtualenv --python=python3.10 venv
cd /home/yourusername/ResumeBuilderBot
pip install -r requirements.txt
```
*(Wait for this to finish downloading Flask and Werkzeug.)*

## 🔌 5. Copy the WSGI Code
*This step hooks your `app.py` into PythonAnywhere's servers.* 
1. Go back to the **Web** tab.
2. Scroll to the **"Code"** section and click the link next to **"WSGI configuration file:"** (it looks like `/var/www/yourusername_pythonanywhere_com_wsgi.py`).
3. Delete **EVERYTHING** inside that file and paste this exact code:

```python
import sys
import os

# 1. Add your project folder to the system path
project_home = '/home/yourusername/ResumeBuilderBot'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# 2. Set environment variables (optional but good practice)
os.environ['APP_ENV'] = 'production'

# 3. Import your Flask app (assuming your file is named app.py and the flask instance is 'app')
# PythonAnywhere expects the application object to be named 'application'
from app import app as application  # noqa
```
**(Important: replace `yourusername` with your actual PythonAnywhere username!)**

4. Click **Save** in the top right.

## 🎉 6. Launch!
1. Go back to the **Web** tab.
2. Click the big green **"Reload yourusername.pythonanywhere.com"** button at the top.
3. Click your URL at the top of the screen. Your app is now live to the world!
