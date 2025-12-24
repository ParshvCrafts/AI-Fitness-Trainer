# ⚡ Quick Deploy to Railway - Command Reference

**Time to Deploy: ~15 minutes**

---

## 🚀 Step-by-Step Commands

### 1️⃣ Navigate to Project (In Terminal/CMD)

```bash
cd "c:\Users\p1a2r\OneDrive\Desktop\Git Hub Projects\Computer Vision Projects\Pose Estimation\web_app"
```

---

### 2️⃣ Check Git Status

```bash
git status
```

**Expected Output:** Should show modified files (Dockerfile, app.py, etc.)

---

### 3️⃣ Add All Changes

```bash
git add .
```

---

### 4️⃣ Commit Changes

```bash
git commit -m "Fixed all deployment issues for Railway - Ready to deploy"
```

---

### 5️⃣ Check if You're in Main Branch

```bash
git branch
```

**Should show:** `* main` (or `* master`)

If not on main:
```bash
git checkout main
```

Or rename branch:
```bash
git branch -M main
```

---

### 6️⃣ Push to GitHub

**Option A: If repository already exists**
```bash
git push origin main
```

**Option B: If this is first push**
```bash
git remote add origin https://github.com/YOUR_USERNAME/ai-fitness-trainer.git
git push -u origin main
```

**Replace `YOUR_USERNAME` with your GitHub username!**

---

### 7️⃣ Deploy to Railway (Web Interface)

1. Go to: https://railway.app/
2. Click **"Login with GitHub"**
3. Click **"New Project"**
4. Click **"Deploy from GitHub repo"**
5. If needed, click **"Configure GitHub App"** → Select your repository → **"Install & Authorize"**
6. Select **`ai-fitness-trainer`** repository
7. Railway auto-detects Dockerfile and starts building!

---

### 8️⃣ Add Environment Variables in Railway

In Railway Dashboard → Your Project → **Variables** tab:

| Variable | Value |
|----------|-------|
| `SECRET_KEY` | Use command below to generate ↓ |
| `FLASK_ENV` | `production` |
| `CORS_ORIGINS` | `*` |

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and paste as `SECRET_KEY` value.

Click **"Deploy"** to restart.

---

### 9️⃣ Get Your Live URL

Railway Dashboard → **Settings** → **Networking** → **"Generate Domain"**

Your URL: `https://your-app-name.up.railway.app`

**Click it to test!** 🎉

---

## ✅ Quick Verification

After deployment, test these:

- [ ] Landing page loads
- [ ] Click "Choose Your Arm" → Select Left/Right
- [ ] Click "Start Camera" → Grant permission
- [ ] Video feed appears with pose detection
- [ ] MIN Calibration works (curl arm up, hold 7 sec)
- [ ] MAX Calibration works (extend arm down, hold 7 sec)
- [ ] Rep counter increments when doing curls
- [ ] No errors in Railway logs

---

## 🆘 Quick Fixes

### Problem: "Permission denied" when pushing to GitHub
**Solution:**
```bash
git remote set-url origin https://YOUR_USERNAME@github.com/YOUR_USERNAME/ai-fitness-trainer.git
git push origin main
```
Use your GitHub Personal Access Token as password.

---

### Problem: Build fails in Railway
**Solution:**
- Check Railway build logs for specific error
- Most common issues are already fixed!
- Try "Redeploy" button in Railway

---

### Problem: App shows "Application Error"
**Solution:**
1. Check Railway logs for errors
2. Verify environment variables are set
3. Click "Restart" in Railway dashboard

---

### Problem: Camera doesn't work
**Solution:**
- Make sure you're using the HTTPS Railway URL (not HTTP)
- Grant camera permission in browser
- Try Chrome or Edge browser

---

## 📞 Need More Help?

Read the full guide: **[RAILWAY_DEPLOYMENT_GUIDE.md](RAILWAY_DEPLOYMENT_GUIDE.md)**

---

## 🎯 Success Indicator

When you see this in Railway logs:
```
✓ Deployed
Client connected: xyz...
```

**Congratulations! Your app is live!** 🎉

Share your URL: `https://your-app.up.railway.app`

---

**Quick Deploy Time:** ~15 minutes from start to finish!
