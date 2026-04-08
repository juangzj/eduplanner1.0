from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Prompt",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("purpose", models.TextField()),
                ("role", models.TextField()),
                ("context", models.TextField()),
                ("task", models.TextField()),
                ("process", models.TextField(blank=True, null=True)),
                ("format", models.TextField()),
                ("constraints", models.TextField(blank=True, null=True)),
                ("full_prompt", models.TextField()),
                ("score", models.FloatField(blank=True, null=True)),
                ("feedback", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "teacher",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="prompts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
