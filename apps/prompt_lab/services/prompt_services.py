from django.shortcuts import get_object_or_404

from ..ai.prompt_builder import build_prompt, evaluate_prompt
from ..models import Prompt


def create_prompt_service(user, data):
    full_prompt = build_prompt(data)
    score, feedback = evaluate_prompt(full_prompt, data=data)

    feedback_text = "\n".join(f"- {item}" for item in feedback) if feedback else ""

    return Prompt.objects.create(
        teacher=user,
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
    return Prompt.objects.filter(teacher=user).order_by("-created_at")
