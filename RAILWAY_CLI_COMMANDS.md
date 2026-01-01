# 🚂 Railway CLI Commands Quick Reference

## Installation
```bash
npm install -g @railway/cli
```

## Authentication
```bash
railway login          # Login to Railway
railway whoami         # Check current user
railway logout         # Logout
```

## Project Management
```bash
railway init           # Initialize new project
railway link           # Link to existing project
railway list           # List all projects
railway status         # Show project status
```

## Deployment
```bash
railway up             # Deploy current directory
railway up --detach    # Deploy in background
```

## Environment Variables
```bash
railway variables                    # List all variables
railway variables set KEY=VALUE      # Set variable
railway variables delete KEY         # Delete variable
```

## Database
```bash
railway run python manage.py migrate              # Run migrations
railway run python manage.py createsuperuser      # Create admin user
railway run python manage.py collectstatic        # Collect static files
railway run python manage.py shell                # Django shell
```

## Logs & Monitoring
```bash
railway logs                # View recent logs
railway logs --tail         # Follow logs in real-time
railway logs --tail -n 100  # Show last 100 lines
```

## Service Management
```bash
railway restart            # Restart service
railway down               # Stop service
railway open               # Open deployed URL in browser
```

## Useful Django Management Commands
```bash
# Create superuser
railway run python manage.py createsuperuser

# Make migrations
railway run python manage.py makemigrations

# Run migrations
railway run python manage.py migrate

# Collect static files
railway run python manage.py collectstatic --noinput

# Clear cache
railway run python manage.py shell -c "from django.core.cache import cache; cache.clear()"

# Load fixtures
railway run python manage.py loaddata your_data.json

# Database shell
railway run python manage.py dbshell
```

## Troubleshooting Commands
```bash
# Check deployment status
railway status

# View real-time logs
railway logs --tail

# Restart if stuck
railway restart

# Connect to PostgreSQL directly
railway connect postgres

# Run Django check
railway run python manage.py check

# Show environment variables
railway variables
```

## Quick Deploy Workflow
```bash
# 1. Make changes locally
git add .
git commit -m "Your changes"

# 2. Push to GitHub (Railway auto-deploys)
git push origin main

# 3. Monitor deployment
railway logs --tail

# 4. Test deployment
railway open
```
