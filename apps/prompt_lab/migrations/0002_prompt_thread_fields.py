from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("prompt_lab", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="prompt",
            name="is_ai_generated",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="prompt",
            name="parent_prompt",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="refinement_attempts",
                to="prompt_lab.prompt",
            ),
        ),
        migrations.AddField(
            model_name="prompt",
            name="refinement_number",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="prompt",
            name="root_prompt",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="thread_prompts",
                to="prompt_lab.prompt",
            ),
        ),
    ]
