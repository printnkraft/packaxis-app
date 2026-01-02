#!/usr/bin/env python
"""
Startup script for Railway deployment
Runs migrations and creates superuser before starting the app
"""
import os
import sys
import subprocess

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*50}")
    print(f"🔄 {description}")
    print(f"{'='*50}\n")
    
    result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
    
    if result.returncode == 0:
        print(f"✅ {description} completed successfully!")
    else:
        print(f"❌ {description} failed with exit code {result.returncode}")
        if "migrate" in description.lower():
            print("⚠️ Migration failed but continuing...")
        else:
            sys.exit(result.returncode)
    
    return result.returncode

def main():
    print("\n" + "="*50)
    print("🚀 PackAxis Deployment Starting...")
    print("="*50)
    
    # Reset database completely on first run
    run_command("python reset_database.py", "Reset database")
    
    # Run migrations
    run_command("python manage.py migrate --noinput", "Database migrations")
    
    # Create superuser
    run_command("python create_superuser.py", "Superuser creation")
    
    # Collect static files
    run_command("python manage.py collectstatic --noinput", "Static files collection")
    
    print("\n" + "="*50)
    print("✅ Startup completed! Starting Gunicorn...")
    print("="*50 + "\n")
    
    # Start Gunicorn
    port = os.environ.get('PORT', '8080')
    os.execvp('gunicorn', [
        'gunicorn',
        'packaxis_app.wsgi:application',
        '--bind', f'0.0.0.0:{port}',
        '--workers', '4',
        '--timeout', '120',
        '--access-logfile', '-',
        '--error-logfile', '-',
        '--log-level', 'info'
    ])

if __name__ == '__main__':
    main()
