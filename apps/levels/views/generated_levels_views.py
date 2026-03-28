from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from ..forms import GeneratedLevelsCreateForm
from ..services.generated_levels_services import GeneratedLevelsCreateService


class GeneratedLevelsCreateView(LoginRequiredMixin, CreateView):
    form_class = GeneratedLevelsCreateForm
    template_name = "levels/generated_levels_create_page.html"
    success_url = reverse_lazy("levels:levels")
    login_url = "/users/login/"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
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
        except Exception as exc:
            form.add_error(None, f"No fue posible generar los niveles con IA: {exc}")
            messages.error(self.request, "Ocurrio un error al generar niveles con IA.")
            return self.form_invalid(form)

        messages.success(self.request, "Los niveles fueron generados y guardados correctamente.")
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, "Revise los datos del formulario e intente de nuevo.")
        return super().form_invalid(form)

