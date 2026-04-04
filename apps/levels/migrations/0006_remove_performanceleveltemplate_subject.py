from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("levels", "0005_assessmentrubric"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="performanceleveltemplate",
            name="subject",
        ),
    ]
