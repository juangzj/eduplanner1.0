from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from ..services import (
    create_prompt_service,
    create_refinement_service,
    generate_quality_prompt_service,
    get_latest_thread_prompt,
    get_prompt_by_id,
    get_prompts_by_teacher,
    get_refinement_limits,
    get_root_prompt,
    get_thread_prompts,
    soft_delete_prompt_service,
)

REQUIRED_FIELDS = ["purpose", "role", "context", "task", "format"]

PROMPT_MARKDOWN_SECTIONS = [
    ("purpose", "Proposito"),
    ("role", "Rol"),
    ("context", "Contexto"),
    ("task", "Tarea"),
    ("process", "Proceso"),
    ("format", "Formato"),
    ("constraints", "Restricciones"),
]

FEEDBACK_SECTION_TITLES = {
    "status": "Estado de calidad",
    "general": "Retroalimentacion general",
    "purpose": "Proposito",
    "role": "Rol",
    "context": "Contexto",
    "task": "Tarea",
    "process": "Proceso",
    "format": "Formato",
    "constraints": "Restricciones",
    "other": "Recomendaciones adicionales",
}

FEEDBACK_KEY_BY_PREFIX = {
    "Retroalimentacion general": "general",
    "Proposito": "purpose",
    "Rol": "role",
    "Contexto": "context",
    "Tarea": "task",
    "Proceso": "process",
    "Formato": "format",
    "Restricciones": "constraints",
}


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

    root_prompt = get_root_prompt(prompt)
    latest_prompt = get_latest_thread_prompt(prompt)

    if request.method == "POST":
        action = request.POST.get("action", "").strip()

        if action == "refine":
            payload = _build_payload_from_request(request)
            missing_fields = [field for field in REQUIRED_FIELDS if not payload[field].strip()]
            if missing_fields:
                messages.error(request, "Completa todos los campos obligatorios para continuar refinando.")
                return _render_prompt_detail(
                    request,
                    root_prompt,
                    form_data=payload,
                    missing_fields=missing_fields,
                    show_refine_form=True,
                )

            try:
                refined_prompt = create_refinement_service(request.user, latest_prompt, payload)
            except ValueError as exc:
                messages.error(request, str(exc))
                return redirect("prompt_lab:prompt-detail", prompt_id=latest_prompt.id)

            messages.success(request, "Refinamiento guardado y evaluado con IA correctamente.")
            return redirect("prompt_lab:prompt-detail", prompt_id=refined_prompt.id)

        if action == "generate-quality":
            try:
                generated_prompt = generate_quality_prompt_service(request.user, latest_prompt)
            except ValueError as exc:
                messages.error(request, str(exc))
                return redirect("prompt_lab:prompt-detail", prompt_id=latest_prompt.id)

            messages.success(request, "Prompt final generado con base en el ultimo refinamiento.")
            return redirect("prompt_lab:prompt-detail", prompt_id=generated_prompt.id)

    show_refine_form = request.GET.get("refine") == "1"
    return _render_prompt_detail(request, root_prompt, show_refine_form=show_refine_form)


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


@login_required(login_url="/users/login/")
def prompt_delete_view(request, prompt_id):
    if request.method != "POST":
        messages.error(request, "Metodo no permitido para eliminar prompts.")
        return redirect("prompt_lab:prompt-list")

    prompt = get_prompt_by_id(prompt_id)

    try:
        deleted = soft_delete_prompt_service(request.user, prompt)
    except PermissionError:
        messages.error(request, "No tienes permiso para eliminar este prompt.")
        return redirect("prompt_lab:prompt-list")

    if deleted:
        messages.success(request, "Prompt eliminado correctamente.")
    else:
        messages.info(request, "El prompt ya habia sido eliminado previamente.")

    return redirect("prompt_lab:prompt-list")


def _build_payload_from_request(request):
    return {
        "purpose": request.POST.get("purpose", ""),
        "role": request.POST.get("role", ""),
        "context": request.POST.get("context", ""),
        "task": request.POST.get("task", ""),
        "process": request.POST.get("process", ""),
        "format": request.POST.get("format", ""),
        "constraints": request.POST.get("constraints", ""),
    }


