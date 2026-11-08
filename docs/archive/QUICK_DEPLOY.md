# Quick Deploy Checklist

Follow these steps in order. Should take about 15-20 minutes total.

## Preparation (5 minutes)

- [x] All deployment files created (.gitignore, Procfile, runtime.txt)
- [x] requirements.txt updated (opencv-python-headless)
- [x] app.py updated (PORT and SECRET_KEY)
- [ ] Test locally: `python app.py` (visit http://localhost:5000)

## GitHub Upload (5 minutes)

```bash
# Navigate to your project
cd "C:\Users\p1a2r\OneDrive\Desktop\Git Hub Projects\Computer Vision Projects\Pose Estimation\web_app"

# Initialize Git
git init

# Configure Git (first time only)
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Add all files
git add .

# Commit
git commit -m "Initial commit - AI Fitness Trainer"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/ai-fitness-trainer.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Render Deployment (10 minutes)

1. **Create Account**
   - Go to https://render.com
   - Sign up with GitHub

2. **Create Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select `ai-fitness-trainer` repo

3. **Configure**
   ```
   Name: ai-fitness-trainer
   Region: (choose closest to you)
   Branch: main
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn --worker-class eventlet -w 1 app:app --bind 0.0.0.0:$PORT
   Instance Type: Free
   ```

4. **Environment Variables**
   - Click "Add Environment Variable"
   - Key: `SECRET_KEY`
   - Value: (generate at https://randomkeygen.com/)

5. **Deploy**
   - Click "Create Web Service"
   - Wait 5-10 minutes for build
   - Watch logs for "Your service is live"

6. **Test**
   - Visit: `https://your-app-name.onrender.com`
   - Allow camera access
   - Test calibration and rep counting

## Done!

Your app is now live on the internet!

## Share Your App

Copy this URL and share it:
```
https://your-app-name.onrender.com
```

## Making Updates

When you make changes:

```bash
git add .
git commit -m "Description of changes"
git push origin main
```

Render will automatically redeploy (takes 5-10 minutes).

## Need Help?

1. Check Render logs in dashboard
2. See DEPLOYMENT_COMPLETE_GUIDE.md for detailed troubleshooting
3. Visit Render docs: https://render.com/docs
