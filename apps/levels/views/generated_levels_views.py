import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView
from django.views.decorators.cache import never_cache

from ..forms import GeneratedLevelsCreateForm, GeneratedLevelsUpdateForm
from ..models import GeneratedLevels
from ..services.generated_levels_services import (
    GeneratedLevelsCreateService,
    GeneratedLevelsUpdateService,
)


logger = logging.getLogger(__name__)


@method_decorator(never_cache, name="dispatch")
class GeneratedLevelsCreateView(LoginRequiredMixin, CreateView):
    form_class = GeneratedLevelsCreateForm
    template_name = "levels/generated_levels_create_page.html"
    success_url = reverse_lazy("levels:levels")
    login_url = "/users/login/"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["selected_template_id"] = self.request.GET.get("template") or self.request.POST.get("performance_template")
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        template_id = self.request.GET.get("template")
        if template_id:
            initial["performance_template"] = template_id
        return initial

    def form_valid(self, form):
        try:
            self.object = GeneratedLevelsCreateService.create_generated_levels_service(
                form=form,
                user=self.request.user,
            )
        except Exception:
            logger.exception("Error al generar los niveles (usuario %s)", self.request.user.pk)
            form.add_error(None, "No fue posible generar los niveles con IA. Intente de nuevo.")
            messages.error(self.request, "Ocurrió un error al generar niveles con IA.")
            return self.form_invalid(form)

        messages.success(self.request, "Los niveles fueron generados y guardados correctamente.")
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, "Revise los datos del formulario e intente de nuevo.")
        return super().form_invalid(form)


@method_decorator(never_cache, name="dispatch")
class GeneratedLevelsUpdateView(LoginRequiredMixin, UpdateView):
    model = GeneratedLevels
    form_class = GeneratedLevelsUpdateForm
    template_name = "levels/generated_levels_edit_page.html"
    success_url = reverse_lazy("levels:levels")
    login_url = "/users/login/"

    def get_queryset(self):
        return GeneratedLevels.objects.filter(
            performance_template__user=self.request.user,
            performance_template__deleted_at__isnull=True,
            deleted_at__isnull=True,
        ).select_related("performance_template")

    def form_valid(self, form):
        try:
            self.object = GeneratedLevelsUpdateService.update_generated_levels_service(
                form=form,
                generated_levels=self.get_object(),
                user=self.request.user,
            )
        except Exception:
            logger.exception("Error al actualizar los niveles %s", self.kwargs.get("pk"))
            form.add_error(None, "No fue posible actualizar los niveles. Intente de nuevo.")
            messages.error(self.request, "Ocurrió un error al editar los niveles.")
            return self.form_invalid(form)

        messages.success(self.request, "Los niveles fueron actualizados correctamente.")
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, "Revise los datos del formulario e intente de nuevo.")
        return super().form_invalid(form)

