# 🚀 Railway Deployment Checklist

## ✅ Pre-Deployment (Complete These First)

### 1. Backblaze B2 Setup
- [ ] Create Backblaze B2 account
- [ ] Create bucket (e.g., `packaxis-media`)
- [ ] Set bucket to **Public**
- [ ] Create Application Key (Read & Write access)
- [ ] Copy `keyID` and `applicationKey`
- [ ] Note your endpoint URL (e.g., `s3.us-west-004.backblazeb2.com`)

### 2. Cloudflare DNS Setup
- [ ] Domain DNS already moved to Cloudflare ✓
- [ ] Add CNAME for CDN (e.g., `cdn.yourdomain.com` → `f004.backblazeb2.com`)
- [ ] Enable Proxy (orange cloud) on CDN CNAME
- [ ] SSL/TLS set to **Full (strict)**
- [ ] Enable "Always Use HTTPS"

### 3. Generate Production Secrets
- [ ] Run `python generate_secret_key.py` (already done)
- [ ] Copy generated SECRET_KEY: `qo&p@2p^hmx0s57%85s0ar9w^3qop%l=j=8gf-2paxt0mki+st`
- [ ] Prepare email app password (if using Gmail)

---

## 🔧 Railway Deployment Steps

### Step 1: Create Railway Project
```bash
1. Go to https://railway.app
2. Sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your repository
```

### Step 2: Add PostgreSQL Database
```bash
1. In Railway project dashboard
2. Click "+ New" 
3. Select "Database" → "PostgreSQL"
4. Wait for provisioning (auto-adds DATABASE_URL)
```

### Step 3: Configure Environment Variables
Go to Railway → Your Project → **Variables** tab

Copy these variables (update with your actual values):

```bash
# Core Django
SECRET_KEY=qo&p@2p^hmx0s57%85s0ar9w^3qop%l=j=8gf-2paxt0mki+st
DEBUG=False
ALLOWED_HOSTS=your-app.up.railway.app,yourdomain.com,www.yourdomain.com
DJANGO_SETTINGS_MODULE=packaxis_app.settings
PYTHONUNBUFFERED=1

# Backblaze B2 (REPLACE WITH YOUR VALUES)
USE_B2_STORAGE=True
B2_KEY_ID=your_actual_key_id
B2_APPLICATION_KEY=your_actual_application_key
B2_BUCKET=packaxis-media
B2_ENDPOINT=s3.us-west-004.backblazeb2.com
B2_REGION=us-west-004
B2_CUSTOM_DOMAIN=cdn.yourdomain.com

# Email (Optional - update with your details)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=Packaxis Packaging <noreply@packaxis.ca>

# Sentry (Optional)
SENTRY_DSN=https://your-dsn@sentry.io/project-id
SENTRY_TRACES_SAMPLE_RATE=0.1
```

### Step 4: Push Code to GitHub
```bash
cd "c:\Users\pujan\OneDrive\Desktop\PackAxis Packaging\PackAxis App"
git add .
git commit -m "Add Railway deployment configuration"
git push origin main
```

Railway will automatically start deploying!

### Step 5: Monitor Deployment
```bash
# In Railway dashboard, click on your service
# Watch the "Deployments" tab
# Check logs for any errors
```

### Step 6: Add Custom Domain
```bash
1. In Railway → Settings → Domains
2. Click "+ Custom Domain"
3. Enter: yourdomain.com
4. Note the CNAME target Railway provides
```

### Step 7: Update Cloudflare DNS
```bash
1. Go to Cloudflare → DNS
2. Add/Update CNAME record:
   Type: CNAME
   Name: @
   Target: your-app.up.railway.app
   Proxy: ✅ Proxied (orange cloud)

3. Add www subdomain:
   Type: CNAME
   Name: www  
   Target: yourdomain.com
   Proxy: ✅ Proxied
```

### Step 8: Create Superuser
```bash
# Option A: Via Railway CLI
railway run python manage.py createsuperuser

# Option B: Via Railway Dashboard
# Go to your service → Settings → "Run a Command"
# Enter: python manage.py createsuperuser
```

---

## 🧪 Post-Deployment Testing

