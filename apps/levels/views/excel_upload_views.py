from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache

from ..forms import ExcelUploadForm
from ..services import ExcelUploadError, ExcelUploadService


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
