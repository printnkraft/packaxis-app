# Generated manually on 2025-12-14

from django.db import migrations


def create_industries_menu(apps, schema_editor):
    MenuItem = apps.get_model('core', 'MenuItem')
    
    # Create Industries parent menu item
    industries_parent = MenuItem.objects.create(
        title="Industries",
        url="",  # Leave blank for dropdown parent
        parent=None,
        order=3,
        is_active=True,
        open_in_new_tab=False
    )
    
    # Update other menu items order
    MenuItem.objects.filter(title="Services").update(order=4)
    MenuItem.objects.filter(title="About").update(order=5)
    MenuItem.objects.filter(title="Contact").update(order=6)
    
    # Create child menu items
    children_data = [
        ("Restaurant & Takeout", "/restaurant-paper-bags/", 1),
        ("Retail Stores", "/retail-paper-bags/", 2),
        ("Boutique & Fashion", "/boutique-packaging/", 3),
        ("Grocery & Supermarket", "/grocery-paper-bags/", 4),
        ("Bakery & Cafe", "/bakery-paper-bags/", 5),
    ]
    
    for title, url, order in children_data:
        MenuItem.objects.create(
            title=title,
            url=url,
            parent=industries_parent,
            order=order,
            is_active=True,
            open_in_new_tab=False
        )


def reverse_industries_menu(apps, schema_editor):
    MenuItem = apps.get_model('core', 'MenuItem')
    
    # Delete Industries menu and its children
    MenuItem.objects.filter(title="Industries").delete()
    
    # Restore original order
    MenuItem.objects.filter(title="Services").update(order=3)
    MenuItem.objects.filter(title="About").update(order=4)
    MenuItem.objects.filter(title="Contact").update(order=5)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_remove_productold'),
    ]

    operations = [
        migrations.RunPython(create_industries_menu, reverse_industries_menu),
    ]
