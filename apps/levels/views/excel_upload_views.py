from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import urlencode
from django.views.decorators.cache import never_cache

from ..forms import ExcelUploadForm
from ..services import ExcelUploadError, ExcelUploadService


# Clave de sesión con los datos del Excel para precargar la planeación de clase
CLASS_PLANNING_EXCEL_SESSION_KEY = "class_planning_excel_data"


@never_cache
@login_required(login_url="/users/login/")
def excel_upload_view(request):
    """
    Vista para la carga de plantillas desde un archivo Excel.
    """

    form = ExcelUploadForm(request.POST or None, request.FILES or None)

    if request.method == "POST":

        if form.is_valid():
            try:
                ExcelUploadService.create_performance_level_from_excel_service(
                    excel_file=form.cleaned_data["excel_file"],
                    user=request.user,
                )

                messages.success(request, "Plantilla creada correctamente desde el Excel.")
                return redirect("levels:levels")

            except ExcelUploadError as e:
                form.add_error("excel_file", str(e))

        messages.error(request, "No se pudo procesar el archivo. Revise los errores e intente de nuevo.")

    return render(request, "levels/excel_upload_page.html", {
        "form": form,
    })


@never_cache
@login_required(login_url="/users/login/")
def class_planning_excel_upload_view(request):
    """
    Vista para precargar el formulario de planeación de clase desde un archivo Excel.
    Los datos extraídos se guardan en sesión y el docente los revisa antes de generar con IA.
    """

    template_id = request.GET.get("template") or request.POST.get("template") or ""
    form = ExcelUploadForm(request.POST or None, request.FILES or None)

    if request.method == "POST":

        if form.is_valid():
            try:
                data = ExcelUploadService.extract_class_planning_data_from_excel_service(
                    excel_file=form.cleaned_data["excel_file"],
                )

                request.session[CLASS_PLANNING_EXCEL_SESSION_KEY] = data

                messages.success(request, "Datos cargados desde el Excel. Revíselos y genere la planeación con IA.")
                create_url = reverse("levels:class-planning-create")
                if template_id:
                    create_url = f"{create_url}?{urlencode({'template': template_id})}"
                return redirect(create_url)

            except ExcelUploadError as e:
                form.add_error("excel_file", str(e))

        messages.error(request, "No se pudo procesar el archivo. Revise los errores e intente de nuevo.")

    return render(request, "levels/class_planning_excel_upload_page.html", {
        "form": form,
        "template_id": template_id,
    })
