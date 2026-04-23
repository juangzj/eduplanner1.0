from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import CreateView
from django.views.generic.detail import SingleObjectMixin
from django.views.decorators.cache import never_cache

from ..forms import ClassPlanningCreateForm
from ..models import ClassPlanning, GeneratedClassPlan, PerformanceLevelTemplate
from ..services.class_planning_services import ClassPlanningCreateService, ClassPlanningDeleteService


@never_cache
@login_required(login_url="/users/login/")
def class_plans_list_view(request):
	class_plannings = (
		ClassPlanning.objects.filter(
			user=request.user,
			deleted_at__isnull=True,
		)
		.select_related(
			"performance_template",
			"generated_levels",
			"assessment_rubric",
		)
		.prefetch_related(
			Prefetch(
				"generated_classes",
				queryset=GeneratedClassPlan.objects.filter(deleted_at__isnull=True).order_by("-created_at"),
			),
		)
		.order_by("-created_at")
	)

	return render(
		request,
		"pages/class_plans.html",
		{"class_plannings": class_plannings},
	)


@method_decorator(never_cache, name="dispatch")
class ClassPlanningCreateView(LoginRequiredMixin, CreateView):
	form_class = ClassPlanningCreateForm
	template_name = "levels/class_planning_create_page.html"
	success_url = reverse_lazy("levels:class-plans")
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

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		template_id = self.request.GET.get("template")
		if template_id:
			try:
				context["selected_template"] = PerformanceLevelTemplate.objects.select_related(
					"generated_levels",
					"generated_levels__assessment_rubric",
				).get(
					id=template_id,
					user=self.request.user,
					deleted_at__isnull=True,
					generated_levels__deleted_at__isnull=True,
					generated_levels__assessment_rubric__deleted_at__isnull=True,
				)
			except Exception:
				context["selected_template"] = None
		else:
			context["selected_template"] = None
		return context

	def form_valid(self, form):
		try:
			self.object = ClassPlanningCreateService.create_class_planning_service(
				form=form,
				user=self.request.user,
			)
		except Exception as exc:
			form.add_error(None, f"No fue posible generar la planeación con IA: {exc}")
			messages.error(self.request, "Ocurrió un error al generar la planeación de clase.")
			return self.form_invalid(form)

		messages.success(self.request, "La planeación de clase fue generada y guardada correctamente.")
		return HttpResponseRedirect(self.get_success_url())

	def form_invalid(self, form):
		messages.error(self.request, "Revise los datos del formulario e intente de nuevo.")
		return super().form_invalid(form)


@method_decorator(never_cache, name="dispatch")
class ClassPlanningDeleteView(LoginRequiredMixin, SingleObjectMixin, View):
	model = ClassPlanning
	success_url = reverse_lazy("levels:class-plans")
	login_url = "/users/login/"
	http_method_names = ["post"]

	def get_success_url(self):
		return self.success_url

	def get_queryset(self):
		return ClassPlanning.objects.filter(
			user=self.request.user,
			deleted_at__isnull=True,
		)

	def post(self, request, *args, **kwargs):
		self.object = self.get_object()

		try:
			was_deleted = ClassPlanningDeleteService.soft_delete_class_planning_service(
				class_planning=self.object,
				user=request.user,
			)
		except Exception as exc:
			messages.error(request, f"No fue posible eliminar la planeación de clase: {exc}")
			return HttpResponseRedirect(self.get_success_url())

		if was_deleted:
			messages.success(request, "La planeación de clase fue eliminada correctamente.")
		else:
			messages.error(request, "No se pudo eliminar la planeación de clase seleccionada.")

		return HttpResponseRedirect(self.get_success_url())
