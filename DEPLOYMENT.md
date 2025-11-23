# PackAxis Deployment Guide - PythonAnywhere

## Prerequisites

1. GitHub account
2. PythonAnywhere Hacker account ($5/month)
3. Domain name (packaxis.ca) - optional

## Step 1: Push to GitHub

1. **Initialize Git** (if not already done):
```bash
cd "C:\Users\pujan\OneDrive\Desktop\PackAxis Packaging\PackAxis App"
git init
git add .
git commit -m "Initial commit - PackAxis website"
```

2. **Create GitHub Repository**:
   - Go to github.com
   - Click "New Repository"
   - Name: `packaxis-website`
   - Make it Private
   - Don't initialize with README (we have one)

3. **Push to GitHub**:
```bash
git remote add origin https://github.com/YOUR_USERNAME/packaxis-website.git
git branch -M main
git push -u origin main
```

## Step 2: Set Up PythonAnywhere

### 2.1 Create Account
1. Go to https://www.pythonanywhere.com
2. Sign up for **Hacker plan** ($5/month)
3. Verify your email

### 2.2 Clone Your Repository

1. Open **Bash console** on PythonAnywhere
2. Clone your repo:
```bash
git clone https://github.com/YOUR_USERNAME/packaxis-website.git
cd packaxis-website
```

### 2.3 Create Virtual Environment

```bash
mkvirtualenv --python=/usr/bin/python3.10 packaxis-env
pip install -r requirements.txt
```

### 2.4 Set Up Database

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### 2.5 Populate Initial Data

```bash
python manage.py populate_data
```

## Step 3: Configure Web App

1. Go to **Web** tab on PythonAnywhere dashboard
2. Click **Add a new web app**
3. Choose **Manual configuration**
4. Select **Python 3.10**

### 3.1 Update WSGI Configuration

1. Click on WSGI configuration file link
2. **Delete everything** and replace with:

```python
import os
import sys

# Add your project directory to the sys.path
path = '/home/YOUR_USERNAME/packaxis-website'
if path not in sys.path:
    sys.path.insert(0, path)

# Set environment variable for settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'packaxis_app.settings'

# Activate virtual environment
activate_this = '/home/YOUR_USERNAME/.virtualenvs/packaxis-env/bin/activate_this.py'
with open(activate_this) as f:
    exec(f.read(), {'__file__': activate_this})

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

3. Click **Save**

### 3.2 Set Virtual Environment Path

1. In **Web** tab, find "Virtualenv" section
2. Enter: `/home/YOUR_USERNAME/.virtualenvs/packaxis-env`

### 3.3 Configure Static Files

In **Web** tab, add these mappings:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/YOUR_USERNAME/packaxis-website/staticfiles` |
| `/media/` | `/home/YOUR_USERNAME/packaxis-website/media` |

### 3.4 Update Django Settings

Edit `packaxis_app/settings.py` on PythonAnywhere:

```bash
nano ~/packaxis-website/packaxis_app/settings.py
```

Update these settings:

```python
DEBUG = False

ALLOWED_HOSTS = ['YOUR_USERNAME.pythonanywhere.com', 'packaxis.ca', 'www.packaxis.ca']

# Database - MySQL for production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'YOUR_USERNAME$packaxis',
        'USER': 'YOUR_USERNAME',
        'PASSWORD': 'YOUR_DB_PASSWORD',
        'HOST': 'YOUR_USERNAME.mysql.pythonanywhere-services.com',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = [
    'https://YOUR_USERNAME.pythonanywhere.com',
    'https://packaxis.ca',
    'https://www.packaxis.ca'
]
```

Save: `Ctrl+O`, `Enter`, `Ctrl+X`

## Step 4: Set Up MySQL Database

1. Go to **Databases** tab
2. Note your MySQL password (or set new one)
3. Create database: `YOUR_USERNAME$packaxis`
4. Run migrations again:
```bash
cd ~/packaxis-website
python manage.py migrate
python manage.py populate_data
```

## Step 5: Reload Web App

1. Go to **Web** tab
2. Click big green **Reload** button
3. Visit: `https://YOUR_USERNAME.pythonanywhere.com`

## Step 6: Set Up Custom Domain (Optional)

1. Go to **Web** tab
2. Add custom domain: `packaxis.ca`
3. Follow DNS instructions:
   - Add CNAME record: `www` → `YOUR_USERNAME.pythonanywhere.com`
   - Add A record: `@` → (PythonAnywhere IP provided)
4. Enable HTTPS (automatic)

## Step 7: Configure Email (Gmail SMTP)

1. Generate Gmail App Password:
   - https://myaccount.google.com/apppasswords
   - App: Mail
   - Copy the password

2. Update settings on PythonAnywhere:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'packaxiscanada@gmail.com'
EMAIL_HOST_PASSWORD = 'YOUR_APP_PASSWORD'  # The 16-character app password
```

3. Reload web app

## Maintenance

### Update Website (Push Changes):

```bash
# On your local machine
git add .
git commit -m "Update description"
git push origin main

# On PythonAnywhere bash console
cd ~/packaxis-website
git pull origin main
python manage.py collectstatic --noinput
# Click Reload button in Web tab
```

### View Logs:

- Error log: Web tab → log files
- Server log: Web tab → server log

### Backup Database:

```bash
cd ~/packaxis-website
python manage.py dumpdata > backup.json
```

## Troubleshooting

### Site not loading:
- Check error log in Web tab
- Verify WSGI file paths
- Ensure virtual environment is correct

### Static files not showing:
- Run `collectstatic` again
- Check static file mappings
- Verify paths are absolute

### Database errors:
- Check MySQL credentials
- Ensure database exists
- Run migrations again

### Import errors:
- Activate virtual environment
- Install missing packages: `pip install PACKAGE_NAME`
- Reload web app

## Support

- PythonAnywhere Forums: https://www.pythonanywhere.com/forums/
- PythonAnywhere Help: https://help.pythonanywhere.com/
- Django Docs: https://docs.djangoproject.com/

## Costs

- **PythonAnywhere Hacker**: $5/month
- **Domain (packaxis.ca)**: ~$15/year (optional)
- **Total**: $5-6/month

---

**Your website will be live at:** `https://YOUR_USERNAME.pythonanywhere.com`

Or with custom domain: `https://packaxis.ca`
