# Manual migration to rename Product table to ProductOld
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_make_description_optional'),
    ]

    operations = [
        # NOTE: In fresh databases, Product doesn't exist yet (it was created and then removed in earlier versions)
        # This migration is a no-op on fresh installations; it only applies to existing databases that have ProductOld
    ]
