import uuid
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase, override_settings
from django.urls import reverse

from .views.class_planning_views import ClassPlanningDeleteView
from .views.generated_class_plan_views import GeneratedClassPlanDeleteView

INTERNAL_ERROR = "User does not own this record."


@override_settings(ALLOWED_HOSTS=["*"])
class DeleteErrorMessageTests(TestCase):
    """
    Si falla el borrado, el docente ve un mensaje en español y el detalle
    del error interno solo queda en el log.
    """

    def setUp(self):
        user = get_user_model().objects.create_user("docente@gmail.com", "Clave#2026", first_name="Ana", last_name="Ruiz")
        self.client.force_login(user)

    def _assert_hidden_error(self, view_class, service_path, url_name, expected_message):
        record_id = uuid.uuid4()
        with patch.object(view_class, "get_object", return_value=SimpleNamespace(pk=record_id)), \
                patch(service_path, side_effect=PermissionError(INTERNAL_ERROR)), \
                self.assertLogs(view_class.__module__, level="ERROR") as logs:
            response = self.client.post(reverse(url_name, args=[record_id]))

        shown = [str(message) for message in get_messages(response.wsgi_request)]
        self.assertEqual(shown, [expected_message])
        self.assertIn(INTERNAL_ERROR, "\n".join(logs.output))

    def test_class_planning_delete_hides_internal_error(self):
        self._assert_hidden_error(
            ClassPlanningDeleteView,
            "apps.levels.views.class_planning_views.ClassPlanningDeleteService.soft_delete_class_planning_service",
            "levels:class-planning-delete",
            "No fue posible eliminar la planeación de clase. Intente de nuevo.",
        )

    def test_generated_class_plan_delete_hides_internal_error(self):
        self._assert_hidden_error(
            GeneratedClassPlanDeleteView,
            "apps.levels.views.generated_class_plan_views.GeneratedClassPlanDeleteService.soft_delete_generated_class_plan_service",
            "levels:generated-class-plan-delete",
            "No fue posible eliminar la clase generada. Intente de nuevo.",
        )
