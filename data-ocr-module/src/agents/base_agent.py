"""
Base Agent — Abstract Base Class for Pipeline Agents.

Provides a standardized interface for all agents in the sequential
pipeline with built-in timing, logging, and error handling.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any

from src.utils.logger import logger


class BaseAgent(ABC):
    """Abstract base class for all pipeline agents.

    Every agent in the sequential pipeline inherits from this class
    and implements the ``run()`` method.  The ``execute()`` wrapper
    adds timing, structured logging, and error handling so individual
    agents never crash the pipeline.

    Subclasses must:
    1. Set ``self._name`` in ``__init__`` (or override the property).
    2. Implement ``run(context)`` with their processing logic.
    """

    def __init__(self) -> None:
        self._name: str = self.__class__.__name__

    @property
    def name(self) -> str:
        """Human-readable agent name used in logs and reports."""
        return self._name

    @abstractmethod
    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute the agent's core logic.

        Parameters
        ----------
        context : dict
            Shared pipeline context dict.  The agent should read its
            required inputs from ``context`` and add its outputs back.

        Returns
        -------
        dict
            The *updated* context dict with new keys added.
        """
        ...

    def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Run the agent with timing, logging, and error handling.

        This is the method called by the pipeline orchestrator.  It
        wraps ``run()`` and guarantees the pipeline never crashes due
        to an individual agent failure.

        Parameters
        ----------
        context : dict
            Shared pipeline context dict.

        Returns
        -------
        dict
            Updated context.  On failure, ``agent_error`` and
            ``agent_error_name`` keys are set instead.
        """
        logger.info("▶ Agent '{}' starting…", self.name)
        start = time.time()

        try:
            context = self.run(context)
            duration = round(time.time() - start, 3)
            context.setdefault("agent_timings", {})[self.name] = duration
            logger.info(
                "✔ Agent '{}' completed in {:.3f}s",
                self.name,
                duration,
            )
        except Exception as exc:
            duration = round(time.time() - start, 3)
            context.setdefault("agent_timings", {})[self.name] = duration
            context["agent_error"] = str(exc)
            context["agent_error_name"] = self.name
            logger.error(
                "✘ Agent '{}' failed after {:.3f}s: {}",
                self.name,
                duration,
                exc,
            )

        return context
