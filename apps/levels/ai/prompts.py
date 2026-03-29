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
    Subject: {prompt_data.get('subject', '')}
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
        Uses generated levels and context to create a coherent rubric.
        """
        return f"""
    You are an expert educational pedagogue specialized in competency-based assessment.

    Your task is to generate a complete assessment rubric in Spanish using the context and the four generated performance levels.

    Rules:
    1. The rubric must align with the competency, statement, and learning evidence.
    2. The rubric must be practical and ready for classroom use.
    3. Use clear, professional, and concise language.
    4. Keep pedagogical coherence with Bloom's taxonomy progression already represented in the levels.
    5. The rubric content should clearly map each criterion to the four performance levels.

    Context:

    Area: {prompt_data.get('area', '')}
    Subject: {prompt_data.get('subject', '')}
    Grade: {prompt_data.get('grade', '')}
    Academic Period: {prompt_data.get('academic_period', '')}
    Competency: {prompt_data.get('competency', '')}
    Learning Statement: {prompt_data.get('statement', '')}
    Learning Evidence: {prompt_data.get('learning_evidence', '')}
    Level Title: {prompt_data.get('level_title', '')}
    Level Description: {prompt_data.get('level_description', '')}

    Generated performance levels:
    
    Low Level: {prompt_data.get('low_level', '')}
    Basic Level: {prompt_data.get('basic_level', '')}
    High Level: {prompt_data.get('high_level', '')}
    Superior Level: {prompt_data.get('superior_level', '')}

    Generate a comprehensive assessment rubric that:
    - Has a clear, descriptive title related to the competency
    - Includes a brief description of the rubric's purpose and use
    - Provides detailed rubric content with criteria and performance indicators

    Return ONLY a valid JSON object with these keys:

    title
    rubric_description
    rubric_content

    Formatting expectations:
    - title: short and specific title for the rubric in Spanish.
    - rubric_description: short paragraph (2-3 sentences) explaining scope and use.
    - rubric_content: structured rubric text in Spanish, organized with clear criteria and progression across the four levels.

    Do not include markdown fences.
    Do not include explanations.
    Do not include extra keys.
    """
