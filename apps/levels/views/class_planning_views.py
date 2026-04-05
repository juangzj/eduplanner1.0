from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..models import ClassPlanning


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
		.prefetch_related("generated_classes")
		.order_by("-created_at")
	)

	return render(
		request,
		"pages/class_plans.html",
		{"class_plannings": class_plannings},
	)
