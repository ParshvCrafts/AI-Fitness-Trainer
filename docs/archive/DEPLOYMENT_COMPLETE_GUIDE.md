# Complete Deployment Guide - AI Fitness Trainer

This guide will walk you through deploying your pose estimation web app from zero to live on the internet - completely free!

## Overview

Your app is a real-time Flask application with WebSockets (SocketIO), which requires special hosting considerations. We'll use **Render** (free tier) for hosting.

---

## Part 1: Prepare Your Project for Deployment

### Step 1: Create Essential Deployment Files

You'll need a few additional files for deployment:

#### A. Create `.gitignore` file
This tells Git what NOT to upload to GitHub.

Create a file named `.gitignore` in your `web_app` folder with:

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

# Certificates (don't upload your local SSL certs)
cert.pem
key.pem

# Environment variables
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
```

#### B. Create `runtime.txt` file
This tells Render which Python version to use.

Create a file named `runtime.txt`:

```
python-3.11.0
```

#### C. Update `requirements.txt`
Your current requirements.txt needs one small modification for cloud deployment:

Replace `opencv-python` with `opencv-python-headless`:

```
Flask==3.0.0
flask-socketio==5.3.5
opencv-python-headless==4.8.1.78
mediapipe==0.10.8
numpy==1.24.3
python-socketio==5.10.0
python-engineio==4.8.0
eventlet==0.33.3
dnspython==2.4.2
Werkzeug==3.0.1
gunicorn==21.2.0
```

**Why?** `opencv-python-headless` is lighter and works better on servers without displays.

#### D. Create `Procfile`
This tells Render how to start your app.

Create a file named `Procfile` (no file extension):

```
web: gunicorn --worker-class eventlet -w 1 app:app --bind 0.0.0.0:$PORT
```

#### E. Update `app.py` for Production

Change the last lines in `app.py` from:

```python
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
```

To:

```python
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
```

#### F. Update Secret Key

In `app.py`, change line 18 from:

```python
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
```

To a random secret (generate one at https://randomkeygen.com/):

```python
import os
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-dev-key-change-me')
```

---

## Part 2: Upload to GitHub

### Step 1: Install Git (if not already installed)

**Windows:**
- Download Git from: https://git-scm.com/download/win
- Install with default settings
- Restart your terminal/command prompt

**Mac:**
- Git usually comes pre-installed
- Or install via: `brew install git`

**Verify installation:**
```bash
git --version
```

### Step 2: Create a GitHub Account

1. Go to https://github.com
2. Click "Sign up"
3. Create your account (it's free!)

### Step 3: Create a New Repository on GitHub

1. Log into GitHub
2. Click the "+" icon (top right) → "New repository"
3. Repository name: `ai-fitness-trainer` (or any name you like)
4. Description: "AI-powered bicep curl counter using computer vision"
5. Select "Public" (required for free hosting)
6. **DO NOT** check "Add a README"
7. Click "Create repository"

### Step 4: Upload Your Code to GitHub

Open Command Prompt / Terminal and navigate to your project folder:

```bash
cd "C:\Users\p1a2r\OneDrive\Desktop\Git Hub Projects\Computer Vision Projects\Pose Estimation\web_app"
```

Then run these commands one by one:

```bash
# Initialize git repository
git init

# Configure your identity (replace with your info)
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Add all files to git
git add .

# Create your first commit
git commit -m "Initial commit - AI Fitness Trainer app"

# Connect to your GitHub repository (REPLACE with YOUR repository URL)
git remote add origin https://github.com/YOUR_USERNAME/ai-fitness-trainer.git

# Rename branch to main
git branch -M main

# Push code to GitHub
git push -u origin main
```

**Note:** Replace `YOUR_USERNAME` with your actual GitHub username!

When prompted, enter your GitHub username and password (or personal access token).

**If you need a Personal Access Token:**
1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token
3. Give it "repo" permissions
4. Copy the token and use it as your password

---

## Part 3: Deploy to Render (Free Forever)

Render is perfect for your app because:
- Free tier available
- Supports WebSockets
- Stays running 24/7 (with some limitations)
- Easy deployment from GitHub

### Step 1: Create Render Account

1. Go to https://render.com
2. Click "Get Started for Free"
3. Sign up with GitHub (easiest option)

### Step 2: Create a New Web Service

1. In Render dashboard, click "New +" → "Web Service"
2. Click "Connect a repository"
3. Give Render permission to access your GitHub
4. Find and select your `ai-fitness-trainer` repository
5. Click "Connect"

### Step 3: Configure Your Service

Fill in the following:

**Name:** `ai-fitness-trainer` (or any unique name)

**Region:** Choose closest to you

**Branch:** `main`

**Root Directory:** Leave empty

**Runtime:** `Python 3`

**Build Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
gunicorn --worker-class eventlet -w 1 app:app --bind 0.0.0.0:$PORT
```

**Instance Type:** `Free`

### Step 4: Add Environment Variables

Scroll down to "Environment Variables" section:

Click "Add Environment Variable":

