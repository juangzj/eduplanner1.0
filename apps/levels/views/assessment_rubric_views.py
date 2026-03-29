from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from ..forms import AssessmentRubricCreateForm, AssessmentRubricUpdateForm
from ..models import AssessmentRubric
from ..services.assessment_rubric_services import (
    AssessmentRubricCreateService,
    AssessmentRubricUpdateService,
)


class AssessmentRubricCreateView(LoginRequiredMixin, CreateView):
    form_class = AssessmentRubricCreateForm
    template_name = "levels/assessment_rubric_create_page.html"
    success_url = reverse_lazy("levels:levels")
    login_url = "/users/login/"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        generated_levels_id = self.request.GET.get("generated_levels")
        if generated_levels_id:
            initial["generated_levels"] = generated_levels_id
        return initial

    def form_valid(self, form):
        try:
            self.object = AssessmentRubricCreateService.create_assessment_rubric_service(
                form=form,
                user=self.request.user,
            )
        except Exception as exc:
            form.add_error(None, f"No fue posible generar la rúbrica con IA: {exc}")
            messages.error(self.request, "Ocurrió un error al generar la rúbrica con IA.")
            return self.form_invalid(form)

        messages.success(self.request, "La rúbrica fue generada y guardada correctamente.")
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, "Revise los datos del formulario e intente de nuevo.")
        return super().form_invalid(form)


class AssessmentRubricUpdateView(LoginRequiredMixin, UpdateView):
    model = AssessmentRubric
    form_class = AssessmentRubricUpdateForm
    template_name = "levels/assessment_rubric_edit_page.html"
    success_url = reverse_lazy("levels:levels")
    login_url = "/users/login/"

    def get_queryset(self):
        return AssessmentRubric.objects.filter(
            generated_levels__performance_template__user=self.request.user,
            generated_levels__performance_template__deleted_at__isnull=True,
            generated_levels__deleted_at__isnull=True,
            deleted_at__isnull=True,
        ).select_related("generated_levels", "generated_levels__performance_template")

    def form_valid(self, form):
        try:
            self.object = AssessmentRubricUpdateService.update_assessment_rubric_service(
                form=form,
                assessment_rubric=self.get_object(),
                user=self.request.user,
            )
        except Exception as exc:
            form.add_error(None, f"No fue posible actualizar la rúbrica: {exc}")
            messages.error(self.request, "Ocurrió un error al editar la rúbrica.")
            return self.form_invalid(form)

        messages.success(self.request, "La rúbrica fue actualizada correctamente.")
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, "Revise los datos del formulario e intente de nuevo.")
        return super().form_invalid(form)
