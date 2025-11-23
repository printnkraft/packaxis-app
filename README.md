# PackAxis Canada - Django Application

This is a Django web application for PackAxis Canada, a premium paper bag supplier.

## Setup Instructions

### 1. Prerequisites
- Python 3.14.0 (already installed in virtual environment)
- Django 5.2.8 (already installed)
- Pillow (already installed)

### 2. Virtual Environment
The virtual environment is already set up in the parent directory:
- Path: `C:/Users/pujan/OneDrive/Desktop/PackAxis Packaging/.venv`

### 3. Running the Development Server

To run the Django development server:

```powershell
cd "C:\Users\pujan\OneDrive\Desktop\PackAxis Packaging\PackAxis App"
& "C:/Users/pujan/OneDrive/Desktop/PackAxis Packaging/.venv/Scripts/python.exe" manage.py runserver
```

Then open your browser and visit: `http://127.0.0.1:8000/`

### 4. Database Migration

Before first run, create the database:

```powershell
cd "C:\Users\pujan\OneDrive\Desktop\PackAxis Packaging\PackAxis App"
& "C:/Users/pujan/OneDrive/Desktop/PackAxis Packaging/.venv/Scripts/python.exe" manage.py migrate
```

### 5. Create Admin User (Optional)

To access the admin panel at `/admin/`:

```powershell
& "C:/Users/pujan/OneDrive/Desktop/PackAxis Packaging/.venv/Scripts/python.exe" manage.py createsuperuser
```

## Project Structure

```
PackAxis App/
├── core/                   # Main application
│   ├── templates/
│   │   └── core/
│   │       ├── base.html   # Base template with header/footer
│   │       └── index.html  # Home page
│   ├── views.py           # View functions
│   └── urls.py            # URL routing
├── packaxis_app/          # Project settings
│   ├── settings.py        # Django settings
│   └── urls.py            # Main URL configuration
├── static/                # Static files
│   ├── css/
│   │   └── styles.css     # Main stylesheet
│   ├── js/
│   │   └── script.js      # JavaScript
│   └── images/            # Images and assets
└── manage.py              # Django management script
```

## Available URLs

- `/` - Home page
- `/shopping-paper-bags/` - Shopping Paper Bags product page
- `/brown-kraft-bags/` - Brown Kraft Bags product page
- `/white-paper-bags/` - White Paper Bags product page
- `/custom-branded-bags/` - Custom Branded Bags product page
- `/paper-straws/` - Paper Straws product page
- `/privacy-policy/` - Privacy Policy
- `/terms-of-service/` - Terms of Service
- `/admin/` - Admin panel

## Next Steps for E-commerce

To add e-commerce functionality in the future:

1. **Install additional packages:**
   ```powershell
   pip install django-crispy-forms stripe
   ```

2. **Create models for:**
   - Products
   - Orders
   - Cart
   - Customer information

3. **Add payment integration:**
   - Stripe or PayPal
   - Order management system

4. **Implement user authentication:**
   - User registration
   - Login/Logout
   - Customer dashboard

## Development Notes

- The current setup is a **static content** Django app that mirrors your existing HTML website
- All HTML files use Django template tags for dynamic URLs and static files
- The layout and design are identical to your original website
- Ready for future e-commerce features without changing the layout

## Static Files

Run `collectstatic` before deployment:

```powershell
& "C:/Users/pujan/OneDrive/Desktop/PackAxis Packaging/.venv/Scripts/python.exe" manage.py collectstatic
```

## Contact

For issues or questions about the Django application, contact your development team.