### Test These URLs:
- [ ] `https://yourdomain.com` - Homepage loads
- [ ] `https://yourdomain.com/admin` - Admin accessible
- [ ] `https://yourdomain.com/products` - Products page works
- [ ] `https://cdn.yourdomain.com/` - CDN accessible
- [ ] Upload test image in admin - verify B2 storage works
- [ ] Check mobile menu functionality
- [ ] Test search functionality
- [ ] Test product detail pages
- [ ] Test cart functionality

### Check Browser Console:
- [ ] No JavaScript errors
- [ ] No missing resources (404s)
- [ ] No mixed content warnings

### Check Railway Logs:
```bash
railway logs --tail
```
- [ ] No Python errors
- [ ] Database connections successful
- [ ] Static files served correctly

---

## 🔒 Security Verification

- [ ] `DEBUG=False` is set
- [ ] HTTPS redirects working (Cloudflare)
- [ ] Admin panel only accessible via HTTPS
- [ ] SECRET_KEY is secure and not in git
- [ ] B2 bucket permissions correct (public read)
- [ ] ALLOWED_HOSTS includes all domains
- [ ] Cloudflare SSL set to "Full (strict)"

---

## 🎯 Performance Optimization

### Cloudflare Page Rules (Optional):
```bash
1. cdn.yourdomain.com/*
   - Cache Level: Cache Everything
   - Edge Cache TTL: 1 month

2. yourdomain.com/static/*
   - Cache Level: Cache Everything

3. yourdomain.com/media/*  
   - Cache Level: Cache Everything
```

### Railway Scaling (if needed):
```bash
Settings → Resources
- Adjust memory/CPU if experiencing slowdowns
- Monitor usage in "Metrics" tab
```

---

## 🐛 Troubleshooting Guide

### Issue: Deployment Failed
**Check:**
- Railway build logs for errors
- requirements.txt is complete
- Procfile is correct
- Python version compatible

**Fix:**
```bash
railway logs --tail
```

### Issue: Static Files Not Loading
**Fix:**
```bash
railway run python manage.py collectstatic --noinput --clear
```

### Issue: Media Uploads Fail
**Check:**
- B2_KEY_ID and B2_APPLICATION_KEY correct
- B2_BUCKET name matches exactly
- Bucket is set to Public
- B2_ENDPOINT URL correct

**Fix:** Re-verify B2 credentials in Railway variables

### Issue: Database Connection Error
**Check:**
- PostgreSQL addon is running
- DATABASE_URL is automatically set

**Fix:** 
```bash
# Restart PostgreSQL addon
# Or recreate it if corrupted
```

### Issue: 502 Bad Gateway
**Check Railway logs:**
```bash
railway logs --tail
```
**Common causes:**
- Python syntax error
- Missing package in requirements.txt
- Database migration needed
- Gunicorn startup failed

**Fix:**
```bash
railway run python manage.py migrate
railway restart
```

### Issue: Custom Domain Not Working
**Check:**
- Cloudflare DNS propagated (24-48 hours max)
- CNAME points to correct Railway domain
- Orange cloud (Proxied) enabled in Cloudflare
- ALLOWED_HOSTS includes the domain

**Fix:**
```bash
# Update ALLOWED_HOSTS in Railway variables
ALLOWED_HOSTS=your-app.up.railway.app,yourdomain.com,www.yourdomain.com
```

---

## 📞 Support & Resources

- **Railway Docs**: https://docs.railway.app
- **Railway Community**: https://discord.gg/railway
- **Backblaze B2**: https://help.backblaze.com
- **Cloudflare Support**: https://support.cloudflare.com
- **Django Deployment**: https://docs.djangoproject.com/en/5.2/howto/deployment/

---

## ✅ Deployment Complete!

Once all checklist items are ✅, your PackAxis Packaging site is LIVE! 🎉

**Next Steps:**
1. Add products via admin panel
2. Configure payment gateway (if using Stripe)
3. Set up email marketing (if applicable)
4. Monitor with Sentry for errors
5. Set up database backups on Railway
6. Add Google Analytics (optional)

---

**Your Production Site**: https://yourdomain.com  
**Admin Panel**: https://yourdomain.com/admin  
**Railway Dashboard**: https://railway.app/dashboard
