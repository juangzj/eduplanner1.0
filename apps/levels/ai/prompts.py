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
    Learning: {prompt_data.get('learning', '')}
    Didactic Resources: {prompt_data.get('didactic_resources', '')}
    Learning Evidence: {prompt_data.get('learning_evidence', '')}
    Evaluation Criteria: {prompt_data.get('evaluation_criteria', '')}
    Assessment Instrument: {prompt_data.get('assessment_instrument', '')}
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
Learning: {prompt_data.get('learning')}
Didactic resources: {prompt_data.get('didactic_resources')}
Learning evidence: {prompt_data.get('learning_evidence')}
Evaluation criteria: {prompt_data.get('evaluation_criteria')}
Assessment instrument: {prompt_data.get('assessment_instrument')}
Performance description: {prompt_data.get('level_description')}

Pedagogical rules you must follow:

1. The rubric must be clearly aligned with learning, didactic resources, learning evidence, evaluation criteria and assessment instrument.
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


class ClassPlanningPrompt:
        """Prompts for generating class planning content."""

        @staticmethod
        def build_prompt(prompt_data: dict[str, Any]) -> str:
                """
                Build the prompt for generating a complete class planning.
                """
                return f"""
You are an expert educational pedagogue specialized in classroom planning, competency-based learning and didactic sequencing.

Your task is to generate a complete class planning in Spanish, using the context provided below.

Pedagogical rules you must follow:

1. The planning must be coherent with learning, didactic resources, evidences, performance levels and assessment rubric.
2. The content must be practical for a teacher to use in class.
3. Use clear, professional and pedagogically precise language.
4. Organize the planning with readable Markdown structure.
5. Include pedagogical sections such as objective, moments of the class, activities, assessment and resources.
6. Avoid vague generic statements.
7. Adapt the language to the grade and academic period.
8. Use the teacher prompt as the pedagogical intention, but do not copy it blindly.
9. Make the sequence realistic for a class of {prompt_data.get('duration_minutes')} minutes.

Context:

Area: {prompt_data.get('area', '')}
Grade: {prompt_data.get('grade', '')}
Academic Period: {prompt_data.get('academic_period', '')}
Learning: {prompt_data.get('learning', '')}
Didactic Resources: {prompt_data.get('didactic_resources', '')}
Learning Evidence: {prompt_data.get('learning_evidence', '')}
Evaluation Criteria: {prompt_data.get('evaluation_criteria', '')}
Assessment Instrument: {prompt_data.get('assessment_instrument', '')}
Level Title: {prompt_data.get('level_title', '')}
Level Description: {prompt_data.get('level_description', '')}
Low Level: {prompt_data.get('low_level', '')}
Basic Level: {prompt_data.get('basic_level', '')}
High Level: {prompt_data.get('high_level', '')}
Superior Level: {prompt_data.get('superior_level', '')}
Rubric Title: {prompt_data.get('rubric_title', '')}
Rubric Description: {prompt_data.get('rubric_description', '')}
Rubric Content: {prompt_data.get('rubric_content', '')}
Topic: {prompt_data.get('topic', '')}
Subtopic: {prompt_data.get('subtopic', '')}
Class Objective: {prompt_data.get('class_objective', '')}
Duration Minutes: {prompt_data.get('duration_minutes', '')}
Methodology: {prompt_data.get('methodology', '')}
Resources: {prompt_data.get('resources', '')}
Teacher Prompt: {prompt_data.get('prompt', '')}

Generate a complete class planning with this structure:

1. Title
2. General context
3. Class objective
4. Development of the class with three moments: inicio, desarrollo y cierre
5. Assessment strategy aligned with the rubric
6. Required resources
7. Teacher notes or recommendations

Return ONLY a valid JSON object with this exact structure:

{{
    "generated_content": ""
}}

The generated_content value MUST contain only Markdown formatted text.
Do not add explanations.
Do not add extra keys.
Do not add text outside the JSON.
                """
