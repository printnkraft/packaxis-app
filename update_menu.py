# Run this in Django shell on PythonAnywhere
# python manage.py shell
# Then paste this code:

from core.models import MenuItem

# Update the Products menu item to point to the products page instead of having children
products_menu = MenuItem.objects.filter(title='Products').first()
if products_menu:
    products_menu.url = '/products/'
    products_menu.save()
    print(f"Updated Products menu item to point to /products/")
else:
    print("Products menu item not found")

# You can also delete the child menu items if you want a clean Products page link
# Uncomment the lines below to remove the dropdown:
# if products_menu:
#     products_menu.children.all().delete()
#     print("Deleted product child menu items")
