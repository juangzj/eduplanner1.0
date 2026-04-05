from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AIProvider(ABC):
    @abstractmethod
    def generate_level_content(self, prompt_data: dict[str, Any]) -> dict[str, str]:
        """
        Generate performance levels from prompt data and return a JSON-like dict.
        """

    @abstractmethod
    def generate_assessment_content(self, prompt_data: dict[str, Any]) -> dict[str, str]:
        """
        Generate assessment rubric content from generated levels and context.
        """

    @abstractmethod
    def generate_class_planning_content(self, prompt_data: dict[str, Any]) -> dict[str, str]:
        """
        Generate a complete class planning from pedagogical context and teacher input.
        """

