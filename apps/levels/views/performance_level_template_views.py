from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import redirect, render

from ..forms import PerformanceLevelFilterForm, PerformanceLevelTemplateCreateForm
from ..models import PerformanceLevelTemplate
from ..services import create_performance_level_service


def performance_level_create_view(request):
    """
    Vista exclusiva para la creación de niveles de desempeño.
    """

    form = PerformanceLevelTemplateCreateForm(request.POST or None)

    if request.method == 'POST':

        if form.is_valid():
            try:
                # Se envía el formulario + el usuario autenticado
                create_performance_level_service(form, request.user)

                messages.success(request, "Nivel de desempeño creado exitosamente.")
                return redirect('users:dashboard')

            except Exception as e:
                form.add_error(None, f"Error al procesar la solicitud: {str(e)}")

        else:
            messages.error(request, "Error en los datos suministrados. Verifique el formulario.")

    return render(request, 'levels/create_performance_level.html', {
        'form': form,
        'title': 'Registrar Nuevo Nivel de Desempeño'
    })

@login_required(login_url="/users/login/")
def levels_view(request):

    if request.method == "POST":
        form = PerformanceLevelTemplateCreateForm(request.POST)

        if form.is_valid():
            performance = form.save(commit=False)
            performance.user = request.user
            performance.save()
            messages.success(request, "Plantilla guardada correctamente.")
            return redirect("levels:levels")

        messages.error(request, "Revise los datos del formulario e intente de nuevo.")
    else:
        form = PerformanceLevelTemplateCreateForm()

    performance_levels = (
        PerformanceLevelTemplate.objects.filter(
            user=request.user,
            deleted_at__isnull=True,
        )
    )

    filter_form = PerformanceLevelFilterForm(request.GET or None)

    if filter_form.is_valid():
        area = filter_form.cleaned_data.get("area")
        grade = filter_form.cleaned_data.get("grade")
        subject = filter_form.cleaned_data.get("subject")
        academic_period = filter_form.cleaned_data.get("academic_period")
        search = filter_form.cleaned_data.get("search")

        if area:
            performance_levels = performance_levels.filter(area=area)

        if grade:
            performance_levels = performance_levels.filter(grade=grade)

        if subject:
            performance_levels = performance_levels.filter(subject=subject)

        if academic_period:
            performance_levels = performance_levels.filter(academic_period=academic_period)

        if search:
            performance_levels = performance_levels.filter(
                Q(level_title__icontains=search)
                | Q(level_description__icontains=search)
                | Q(competency__icontains=search)
                | Q(statement__icontains=search)
            )

    performance_levels = performance_levels.prefetch_related("generated_levels").order_by("-created_at")

    for performance in performance_levels:
        try:
            gen = performance.generated_levels
            performance.has_generated_levels = gen.deleted_at is None
        except ObjectDoesNotExist:
            performance.has_generated_levels = False

    return render(
        request,
        "pages/levels.html",
        {
            "form": form,
            "filter_form": filter_form,
            "performance_levels": performance_levels,
        },
    )