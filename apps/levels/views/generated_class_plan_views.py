import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import UpdateView

from ..forms import GeneratedClassPlanUpdateForm
from ..models import GeneratedClassPlan
from ..services.generated_class_plan_services import (
    GeneratedClassPlanDeleteService,
    GeneratedClassPlanUpdateService,
)


logger = logging.getLogger(__name__)


@method_decorator(never_cache, name="dispatch")
class GeneratedClassPlanUpdateView(LoginRequiredMixin, UpdateView):
    model = GeneratedClassPlan
    form_class = GeneratedClassPlanUpdateForm
    template_name = "levels/generated_class_plan_edit_page.html"
    success_url = reverse_lazy("levels:class-plans")
    login_url = "/users/login/"

    def get_queryset(self):
        return GeneratedClassPlan.objects.filter(
            class_planning__user=self.request.user,
            class_planning__deleted_at__isnull=True,
            deleted_at__isnull=True,
        ).select_related("class_planning", "class_planning__performance_template")

    def form_valid(self, form):
        try:
            self.object = GeneratedClassPlanUpdateService.update_generated_class_plan_service(
                form=form,
                generated_class_plan=self.get_object(),
                user=self.request.user,
            )
        except Exception:
            logger.exception("Error al actualizar la clase generada %s", self.kwargs.get("pk"))
            form.add_error(None, "No fue posible actualizar la clase generada. Intente de nuevo.")
            messages.error(self.request, "Ocurrió un error al editar el contenido generado.")
            return self.form_invalid(form)

        messages.success(self.request, "El contenido generado fue actualizado correctamente.")
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, "Revise los datos del formulario e intente de nuevo.")
        return super().form_invalid(form)


@method_decorator(never_cache, name="dispatch")
class GeneratedClassPlanDeleteView(LoginRequiredMixin, SingleObjectMixin, View):
    model = GeneratedClassPlan
    success_url = reverse_lazy("levels:class-plans")
    login_url = "/users/login/"
    http_method_names = ["post"]

    def get_success_url(self):
        return self.success_url

    def get_queryset(self):
        return GeneratedClassPlan.objects.filter(
            class_planning__user=self.request.user,
            class_planning__deleted_at__isnull=True,
            deleted_at__isnull=True,
        ).select_related("class_planning")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        try:
            was_deleted = GeneratedClassPlanDeleteService.soft_delete_generated_class_plan_service(
                generated_class_plan=self.object,
                user=request.user,
            )
        except Exception:
            logger.exception("Error al eliminar la clase generada %s", self.object.pk)
            messages.error(request, "No fue posible eliminar la clase generada. Intente de nuevo.")
            return HttpResponseRedirect(self.get_success_url())

        if was_deleted:
            messages.success(request, "La clase generada fue eliminada correctamente.")
        else:
            messages.error(request, "No se pudo eliminar la clase generada seleccionada.")

        return HttpResponseRedirect(self.get_success_url())