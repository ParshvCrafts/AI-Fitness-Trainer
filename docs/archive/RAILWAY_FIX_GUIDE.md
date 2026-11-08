# 🚀 Railway Deployment Fix - Dashboard Configuration

## ⚠️ The Problem

Railway is trying to run the wrong application because your GitHub repository contains the entire "Computer Vision Projects" folder, not just the `web_app` folder.

**The logs show:**
```
2025-12-24 17:06:43 | INFO | src.api.main:lifespan:182 | Shutting down application
```

This is **NOT** your AI Fitness Trainer app! Railway is detecting a different service.

---

## ✅ The Solution (Simple - 5 Minutes)

**Configure Railway through the Dashboard** (no Git needed!)

### Step 1: Go to Your Railway Project

1. Go to [railway.app](https://railway.app/)
2. Sign in
3. Click on your "AI-Fitness-Trainer" project

---

### Step 2: Configure Root Directory

1. Click on your service (the deployment)
2. Go to **"Settings"** tab
3. Scroll to **"Build"** section
4. Look for **"Root Directory"** or **"Working Directory"**
5. Set it to: `Pose Estimation/web_app`
6. Click **"Save"** or **"Update"**

---

### Step 3: Configure Dockerfile Path

1. Still in **"Settings"** → **"Build"** section
2. Look for **"Dockerfile Path"**
3. Set it to: `Dockerfile` (since we're already in the web_app directory)
4. Click **"Save"**

---

### Step 4: Verify Start Command

1. Scroll to **"Deploy"** section
2. Look for **"Start Command"** or **"Custom Start Command"**
3. It should be: `python app.py`
4. If it's different, change it to `python app.py`
5. Click **"Save"**

---

### Step 5: Redeploy

1. Go to **"Deployments"** tab
2. Click **"Deploy"** or **"Redeploy"** button
3. Wait 5-10 minutes for build

---

## 📊 Expected Build Output

After redeploying with correct settings, you should see:

```
✓ Fetching snapshot from GitHub
✓ Using root directory: Pose Estimation/web_app
✓ Found Dockerfile at: Pose Estimation/web_app/Dockerfile
✓ Building Docker image
  FROM python:3.10-slim ✓
  WORKDIR /app ✓
  RUN apt-get install libgl1 ffmpeg... ✓
  RUN pip install Flask mediapipe opencv... ✓
✓ Build complete
✓ Deploying
✓ Deployment successful
```

**Runtime logs should show:**
```
INFO: Uvicorn running on http://0.0.0.0:5000
INFO: Application startup complete
```

**NOT:**
```
src.api.main:lifespan:182  ❌ (this was wrong!)
```

---

## 🎯 Alternative: Use Railway CLI (Advanced)

If dashboard doesn't have root directory option, use CLI:

### Install Railway CLI
```bash
npm install -g @railway/cli
```

Or download from: https://docs.railway.app/develop/cli

### Login
```bash
railway login
```

### Link Project
```bash
cd "c:\Users\p1a2r\OneDrive\Desktop\Git Hub Projects\Computer Vision Projects"
railway link
```
Select your "AI-Fitness-Trainer" project

### Set Root Directory
```bash
railway up --rootDir "Pose Estimation/web_app"
```

---

## 🔧 If That Doesn't Work: Create Separate Repository

**Best Long-term Solution:**

1. Create a **NEW** GitHub repository for ONLY the web_app
2. Copy ONLY the `web_app` folder contents to the new repo
3. Deploy the new repo to Railway

### Commands:
```bash
# Navigate to web_app
cd "c:\Users\p1a2r\OneDrive\Desktop\Git Hub Projects\Computer Vision Projects\Pose Estimation\web_app"

# Initialize new Git repo
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - AI Fitness Trainer web app"

# Create new GitHub repo (on GitHub.com)
# Name it: ai-fitness-trainer-app

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/ai-fitness-trainer-app.git

# Push
git push -u origin main
```

Then deploy THIS repo to Railway - it will work perfectly!

---

## ✅ Success Indicators

You'll know it's working when:

1. ✅ Railway build logs show: "Found Dockerfile at: Pose Estimation/web_app/Dockerfile"
2. ✅ Runtime logs show: `INFO: Uvicorn running on http://0.0.0.0:5000`
3. ✅ Runtime logs show: `Client connected: xyz123` (when you access the app)
4. ✅ NO mentions of `src.api.main` in logs
5. ✅ Your URL loads the AI Fitness Trainer landing page

---

## 🆘 Need Help?

If Railway dashboard doesn't have "Root Directory" option:

1. **Option A**: Use Railway CLI (see above)
2. **Option B**: Create separate repo for web_app (recommended)
3. **Option C**: Contact Railway support and ask how to set root directory

---

## 📝 Quick Checklist

Before redeploying:

- [ ] Root Directory set to: `Pose Estimation/web_app`
- [ ] Dockerfile Path set to: `Dockerfile`
- [ ] Start Command set to: `python app.py`
- [ ] Environment variables set (SECRET_KEY, FLASK_ENV, CORS_ORIGINS)
- [ ] Clicked "Redeploy" button

---

## 🎉 Next Steps After Successful Deployment

Once you see the correct logs:

1. Go to **"Settings"** → **"Networking"** → **"Generate Domain"**
2. Click your Railway URL
3. Test your AI Fitness Trainer app!
4. Camera permission → Calibration → Rep counting

---

**Good luck! The fix is simple - just configure the root directory in Railway dashboard!** 🚀
