# Render Deployment Configuration

This project is optimized for deployment on **Render.com** (free and paid tiers).

## Quick Start: Deploy to Render Free Tier

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Initial backend setup"
git push origin main
```

### Step 2: Create Render Service
1. Go to [render.com](https://render.com) and sign up (free)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: oil-leak-detection-api
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:5000 --workers 2 app:create_app()`
   - **Instance Type**: Free ($0)

### Step 3: Add Environment Variables
In Render dashboard, add:
```
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
RENDER_FREE_TIER=true
```

### Step 4: Deploy
Click "Create Web Service" and Render will auto-build & deploy!

## Free Tier Notes
- ⏰ Spins down after 15 min inactivity (cold starts)
- 💾 512MB RAM (optimized config uses ~300MB)
- 🔒 Limited CPU (processes frames sequentially)
- 📊 No persistent storage (images not saved on free tier)
- ✅ Works well for API-only, detection runs locally

## API URL
Once deployed, your API will be at:
```
https://oil-leak-detection-api.onrender.com
```

## Upgrading to Starter Plan ($12/month)
If free tier doesn't meet needs:
1. Go to Render dashboard
2. Select this service
3. "Settings" → "Instance Type" → "Starter"
4. Get 1GB RAM + always-on + fast starts

## Dockerfile Variants

- **Dockerfile** - Full production (use for paid tier)
- **Dockerfile.freetier** - Optimized for free tier (use this!)

## Testing Deployment

After deployment, test with:

```bash
# Health check
curl https://oil-leak-detection-api.onrender.com/api/health

# Register vehicle
curl -X POST https://oil-leak-detection-api.onrender.com/api/scan-qr \
  -H "Content-Type: application/json" \
  -d '{"win_number":"TEST001"}'

# Get dashboard
curl https://oil-leak-detection-api.onrender.com/api/dashboard
```

## Troubleshooting

**Deployment fails?**
- Check build logs in Render dashboard
- Verify requirements.txt is correct
- Ensure Python version matches runtime.txt

**Cold starts too slow?**
- Normal on free tier (15-20 sec after inactivity)
- Upgrade to Starter for always-on

**Out of memory?**
- Reduce frame resolution in config
- Use `RENDER_FREE_TIER=true` env var
- Move detection to frontend

**Database issues?**
- Free tier uses SQLite (ephemeral)
- Data resets on redeploy
- Upgrade to Starter + PostgreSQL add-on for persistence
