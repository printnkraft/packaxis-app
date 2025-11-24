# Run this in Django shell on PythonAnywhere
# python manage.py shell
# Then paste this code:

from core.models import Service

# Update Fast Turnaround service to Quality Production
service = Service.objects.filter(title='Fast Turnaround').first()
if service:
    service.title = 'Quality Production'
    service.description = 'Meticulous attention to detail and quality control. Every order is produced to the highest standards.'
    service.icon = 'fas fa-industry'
    service.save()
    print("Updated 'Fast Turnaround' to 'Quality Production'")
else:
    print("Service not found")
