import json
import re
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .services import prompt_services

QUALITY_MESSAGE = "El prompt ya tiene calidad para uso docente"

STRONG_DATA = {
    "purpose": "Desarrollar pensamiento critico al comparar dos fuentes historicas sobre la independencia en grado 10.",
    "role": "Actua como docente de Ciencias Sociales de grado 10 con experiencia en didactica de la historia y enfoque en aprendizaje basado en indagacion.",
    "context": "Grado 10, 32 estudiantes de 15 a 16 anos, tema independencia de Colombia, clase de 50 minutos, sin internet, 3 estudiantes con rezago lector, el grupo conoce la linea de tiempo basica.",
    "task": "Genera una secuencia de 3 actividades con objetivo, instrucciones, criterio de logro y evidencia para comparar dos fuentes primarias.",
    "process": "Paso 1: diagnostica errores comunes. Paso 2: propone actividad guiada con ejemplo. Paso 3: cierre metacognitivo con preguntas.",
    "format": "Responde en tabla markdown con 5 columnas: objetivo, actividad, recurso, evaluacion, adaptacion. Maximo 300 palabras.",
    "constraints": "Tono motivador y cercano, lenguaje sencillo para estudiantes, cita fuentes del Ministerio de Educacion, usa ejemplos y preguntas socraticas.",
}

MAX_LEVELS = {
    "persona_rol": 3, "task_intent": 4, "contexto": 4, "output": 4, "audiencia": 3,
    "steps": 3, "referencias": 2, "tonalidad": 2, "tecnicas": 2,
}


def fake_openai(levels):
    """
    Simula OpenAI: devuelve la evaluacion de la rubrica con los niveles indicados
    (los criterios no indicados quedan en su nivel maximo).
    """
    payload = {
        "score": 0,
        "overall_feedback": "Evaluacion simulada.",
        "dimension_scores": {
            key: {"level": levels.get(key, max_level), "max_level": max_level, "weighted_score": 0, "feedback": f"Nota {key}"}
            for key, max_level in MAX_LEVELS.items()
        },
        "recommendations": ["Recomendacion 1", "Recomendacion 2", "Recomendacion 3"],
    }
    response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(payload)))])

    class FakeClient:
        def __init__(self, *args, **kwargs):
            self.chat = SimpleNamespace(completions=SimpleNamespace(create=lambda **kwargs: response))

    return patch("openai.OpenAI", FakeClient)


def feedback_lines(prompt):
    return [line.strip().lstrip("- ") for line in (prompt.feedback or "").splitlines() if line.strip()]


def criteria_points(lines):
    return [float(match.group(1)) for line in lines if (match := re.search(r": ([\d.]+) de \d+ puntos\.", line))]


