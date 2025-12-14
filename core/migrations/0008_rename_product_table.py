# Manual migration to rename Product table to ProductOld
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_make_description_optional'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Product',
            new_name='ProductOld',
        ),
    ]
