from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from ..services import create_prompt_service, get_prompt_by_id, get_prompts_by_teacher

REQUIRED_FIELDS = ["purpose", "role", "context", "task", "format"]


@login_required(login_url="/users/login/")
def prompt_create_view(request):
    if request.method == "POST":
        payload = {
            "purpose": request.POST.get("purpose", ""),
            "role": request.POST.get("role", ""),
            "context": request.POST.get("context", ""),
            "task": request.POST.get("task", ""),
            "process": request.POST.get("process", ""),
            "format": request.POST.get("format", ""),
            "constraints": request.POST.get("constraints", ""),
        }

        missing_fields = [
            field for field in REQUIRED_FIELDS if not payload[field].strip()
        ]
        if missing_fields:
            messages.error(
                request,
                "Completa todos los campos obligatorios antes de generar el prompt.",
            )
            return render(
                request,
                "prompt_lab/prompt_create_page.html",
                {"form_data": payload, "missing_fields": missing_fields},
            )

        prompt = create_prompt_service(request.user, payload)
        messages.success(request, "Prompt generado y guardado correctamente.")
        return redirect("prompt_lab:prompt-detail", prompt_id=prompt.id)

    return render(request, "prompt_lab/prompt_create_page.html")


@login_required(login_url="/users/login/")
def prompt_detail_view(request, prompt_id):
    prompt = get_prompt_by_id(prompt_id)

    if prompt.teacher_id != request.user.id:
        messages.error(request, "No tienes permiso para ver este prompt.")
        return redirect("prompt_lab:prompt-create")

    feedback_items = []
    if prompt.feedback:
        feedback_items = [
            line.lstrip("- ").strip() for line in prompt.feedback.splitlines() if line.strip()
        ]

    return render(
        request,
        "prompt_lab/prompt_detail_page.html",
        {
            "prompt": prompt,
            "feedback_items": feedback_items,
        },
    )


@login_required(login_url="/users/login/")
def prompt_list_view(request):
    prompts = get_prompts_by_teacher(request.user)

    return render(
        request,
        "prompt_lab/prompt_list_page.html",
        {
            "prompts": prompts,
        },
    )