@override_settings(ALLOWED_HOSTS=["*"], OPENAI_API_KEY="test-key", PROMPT_LAB_GENERATION_MIN_REFINEMENTS=0)
class PromptScoreTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            "docente@gmail.com", "Clave#2026", first_name="Ana", last_name="Ruiz"
        )

    def _teacher_and_ai_prompts(self, data):
        teacher_prompt = prompt_services.create_prompt_service(self.user, data)
        # La IA "mejora" el prompt devolviendo el mismo contenido que escribio el docente
        with patch.object(prompt_services, "generate_quality_prompt", return_value=dict(data)):
            ai_prompt = prompt_services.generate_quality_prompt_service(self.user, teacher_prompt)
        self.assertTrue(ai_prompt.is_ai_generated)
        return teacher_prompt, ai_prompt

    def test_ai_generated_prompt_gets_same_score_as_teacher_with_ai_evaluation(self):
        with fake_openai({"tecnicas": 1}):
            teacher_prompt, ai_prompt = self._teacher_and_ai_prompts(STRONG_DATA)

        self.assertEqual(teacher_prompt.score, 97.5)
        self.assertEqual(ai_prompt.score, teacher_prompt.score)
        self.assertEqual(feedback_lines(ai_prompt), feedback_lines(teacher_prompt))

    @override_settings(OPENAI_API_KEY="")
    def test_ai_generated_prompt_gets_same_score_as_teacher_with_rule_fallback(self):
        teacher_prompt, ai_prompt = self._teacher_and_ai_prompts(STRONG_DATA)

        self.assertEqual(teacher_prompt.score, 92.5)
        self.assertEqual(ai_prompt.score, teacher_prompt.score)
        self.assertEqual(feedback_lines(ai_prompt), feedback_lines(teacher_prompt))

    def test_ai_generated_feedback_has_criteria_that_sum_to_total(self):
        for api_key in ("test-key", ""):
            with self.subTest(api_key=api_key or "fallback"), override_settings(OPENAI_API_KEY=api_key), fake_openai({"tecnicas": 1}):
                _, ai_prompt = self._teacher_and_ai_prompts(STRONG_DATA)
                lines = feedback_lines(ai_prompt)
                points = criteria_points(lines)

                self.assertEqual(len(points), 9)  # los 9 criterios del Prompt Canvas
                self.assertAlmostEqual(sum(points), float(ai_prompt.score), places=1)
                self.assertIn(f"Puntaje total: {ai_prompt.score}/100", lines)
                self.assertFalse(any(line.startswith("Ajuste de puntaje:") for line in lines))

    def test_quality_message_only_from_85(self):
        cases = [
            ({"contexto": 2, "tecnicas": 1, "tonalidad": 1}, 85.0, True),
            ({"contexto": 2, "tecnicas": 1, "tonalidad": 1, "referencias": 1}, 82.5, False),
        ]
        for levels, expected_score, has_message in cases:
            with self.subTest(score=expected_score), fake_openai(levels):
                teacher_prompt, ai_prompt = self._teacher_and_ai_prompts(STRONG_DATA)
                for prompt in (teacher_prompt, ai_prompt):
                    self.assertEqual(prompt.score, expected_score)
                    self.assertEqual(QUALITY_MESSAGE in prompt.feedback, has_message)

    def test_adjustment_line_explains_capped_score(self):
        weaker_rules_data = dict(STRONG_DATA, process="", constraints="")  # reglas internas: 80.8
        cases = [
            (
                STRONG_DATA,
                {"contexto": 1},
                74.0,
                "Ajuste de puntaje: Puntaje ajustado a 74 de 85 porque el contexto es insuficiente.",
            ),
            (
                weaker_rules_data,
                {},
                90.8,
                "Ajuste de puntaje: Puntaje ajustado a 90.8 de 100 porque la evaluación con IA supera "
                "en más de 10 puntos a la evaluación por reglas internas (80.8).",
            ),
        ]
        for data, levels, expected_score, expected_line in cases:
            with self.subTest(expected_score=expected_score), fake_openai(levels):
                _, ai_prompt = self._teacher_and_ai_prompts(data)
                lines = feedback_lines(ai_prompt)

                self.assertEqual(ai_prompt.score, expected_score)
                self.assertIn(expected_line, lines)
                # La linea de ajuste va justo despues del puntaje total
                total_index = lines.index(f"Puntaje total: {expected_score}/100")
                self.assertEqual(lines[total_index + 1], expected_line)

                # En el detalle se muestra dentro del bloque de puntaje
                self.client.force_login(self.user)
                response = self.client.get(reverse("prompt_lab:prompt-detail", args=[ai_prompt.id]))
                self.assertContains(response, expected_line.removeprefix("Ajuste de puntaje: "))


