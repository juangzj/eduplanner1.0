class GeneratedLevelsCreateService:

    @staticmethod
    def create_generated_levels_service(form, user=None):
        """
        Crea los niveles generados a partir del formulario.
        """
        generated_levels = form.save(commit=False)
        generated_levels.save()

        template = generated_levels.performance_template
        template.generated_level_id = str(generated_levels.id)
        template.save(update_fields=["generated_level_id"])

        return generated_levels