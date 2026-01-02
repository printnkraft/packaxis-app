# Railway Migrations Script
$pythonPath = "C:/Users/pujan/OneDrive/Desktop/PackAxis Packaging/PackAxis App/venv/Scripts/python.exe"

Write-Host "Running migrations on Railway..." -ForegroundColor Green
railway run $pythonPath manage.py migrate

Write-Host "`nCreating superuser..." -ForegroundColor Green  
railway run $pythonPath manage.py createsuperuser
