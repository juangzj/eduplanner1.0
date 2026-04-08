from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404

from ..ai.prompt_builder import build_prompt, evaluate_prompt, generate_quality_prompt
from ..models import Prompt


def create_prompt_service(user, data):
    full_prompt = build_prompt(data)
    score, feedback = evaluate_prompt(full_prompt, data=data)

    feedback_text = "\n".join(f"- {item}" for item in feedback) if feedback else ""

    return Prompt.objects.create(
        teacher=user,
        parent_prompt=None,
        root_prompt=None,
        refinement_number=0,
        is_ai_generated=False,
        purpose=data.get("purpose", "").strip(),
        role=data.get("role", "").strip(),
        context=data.get("context", "").strip(),
        task=data.get("task", "").strip(),
        process=data.get("process", "").strip() or None,
        format=data.get("format", "").strip(),
        constraints=data.get("constraints", "").strip() or None,
        full_prompt=full_prompt,
        score=score,
        feedback=feedback_text or None,
    )


def get_prompt_by_id(prompt_id):
    return get_object_or_404(Prompt, id=prompt_id)


def get_prompts_by_teacher(user):
    return Prompt.objects.filter(teacher=user, parent_prompt__isnull=True).order_by("-created_at")


def get_root_prompt(prompt):
    return prompt.root_prompt or prompt


def get_thread_prompts(prompt):
    root = get_root_prompt(prompt)
    return Prompt.objects.filter(Q(id=root.id) | Q(root_prompt=root)).order_by("created_at", "id")


def get_latest_thread_prompt(prompt):
    return get_thread_prompts(prompt).last()


def get_refinement_limits():
    max_refinements = max(0, int(getattr(settings, "PROMPT_LAB_MAX_REFINEMENTS", 5)))
    generation_min_refinements = max(
        0,
        int(getattr(settings, "PROMPT_LAB_GENERATION_MIN_REFINEMENTS", 3)),
    )
    return max_refinements, generation_min_refinements


def create_refinement_service(user, source_prompt, data):
    root = get_root_prompt(source_prompt)
    latest = get_latest_thread_prompt(source_prompt)
    max_refinements, _ = get_refinement_limits()

    if latest.refinement_number >= max_refinements:
        raise ValueError("Se alcanzo el numero maximo de refinamientos permitidos.")

    full_prompt = build_prompt(data)
    score, feedback = evaluate_prompt(full_prompt, data=data)
    feedback_text = "\n".join(f"- {item}" for item in feedback) if feedback else ""

    return Prompt.objects.create(
        teacher=user,
        parent_prompt=latest,
        root_prompt=root,
        refinement_number=latest.refinement_number + 1,
        is_ai_generated=False,
        purpose=data.get("purpose", "").strip(),
        role=data.get("role", "").strip(),
        context=data.get("context", "").strip(),
        task=data.get("task", "").strip(),
        process=data.get("process", "").strip() or None,
        format=data.get("format", "").strip(),
        constraints=data.get("constraints", "").strip() or None,
        full_prompt=full_prompt,
        score=score,
        feedback=feedback_text or None,
    )


def generate_quality_prompt_service(user, source_prompt):
    root = get_root_prompt(source_prompt)
    latest = get_latest_thread_prompt(source_prompt)
    _, generation_min_refinements = get_refinement_limits()

    if latest.refinement_number < generation_min_refinements:
        raise ValueError("Aun no se alcanza el minimo de refinamientos para generar prompt final.")

    thread_feedback = [item.feedback for item in get_thread_prompts(source_prompt) if item.feedback]
    feedback_items = []
    for block in thread_feedback:
        feedback_items.extend([line.strip().lstrip("- ") for line in block.splitlines() if line.strip()])

    latest_data = {
        "purpose": latest.purpose,
        "role": latest.role,
        "context": latest.context,
        "task": latest.task,
        "process": latest.process or "",
        "format": latest.format,
        "constraints": latest.constraints or "",
    }

    improved_data = generate_quality_prompt(latest_data, feedback_history=feedback_items)
    full_prompt = improved_data.get("full_prompt") or build_prompt(improved_data)
    score, feedback = evaluate_prompt(full_prompt, data=improved_data)
    feedback_text = "\n".join(f"- {item}" for item in feedback) if feedback else ""

    return Prompt.objects.create(
        teacher=user,
        parent_prompt=latest,
        root_prompt=root,
        refinement_number=latest.refinement_number + 1,
        is_ai_generated=True,
        purpose=improved_data.get("purpose", "").strip(),
        role=improved_data.get("role", "").strip(),
        context=improved_data.get("context", "").strip(),
        task=improved_data.get("task", "").strip(),
        process=improved_data.get("process", "").strip() or None,
        format=improved_data.get("format", "").strip(),
        constraints=improved_data.get("constraints", "").strip() or None,
        full_prompt=full_prompt,
        score=score,
        feedback=feedback_text or None,
    )
