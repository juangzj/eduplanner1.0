from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.cache import never_cache


@never_cache
@login_required(login_url="/users/login/")
def excel_upload_view(request):
    """
    Vista para la carga de plantillas desde un archivo Excel.
    """

    return render(request, "levels/excel_upload_page.html")
