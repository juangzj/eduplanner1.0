"""
Prompt templates for AI content generation.
Separating level generation prompts from assessment rubric prompts.
"""
from typing import Any


class LevelPrompt:
    """Prompts for generating performance levels (low, basic, high, superior)."""

    @staticmethod
    def build_prompt(prompt_data: dict[str, Any]) -> str:
        """
        Build the prompt for generating the four performance levels.
        """
        return f"""
    You are an expert educational pedagogue specialized in competency-based assessment and Bloom's Taxonomy.

    Your task is to generate performance levels for a school rubric used in academic evaluation.

    The rubric must follow these rules:

    1. The four levels must be clearly progressive and based on Bloom's Taxonomy:

    Low Level → Recognizes but presents difficulties
    Basic Level → Identifies and describes
    High Level → Analyzes and applies correctly
    Superior Level → Evaluates, justifies or proposes connections

    2. The levels MUST be aligned directly with the learning evidence.
    Do NOT generate generic levels.
    Each level must describe what the student does specifically in relation to the evidence.

    3. The descriptions must:
    - Be written in Spanish
    - Be concise (1–2 sentences per level)
    - Describe observable student performance
    - Use clear academic language
    - Avoid repeating the same structure in all levels
    - Show clear progression from weak performance to excellent performance

    4. The Low Level must describe difficulties related to the evidence (not only recognition of concepts).

    5. The Superior Level must improve the quality of the work (analysis, justification, connections, evaluation, or deeper understanding), not just repeat the same action.

    Context:

    Area: {prompt_data.get('area', '')}
    Grade: {prompt_data.get('grade', '')}
    Academic Period: {prompt_data.get('academic_period', '')}
    Competency: {prompt_data.get('competency', '')}
    Learning Statement: {prompt_data.get('statement', '')}
    Learning Evidence: {prompt_data.get('learning_evidence', '')}
    Level Title: {prompt_data.get('level_title', '')}
    Level Description: {prompt_data.get('level_description', '')}

    Generate the four performance levels in Spanish with strong pedagogical coherence.

    Return ONLY a valid JSON object with these keys:

    low_level
    basic_level
    high_level
    superior_level

    Do not include explanations.
    Do not include markdown.
    Do not include extra keys.
    """


class AssessmentPrompt:
    """Prompts for generating assessment rubrics."""

    @staticmethod
    def build_prompt(prompt_data: dict[str, Any]) -> str:
        """
        Build the prompt for generating an assessment rubric.
          Uses context to create a coherent rubric in markdown format.
        """
        return f"""
You are an expert educational pedagogue specialized in competency-based assessment and rubric design for elementary and middle school education.

Your task is to generate a high-quality assessment rubric based on the following information:

Area: {prompt_data.get('area')}
Grade: {prompt_data.get('grade')}
Academic period: {prompt_data.get('academic_period')}
Competence: {prompt_data.get('competence') or prompt_data.get('competency')}
Statement: {prompt_data.get('statement')}
Learning evidence: {prompt_data.get('learning_evidence')}
Performance description: {prompt_data.get('level_description')}

Pedagogical rules you must follow:

1. The rubric must be clearly aligned with the competence and the learning evidence.
2. The rubric must include 3 or 4 evaluation criteria only.
3. Each criterion must evaluate only one skill (do not mix multiple skills in the same criterion).
4. The criteria must be ordered from basic cognitive level to higher cognitive level.
5. The performance levels must be:
    - Nivel Bajo
    - Nivel Básico
    - Nivel Alto
    - Nivel Superior
6. Each level must show real progression (not the same sentence with small changes).
7. Use clear, professional and pedagogically correct language.
8. Do not generate very long descriptions.
9. The rubric must be appropriate for grade {prompt_data.get('grade')} students.

Now generate:

1. A professional rubric title
2. A short rubric description (maximum 3 lines)
3. A rubric table in Markdown with:
    - 3 or 4 criteria
    - The 4 performance levels
    - Clear and pedagogical wording

IMPORTANT:

The entire response MUST be written in Spanish.

Return ONLY a valid JSON object using this exact structure:

{{
  "title": "",
  "rubric_description": "",
  "rubric_content": ""
}}

Where "rubric_content" MUST contain only a valid Markdown table with this header order:
| Criterio | Nivel Bajo | Nivel Básico | Nivel Alto | Nivel Superior |

Do not add explanations.
Do not add text outside the JSON.
    """
