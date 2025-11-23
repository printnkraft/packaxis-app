# Quick Start Guide - GitHub & PythonAnywhere Deployment

## ✅ Files Created:
- `requirements.txt` - Python packages needed
- `.gitignore` - Files to exclude from Git
- `DEPLOYMENT.md` - Complete deployment instructions
- Git repository initialized with initial commit

## 📋 Next Steps:

### 1. Create GitHub Repository (5 minutes)

1. Go to: https://github.com/new
2. Repository name: `packaxis-website`
3. Make it **Private** ✅
4. **Don't** initialize with README (we have one)
5. Click "Create repository"

### 2. Push Your Code (2 minutes)

Copy these commands from GitHub (they'll look like this):

```bash
cd "C:\Users\pujan\OneDrive\Desktop\PackAxis Packaging\PackAxis App"
git remote add origin https://github.com/YOUR_USERNAME/packaxis-website.git
git branch -M main
git push -u origin main
```

### 3. Sign Up for PythonAnywhere (5 minutes)

1. Go to: https://www.pythonanywhere.com/registration/register/hacker/
2. Choose username (e.g., `packaxis`)
3. Enter email: packaxiscanada@gmail.com
4. Create password
5. Pay $5 for Hacker plan

### 4. Follow Deployment Guide (20 minutes)

Open the `DEPLOYMENT.md` file and follow steps 2-7.

---

## 🎯 What You'll Have After Deployment:

✅ Website live at: `https://YOUR_USERNAME.pythonanywhere.com`
✅ Admin panel: `https://YOUR_USERNAME.pythonanywhere.com/superusers/`
✅ Version control with Git
✅ Easy updates via `git push`
✅ MySQL database
✅ Free SSL certificate
✅ Email notifications working

---

## 💰 Monthly Cost: $5

## 📞 Need Help?

- Check `DEPLOYMENT.md` for detailed instructions
- PythonAnywhere has excellent support docs
- Their forums are very helpful

---

## 🔄 To Update Website Later:

```bash
# Make changes to your files
git add .
git commit -m "Updated products"
git push origin main

# Then on PythonAnywhere console:
cd ~/packaxis-website
git pull origin main
python manage.py collectstatic --noinput
# Click Reload button in Web tab
```

---

## ⚡ Quick Commands:

**Check Git status:**
```bash
cd "C:\Users\pujan\OneDrive\Desktop\PackAxis Packaging\PackAxis App"
git status
```

**See your commits:**
```bash
git log --oneline
```

**Create a new feature branch:**
```bash
git checkout -b new-feature
```

---

## 📝 Important Notes:

1. **Never commit** your `.env` file or sensitive data
2. **Always test locally** before pushing to production
3. **Backup your database** regularly
4. **Use meaningful commit messages**

Example good commits:
- ✅ "Added newsletter signup form"
- ✅ "Fixed contact form validation"
- ✅ "Updated product images"

Example bad commits:
- ❌ "Updates"
- ❌ "asdf"
- ❌ "test"

---

**You're all set! Ready to deploy? Start with GitHub! 🚀**
