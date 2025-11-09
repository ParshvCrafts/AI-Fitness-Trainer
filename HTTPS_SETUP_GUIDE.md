# Enable HTTPS for Camera Access on Local Network

## The Problem

Browsers block camera access on non-localhost addresses (like `10.42.108.58:5000`) for security reasons. You need HTTPS to access the camera from a local network IP.

---

## Solution: Enable HTTPS with Self-Signed Certificate

### Step 1: Install pyOpenSSL

```bash
pip install pyOpenSSL
```

### Step 2: Generate SSL Certificate

```bash
cd web_app
python generate_cert.py
```

This creates two files:
- `cert.pem` - SSL certificate
- `key.pem` - Private key

### Step 3: Run HTTPS Server

```bash
python app_https.py
```

### Step 4: Access via HTTPS

Open your browser and go to:
```
https://10.42.108.58:5000
```

### Step 5: Accept the Security Warning

**Chrome/Edge:**
1. You'll see "Your connection is not private"
2. Click **"Advanced"**
3. Click **"Proceed to 10.42.108.58 (unsafe)"**

**Firefox:**
1. You'll see "Warning: Potential Security Risk Ahead"
2. Click **"Advanced..."**
3. Click **"Accept the Risk and Continue"**

**Safari:**
1. Click **"Show Details"**
2. Click **"visit this website"**
3. Click **"Visit Website"**

### Step 6: Allow Camera Access

Now when you click "Enable Camera", the browser will allow it!

---

## Alternative Solutions

### Solution 1: Use localhost (If accessing from same machine)

```
http://localhost:5000
```

Browsers allow camera on localhost without HTTPS.

### Solution 2: Chrome Flag (Temporary - Not Recommended)

**Chrome only:**
1. Go to: `chrome://flags/#unsafely-treat-insecure-origin-as-secure`
2. Add: `http://10.42.108.58:5000`
3. Select: **"Enabled"**
4. Restart Chrome

**Warning:** This reduces security. Use only for testing.

### Solution 3: Use ngrok (Easiest for remote access)

```bash
# Install ngrok from https://ngrok.com
ngrok http 5000
```

You'll get a public HTTPS URL like: `https://abc123.ngrok.io`

---

## Troubleshooting

### "Certificate files not found"
Run: `python generate_cert.py` first

### "Module not found: OpenSSL"
Install: `pip install pyOpenSSL`

### Browser still blocks camera
- Ensure you're using HTTPS (not HTTP)
- Clear browser cache and cookies
- Check site permissions in browser settings
- Try incognito/private mode

### "Connection refused"
- Ensure app is running: `python app_https.py`
- Check firewall settings
- Verify IP address: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)

---

## Complete Setup Commands

```bash
# 1. Install SSL library
pip install pyOpenSSL

# 2. Generate certificate
cd web_app
python generate_cert.py

# 3. Run HTTPS server
python app_https.py

# 4. Open browser
# Go to: https://10.42.108.58:5000
# Accept security warning
# Enable camera
```

---

## Files Created

- `generate_cert.py` - Script to generate SSL certificate
- `app_https.py` - HTTPS version of the app
- `cert.pem` - SSL certificate (generated)
- `key.pem` - Private key (generated)

---

## Security Notes

**For Development Only:**
- Self-signed certificates are for development/testing
- Not suitable for production deployment
- Browsers will show security warnings

**For Production:**
- Use a proper SSL certificate (Let's Encrypt, Cloudflare, etc.)
- Deploy to cloud platform with built-in SSL
- See DEPLOYMENT_GUIDE.md for production setup

---

## Quick Reference

| Scenario | Solution | URL |
|----------|----------|-----|
| Same machine | Use localhost | `http://localhost:5000` |
| Local network | HTTPS with cert | `https://10.42.108.58:5000` |
| Remote access | Use ngrok | `https://abc123.ngrok.io` |
| Production | Cloud deployment | `https://yourdomain.com` |

---

## Need More Help?

Check the main README.md or DEPLOYMENT_GUIDE.md for more options.
