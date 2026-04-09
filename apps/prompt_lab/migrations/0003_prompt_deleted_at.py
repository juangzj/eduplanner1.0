from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("prompt_lab", "0002_prompt_thread_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="prompt",
            name="deleted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
