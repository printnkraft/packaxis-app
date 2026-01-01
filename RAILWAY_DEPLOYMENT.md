# PackAxis Packaging - Railway Deployment Guide

## 🚀 Quick Deploy to Railway

### 1. Create Railway Account & Project
1. Go to [Railway.app](https://railway.app)
2. Sign in with GitHub
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Choose your `PackAxis Packaging` repository

### 2. Add PostgreSQL Database
1. In your Railway project, click **"+ New"**
2. Select **"Database"** → **"PostgreSQL"**
3. Railway will automatically add `DATABASE_URL` to your environment

### 3. Configure Environment Variables
In Railway project settings → **Variables**, add these:

#### 🔐 Required Django Settings
```bash
SECRET_KEY=your-super-secret-key-here-generate-new-one
DEBUG=False
ALLOWED_HOSTS=your-domain.railway.app,yourdomain.com,www.yourdomain.com
```

#### 🗄️ Backblaze B2 Storage (Required for Media Files)
```bash
USE_B2_STORAGE=True
B2_KEY_ID=your_backblaze_key_id
B2_APPLICATION_KEY=your_backblaze_application_key
B2_BUCKET=your-bucket-name
B2_ENDPOINT=s3.us-west-004.backblazeb2.com
B2_REGION=us-west-004
B2_CUSTOM_DOMAIN=cdn.yourdomain.com
```

#### 📧 Email Configuration (Optional but recommended)
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=Packaxis Packaging <noreply@packaxis.ca>
```

#### 🔔 Sentry Error Tracking (Optional)
```bash
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
SENTRY_TRACES_SAMPLE_RATE=0.1
```

#### 💳 Stripe Payment (If using)
```bash
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

#### 🔧 Additional Settings
```bash
DJANGO_SETTINGS_MODULE=packaxis_app.settings
PYTHONUNBUFFERED=1
PORT=8000
```

### 4. Setup Backblaze B2 Bucket

#### A. Create B2 Bucket
1. Go to [Backblaze B2](https://www.backblaze.com/b2/cloud-storage.html)
2. Create account or sign in
3. Navigate to **"Buckets"** → **"Create a Bucket"**
4. Bucket Settings:
   - **Bucket Name**: `packaxis-media` (or your choice)
   - **Files in Bucket**: **Public**
   - **Encryption**: None (for CDN compatibility)
   - **Object Lock**: Disabled

#### B. Create Application Key
1. Go to **"App Keys"** → **"Add a New Application Key"**
2. Settings:
   - **Name**: `railway-packaxis`
   - **Access**: Read and Write
   - **Bucket**: Select your bucket or "All"
3. Copy `keyID` → Use as `B2_KEY_ID`
4. Copy `applicationKey` → Use as `B2_APPLICATION_KEY`

#### C. Get Endpoint URL
1. In your bucket details, find **"Endpoint"**
2. It will look like: `s3.us-west-004.backblazeb2.com`
3. Use this as `B2_ENDPOINT`
4. Region is part of endpoint: `us-west-004` → Use as `B2_REGION`

### 5. Setup Cloudflare CDN (Optional but Recommended)

#### A. Add Cloudflare to Backblaze
1. In Cloudflare dashboard, go to **DNS**
2. Add CNAME record:
   - **Type**: CNAME
   - **Name**: `cdn` (or `media`)
   - **Target**: `f004.backblazeb2.com` (check your B2 endpoint)
   - **Proxy status**: ✅ Proxied (orange cloud)
3. Your CDN URL: `https://cdn.yourdomain.com`

#### B. Configure Cloudflare for B2
1. Go to **Rules** → **Transform Rules** → **Modify Response Header**
2. Create rule:
   - **Field**: Custom filter expression
   - **Expression**: `(http.host eq "cdn.yourdomain.com")`
   - **Then**: Set static → `Access-Control-Allow-Origin` → `*`

3. Set `B2_CUSTOM_DOMAIN=cdn.yourdomain.com` in Railway

### 6. Domain Setup with Cloudflare

#### A. Add Domain to Railway
1. In Railway project → **Settings** → **Domains**
2. Click **"+ Custom Domain"**
3. Enter: `yourdomain.com`
4. Railway provides:
   - CNAME target: `your-app.up.railway.app`
   - Or A record: IP address

#### B. Configure Cloudflare DNS
1. In Cloudflare → **DNS**
2. Add records:

**Option 1: CNAME (Recommended)**
```
Type: CNAME
Name: @ (root)
Target: your-app.up.railway.app
Proxy: ✅ Proxied
```

**www subdomain**
```
Type: CNAME
Name: www
Target: yourdomain.com
Proxy: ✅ Proxied
```

**Option 2: A Record**
```
Type: A
Name: @
IPv4: Railway IP address
Proxy: ✅ Proxied
```

#### C. Update ALLOWED_HOSTS
```bash
ALLOWED_HOSTS=your-domain.railway.app,yourdomain.com,www.yourdomain.com
```

### 7. Deploy!

#### Automatic Deployment
1. Push code to GitHub:
```bash
git add .
git commit -m "Configure for Railway deployment"
git push origin main
```
2. Railway auto-deploys from GitHub

#### Manual Deployment via Railway CLI
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link project
railway link

# Deploy
railway up
```

### 8. Post-Deployment Tasks

#### A. Create Superuser
```bash
railway run python manage.py createsuperuser
```

#### B. Collect Static Files (if not done automatically)
```bash
railway run python manage.py collectstatic --noinput
```

#### C. Run Migrations
```bash
railway run python manage.py migrate
```

#### D. Load Initial Data (if you have fixtures)
```bash
railway run python manage.py loaddata your_fixture.json
```

### 9. Verify Deployment

#### Check these URLs:
- ✅ `https://yourdomain.com` - Homepage loads
- ✅ `https://yourdomain.com/admin` - Admin panel accessible
- ✅ `https://yourdomain.com/products` - Product pages work
- ✅ Check browser console for no errors
- ✅ Upload test image - verify B2 storage works
- ✅ Test checkout process

#### Monitor Logs:
```bash
railway logs
```

### 10. Cloudflare SSL/TLS Settings

1. Go to **SSL/TLS** → **Overview**
2. Set to **Full (strict)**
3. Go to **Edge Certificates**
4. Enable:
   - ✅ Always Use HTTPS
   - ✅ Automatic HTTPS Rewrites
   - ✅ Opportunistic Encryption

### 11. Performance Optimization

#### A. Cloudflare Caching
1. **Page Rules** (create these):
   - `cdn.yourdomain.com/*` → Cache Level: Cache Everything, Edge TTL: 1 month
   - `yourdomain.com/static/*` → Cache Level: Cache Everything
   - `yourdomain.com/media/*` → Cache Level: Cache Everything

#### B. Railway Scaling
- Go to **Settings** → **Resources**
- Increase if needed (default is usually fine)

### 🎉 Deployment Complete!

Your app should now be live at `https://yourdomain.com`

---

## 🔧 Troubleshooting

### Issue: Static files not loading
**Solution**: 
```bash
railway run python manage.py collectstatic --noinput --clear
```

### Issue: Database connection errors
**Solution**: Check `DATABASE_URL` is set correctly in Railway variables

### Issue: Media files not uploading
**Solution**: Verify B2 credentials and bucket is public

### Issue: 502 Bad Gateway
**Solution**: Check Railway logs for Python errors
```bash
railway logs --tail
```

### Issue: ALLOWED_HOSTS error
**Solution**: Add all domains to `ALLOWED_HOSTS` including Railway domain

---

## 📞 Support Resources

- **Railway Docs**: https://docs.railway.app
- **Backblaze B2 Docs**: https://www.backblaze.com/docs/cloud-storage
- **Cloudflare Docs**: https://developers.cloudflare.com
- **Django Deployment**: https://docs.djangoproject.com/en/5.2/howto/deployment/

---

## 🔒 Security Checklist

- ✅ `DEBUG=False` in production
- ✅ Strong `SECRET_KEY` generated
- ✅ `ALLOWED_HOSTS` properly configured
- ✅ HTTPS enabled via Cloudflare
- ✅ Database backups enabled on Railway
- ✅ Sentry error tracking configured
- ✅ Environment variables secured
- ✅ B2 bucket permissions set correctly
