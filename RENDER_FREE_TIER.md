# Render Free Tier Deployment Guide

## Render Free Tier Limitations
- **RAM**: 512MB (very tight with OpenCV)
- **CPU**: Shared, low priority
- **Storage**: Ephemeral (wiped on redeploy)
- **Inactivity**: Spins down after 15 min (cold starts)
- **Bandwidth**: Limited

## Current Setup Issues
❌ `opencv-python` (full GUI version) = 150MB+ RAM used  
❌ `psycopg2-binary` (PostgreSQL) = unnecessary for free tier  
❌ Local image storage = will be wiped  

## Recommended Approach for Free Tier

### Option 1: Lightweight Detection Only
- Run **frame analysis only** on Render (no storage)
- Send results to frontend for decision
- Frontend stores images locally/in cloud

### Option 2: Use Serverless Functions Instead
- **Better fit**: Firebase Functions, AWS Lambda, Replicate
- Process frames on-demand, not 24/7
- Only pay for actual processing

### Option 3: Upgrade Render Plan
- **Starter**: $12/month = 1GB RAM + always-on
- Much better for real-time processing

## Free Tier Optimizations (if continuing)

1. **Use headless OpenCV** ✓ (already fixed)
2. **Remove image storage** - use cloud (S3, Firebase)
3. **Reduce frame processing** - lower resolution, FPS
4. **Lazy load** - only process on demand, not continuous

## Updated config.py for Free Tier

```python
# Reduce processing load
FRAME_WIDTH = 480      # Was 640
FRAME_HEIGHT = 360     # Was 480
FRAME_RATE = 10        # Was 20 - less processing

MIN_CONTOUR_AREA = 1000  # Higher threshold = less processing

# Use SQLite (local/ephemeral is fine for free tier)
DATABASE_URL = 'sqlite:///detection.db'

# Store images in S3 instead of locally
USE_S3_STORAGE = True
```

## My Recommendation

**For testing phase with free tier:**
1. ✅ Keep backend lightweight (API only)
2. ✅ Store results in database, NOT files
3. ✅ Have frontend handle storage
4. ⚠️ Don't expect 24/7 uptime or fast cold starts

**For production:**
- Upgrade to Render Starter ($12/month)
- Or move to AWS Lambda (pay per invocation)
- Or use Vercel serverless functions for processing

## Deploy to Free Tier

```bash
# Push to GitHub
git push origin main

# Create Render service:
# 1. Sign up at render.com (free tier)
# 2. New > Web Service
# 3. Connect GitHub repo
# 4. Build command: pip install -r requirements.txt
# 5. Start command: gunicorn -w 2 -b 0.0.0.0:5000 app:create_app()
# 6. Add env var: FLASK_ENV=production
```

**Will it work?** Yes, but:
- Expect slow response times
- Expect cold starts (15-20 sec after inactivity)
- Don't upload large frames frequently
- Monitor memory usage

## Better Alternative: Keep Render for API, Process Locally

**For testing**: Run detection locally on your machine/camera system, send results to Render API (just storage/stats).

This way you get:
✅ Real-time detection (local)
✅ Minimal Render load (just API)
✅ Works on free tier
