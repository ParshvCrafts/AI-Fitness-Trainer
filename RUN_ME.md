# How to Run Without Camera Issues

## The Problem
- **HTTPS has WebSocket SSL errors** causing lag and disconnections
- **HTTP blocks camera** on network IPs (10.42.108.58:5000)

## ✅ BEST SOLUTION: Use localhost

### Step 1: Run the regular app
```bash
python app.py
```

### Step 2: Access via localhost
Open browser and go to:
```
http://localhost:5000
```

**Why this works:**
- Browsers allow camera on localhost without HTTPS
- No SSL errors
- Faster, real-time performance

---

## If You Need Network Access (from other devices)

### Option 1: Use ngrok (Recommended)

1. **Download ngrok**: https://ngrok.com/download

2. **Run your app**:
```bash
python app.py
```

3. **In another terminal**:
```bash
ngrok http 5000
```

4. **Use the HTTPS URL** ngrok gives you (e.g., `https://abc123.ngrok.io`)

**Benefits:**
- ✅ Free HTTPS
- ✅ Works from any device/network
- ✅ No WebSocket issues
- ✅ No configuration needed

---

## What I Fixed

1. ✅ **Removed full pose skeleton** - Only draws angle lines now
2. ✅ **Original colors** - Black lines, red circles (like your AI Trainer)
3. ✅ **Faster frame rate** - 30 FPS (was 10 FPS)
4. ✅ **Optimized processing** - Real-time performance

---

## Quick Start

```bash
# Start server
python app.py

# Open browser
http://localhost:5000

# Done!
```

For network access, use ngrok as shown above.