def _feedback_to_items(feedback_text):
    if not feedback_text:
        return []

    return [line.lstrip("- ").strip() for line in feedback_text.splitlines() if line.strip()]


def _prompt_to_markdown(prompt_obj):
    blocks = []

    for field_name, label in PROMPT_MARKDOWN_SECTIONS:
        value = getattr(prompt_obj, field_name, "")
        value_text = str(value).strip() if value else ""
        blocks.append(f"## {label}\n\n{value_text or '_No especificado._'}")

    return "\n\n".join(blocks)


def _prompt_to_sections(prompt_obj):
    sections = []

    for field_name, label in PROMPT_MARKDOWN_SECTIONS:
        value = getattr(prompt_obj, field_name, "")
        text = str(value).strip() if value else ""
        sections.append(
            {
                "field": field_name,
                "label": label,
                "value": text or "No especificado.",
            }
        )

    return sections


def _feedback_to_blocks(feedback_items):
    if not feedback_items:
        return []

    grouped = {key: [] for key in FEEDBACK_SECTION_TITLES.keys()}

    for item in feedback_items:
        normalized = item.strip()

        if normalized.startswith("El prompt ya tiene calidad") or normalized.startswith("El prompt aun no alcanza"):
            grouped["status"].append(normalized)
            continue

        matched = False
        for prefix, key in FEEDBACK_KEY_BY_PREFIX.items():
            prefix_with_colon = f"{prefix}:"
            if normalized.startswith(prefix_with_colon):
                grouped[key].append(normalized[len(prefix_with_colon):].strip())
                matched = True
                break

        if not matched:
            grouped["other"].append(normalized)

    ordered_keys = [
        "status",
        "general",
        "purpose",
        "role",
        "context",
        "task",
        "process",
        "format",
        "constraints",
        "other",
    ]

    blocks = []
    for key in ordered_keys:
        entries = grouped.get(key, [])
        if not entries:
            continue
        blocks.append(
            {
                "key": key,
                "title": FEEDBACK_SECTION_TITLES[key],
                "entries": entries,
            }
        )

    return blocks


def _render_prompt_detail(request, root_prompt, form_data=None, missing_fields=None, show_refine_form=False):
    thread_prompts = list(get_thread_prompts(root_prompt))
    latest_prompt = thread_prompts[-1]
    max_refinements, generation_min_refinements = get_refinement_limits()

    can_refine = latest_prompt.refinement_number < max_refinements
    can_generate_quality = latest_prompt.refinement_number >= generation_min_refinements

    if form_data is None:
        form_data = {
            "purpose": latest_prompt.purpose,
            "role": latest_prompt.role,
            "context": latest_prompt.context,
            "task": latest_prompt.task,
            "process": latest_prompt.process or "",
            "format": latest_prompt.format,
            "constraints": latest_prompt.constraints or "",
        }

    thread_cards = []
    for item in thread_prompts:
        if item.refinement_number == 0:
            card_title = "Intento inicial"
        elif item.is_ai_generated:
            card_title = "Prompt final generado con IA"
        else:
            card_title = f"Refinamiento #{item.refinement_number}"

        thread_cards.append(
            {
                "prompt": item,
                "card_title": card_title,
                "prompt_markdown": _prompt_to_markdown(item),
                "prompt_sections": _prompt_to_sections(item),
                "feedback_items": _feedback_to_items(item.feedback),
                "feedback_blocks": _feedback_to_blocks(_feedback_to_items(item.feedback)),
            }
        )

    context = {
        "prompt": latest_prompt,
        "thread_cards": thread_cards,
        "show_refine_form": show_refine_form and can_refine,
        "form_data": form_data,
        "missing_fields": missing_fields or [],
        "can_refine": can_refine,
        "can_generate_quality": can_generate_quality,
        "max_refinements": max_refinements,
        "generation_min_refinements": generation_min_refinements,
        "current_refinement_number": latest_prompt.refinement_number,
        "remaining_refinements": max(0, max_refinements - latest_prompt.refinement_number),
    }
    return render(request, "prompt_lab/prompt_detail_page.html", context)