**Key:** `SECRET_KEY`
**Value:** (paste a random secret from https://randomkeygen.com/)

**Key:** `PYTHON_VERSION`
**Value:** `3.11.0`

### Step 5: Deploy!

1. Click "Create Web Service"
2. Render will start building your app (this takes 5-10 minutes)
3. Watch the logs - you'll see it installing dependencies
4. Once you see "Build successful" and "Your service is live", you're done!

### Step 6: Access Your Live Website

Your app will be available at:
```
https://ai-fitness-trainer.onrender.com
```
(Replace `ai-fitness-trainer` with whatever name you chose)

---

## Part 4: Important Notes About Free Tier

### Render Free Tier Limitations:

1. **Sleeps after 15 minutes of inactivity**
   - First visitor after sleep will wait 30-60 seconds for app to wake up
   - Subsequent visitors get instant access

2. **750 hours/month free**
   - This is about 31 days, so essentially unlimited for one app

3. **Limited resources**
   - Should work fine for demo/portfolio purposes
   - May be slow with multiple simultaneous users

### Keeping Your App Awake (Optional)

If you want your app to respond instantly, use a free service like UptimeRobot:

1. Go to https://uptimerobot.com
2. Create free account
3. Add new monitor
4. Monitor Type: HTTP(s)
5. URL: Your Render URL
6. Monitoring Interval: 5 minutes
7. This pings your app every 5 minutes to keep it awake

**Note:** This uses your 750 hours faster, but still should last the full month.

---

## Part 5: Custom Domain (Optional - Free)

Want a custom domain like `yourname.com` instead of `.onrender.com`?

### Free Options:

1. **Freenom** (free domains):
   - Go to https://www.freenom.com
   - Get a free .tk, .ml, .ga, .cf, or .gq domain
   - In Render, go to Settings → Custom Domain
   - Follow instructions to connect

2. **GitHub Pages** (if you want a static landing page):
   - Create `yourname.github.io`
   - Redirect to your Render app

---

## Part 6: Making Updates to Your Live App

Whenever you want to update your deployed app:

```bash
# Make your changes to the code

# Add changes
git add .

# Commit changes
git commit -m "Description of what you changed"

# Push to GitHub
git push origin main
```

**Render will automatically detect the GitHub push and redeploy your app!** (takes 5-10 minutes)

---

## Part 7: Troubleshooting

### App won't start?

Check Render logs:
1. Go to your service dashboard
2. Click "Logs" tab
3. Look for error messages

Common issues:
- **Missing dependency:** Add it to `requirements.txt`, then push to GitHub
- **Port error:** Make sure you're using `$PORT` environment variable
- **Module not found:** Check your imports in `app.py`

### Camera not working?

Browser security requires HTTPS for camera access:
- Render automatically provides HTTPS ✓
- Make sure you're accessing via `https://` not `http://`
- Allow camera permissions when browser asks

### WebSocket errors?

Make sure:
- You're using `eventlet` worker class in Procfile
- SocketIO version in requirements.txt matches client library version
- CORS is enabled (already set in your `app.py`)

---

## Part 8: Alternative Free Hosting Options

If Render doesn't work for you, here are alternatives:

### 1. **Railway.app**
- Similar to Render
- Free $5/month credit (resets monthly)
- Very easy setup
- Good WebSocket support

### 2. **Fly.io**
- Free tier: 3GB storage, 160GB bandwidth
- Great for global deployment
- Slightly more complex setup

### 3. **PythonAnywhere** (NOT RECOMMENDED for this app)
- Free tier exists but:
- No WebSocket support on free tier ❌
- Would need major code changes

---

## Summary Checklist

- [ ] Install Git
- [ ] Create GitHub account
- [ ] Create `.gitignore`, `runtime.txt`, `Procfile`
- [ ] Update `requirements.txt` (use opencv-python-headless)
- [ ] Update `app.py` (PORT and SECRET_KEY)
- [ ] Create GitHub repository
- [ ] Push code to GitHub
- [ ] Create Render account
- [ ] Deploy web service on Render
- [ ] Add environment variables
- [ ] Wait for build to complete
- [ ] Test your live website!

---

## Your App Will Be Live At:

```
https://your-app-name.onrender.com
```

Share this link with anyone - it's a professional portfolio piece!

---

## Next Steps (Bonus)

Once deployed, consider:
1. Add Google Analytics to track visitors
2. Create a custom domain
3. Add more exercises (squats, pushups, etc.)
4. Build a mobile app version
5. Add user authentication and workout history
6. Create a README.md with screenshots for GitHub

---

## Need Help?

If you run into issues:
1. Check Render logs first
2. Search the error message on Stack Overflow
3. Check Render documentation: https://render.com/docs
4. GitHub Issues for Flask-SocketIO: https://github.com/miguelgrinberg/Flask-SocketIO/issues

---

**Congratulations! You're about to have a live AI application on the internet!** 🎉

This is a real portfolio piece you can share with employers, friends, and family.

Good luck with your deployment!