class FeedbackBlocksTests(TestCase):

    def test_groups_new_feedback_with_accents_and_old_feedback_without_accents(self):
        from .views.prompt_views import _feedback_to_blocks

        new_feedback = [
            "Retroalimentación general: Buen prompt.",
            "Técnicas de Prompting: 2.5 de 5 puntos. Uso básico (ej.: instrucciones simples).",
            "El prompt aún no alcanza nivel de calidad.",
        ]
        old_feedback = [
            "Retroalimentacion general: Buen prompt.",
            "Tecnicas de Prompting: 2.5 de 5 puntos. Uso basico (ej: instrucciones simples).",
            "El prompt aun no alcanza nivel de calidad.",
        ]
        for feedback in (new_feedback, old_feedback):
            with self.subTest(feedback=feedback[0]):
                keys = [block["key"] for block in _feedback_to_blocks(feedback)]
                self.assertEqual(keys, ["status", "general", "tecnicas"])

    @override_settings(OPENAI_API_KEY="")
    def test_rule_feedback_uses_correct_spelling(self):
        from .ai.prompt_builder import build_prompt, evaluate_prompt

        weak_data = {"purpose": "clase", "role": "profesor", "context": "colegio", "task": "haz algo",
                     "process": "", "format": "texto", "constraints": ""}
        _, feedback = evaluate_prompt(build_prompt(weak_data), data=weak_data)

        self.assertIn("Estado de calidad: El prompt aún no alcanza nivel de calidad. Revise las recomendaciones.", feedback)
        self.assertIn("Técnicas de Prompting: 0 de 5 puntos. No usa técnicas.", feedback)
        self.assertTrue(any("evaluación formativa" in line for line in feedback))


@override_settings(ALLOWED_HOSTS=["*"], OPENAI_API_KEY="")
class QualityStatusBlockTests(TestCase):

    def test_status_lines_go_to_status_block_in_new_and_saved_feedback(self):
        from .views.prompt_views import _feedback_to_blocks, _feedback_to_items

        new_feedback = (
            "- Estado de calidad: El prompt aún no alcanza nivel de calidad. Revise las recomendaciones.\n"
            "- Puntaje total: 40.0/100"
        )
        saved_feedback = (
            "- Estado de calidad: El prompt aun no alcanza nivel de calidad. Revisa las recomendaciones.\n"
            "- Puntaje total: 40.0/100"
        )
        quality_feedback = "- Estado de calidad: El prompt ya tiene calidad para uso docente.\n- Puntaje total: 92.5/100"

        cases = [
            (new_feedback, "El prompt aún no alcanza nivel de calidad. Revise las recomendaciones."),
            (saved_feedback, "El prompt aun no alcanza nivel de calidad. Revisa las recomendaciones."),
            (quality_feedback, "El prompt ya tiene calidad para uso docente."),
        ]
        for feedback, expected_status in cases:
            with self.subTest(status=expected_status):
                blocks = {block["key"]: block for block in _feedback_to_blocks(_feedback_to_items(feedback))}

                self.assertEqual(blocks["status"]["title"], "Estado de calidad")
                self.assertEqual(blocks["status"]["entries"], [expected_status])
                self.assertNotIn("other", blocks)

    def test_detail_page_shows_status_in_status_block(self):
        from .models import Prompt

        user = get_user_model().objects.create_user("estado@gmail.com", "Clave#2026", first_name="Eva", last_name="Paz")
        # Prompt nuevo (retroalimentacion generada ahora) y prompt guardado con el texto anterior sin tildes
        new_prompt = prompt_services.create_prompt_service(user, STRONG_DATA)
        saved_prompt = prompt_services.create_prompt_service(user, STRONG_DATA)
        Prompt.objects.filter(pk=saved_prompt.pk).update(
            feedback="- Estado de calidad: El prompt aun no alcanza nivel de calidad. Revisa las recomendaciones.\n"
                     "- Puntaje total: 40.0/100"
        )

        self.client.force_login(user)
        for prompt in (new_prompt, saved_prompt):
            with self.subTest(prompt=prompt.pk):
                response = self.client.get(reverse("prompt_lab:prompt-detail", args=[prompt.pk]))
                blocks = {block["key"]: block for block in response.context["thread_cards"][0]["feedback_blocks"]}

                self.assertIn("status", blocks)
                self.assertNotIn("other", blocks)
                self.assertContains(response, '<div class="feedback-title">Estado de calidad</div>', html=False)
