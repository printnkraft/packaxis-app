# Railway Simple Deploy Script
# This creates a one-time command to run migrations on Railway

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "  RAILWAY MIGRATION WORKAROUND" -ForegroundColor Yellow
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""
Write-Host "Since Railway CLI has issues running commands from Windows," -ForegroundColor White
Write-Host "we'll use Railway's REST API to trigger a one-time command." -ForegroundColor White
Write-Host ""
Write-Host "MANUAL STEPS:" -ForegroundColor Green
Write-Host "1. Go to: https://railway.app/dashboard" -ForegroundColor White
Write-Host "2. Click on your 'packaxis-app' service" -ForegroundColor White
Write-Host "3. Click the three dots (...) menu" -ForegroundColor White
Write-Host "4. Look for 'Run Command' or similar option" -ForegroundColor White
Write-Host "5. Enter: python manage.py migrate" -ForegroundColor Yellow
Write-Host "6. Press Enter/Submit" -ForegroundColor White
Write-Host ""
Write-Host "Then to create superuser:" -ForegroundColor Green
Write-Host "1. Run another command: python manage.py createsuperuser" -ForegroundColor Yellow
Write-Host "2. Follow the prompts in the Railway dashboard" -ForegroundColor White
Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to open Railway dashboard in browser..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Start-Process "https://railway.app/dashboard"
