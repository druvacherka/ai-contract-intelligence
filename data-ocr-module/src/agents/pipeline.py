"""
Agent Pipeline — Sequential Orchestrator for 7-Agent Pipeline.

Runs all seven agents in order, passing a shared context dictionary
between them, collecting timing telemetry, and optionally reporting
progress via a callback.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Callable

from src.agents.base_agent import BaseAgent
from src.agents.clause_agent import ClauseAgent
from src.agents.compiler_agent import CompilerAgent
from src.agents.gemini_agent import GeminiAgent
from src.agents.ner_agent import NERAgent
from src.agents.ocr_agent import OCRAgent
from src.agents.risk_agent import RiskAgent
from src.agents.text_cleaning_agent import TextCleaningAgent
from src.utils.logger import logger

# Type alias for an optional progress callback.
# signature: callback(agent_index: int, total: int, agent_name: str, status: str)
ProgressCallback = Callable[[int, int, str, str], None] | None


class AgentPipeline:
    """Orchestrate the 7-agent sequential pipeline.

    Usage::

        pipeline = AgentPipeline()
        report = pipeline.run("path/to/contract.pdf", "contract.pdf")

    Parameters
    ----------
    progress_callback : callable, optional
        Called after each agent with ``(index, total, name, status)``.
    """

    def __init__(self, progress_callback: ProgressCallback = None) -> None:
        self._progress_callback = progress_callback

        # Initialise agents in execution order
        self._agents: list[BaseAgent] = [
            OCRAgent(),           # 1. Text extraction
            TextCleaningAgent(),  # 2. Text cleaning
            NERAgent(),           # 3. Named entity recognition
            ClauseAgent(),        # 4. Clause classification
            RiskAgent(),          # 5. Risk analysis
            GeminiAgent(),       # 6. AI summary
            CompilerAgent(),      # 7. Report compilation
        ]

        logger.info(
            "AgentPipeline initialised with {} agents: {}",
            len(self._agents),
            [a.name for a in self._agents],
        )

    def run(
        self,
        file_path: str,
        filename: str,
    ) -> dict[str, Any]:
        """Execute the full pipeline on a single document.

        Parameters
        ----------
        file_path : str
            Absolute or relative path to the document file.
        filename : str
            Original filename (used in the report metadata).

        Returns
        -------
        dict
            The final compiled report dictionary.
        """
        pipeline_start = time.time()
        total_agents = len(self._agents)

        # Seed the shared context
        context: dict[str, Any] = {
            "file_path": str(Path(file_path).resolve()),
            "filename": filename,
        }

        agent_logs: list[dict[str, Any]] = []

        logger.info(
            "═══ Pipeline START ═══ | file='{}' | agents={}",
            filename,
            total_agents,
        )

        for idx, agent in enumerate(self._agents, start=1):
            agent_start = time.time()

            # Notify progress callback
            if self._progress_callback:
                try:
                    self._progress_callback(idx, total_agents, agent.name, "running")
                except Exception:
                    pass  # never let a callback crash the pipeline

            # Execute the agent (execute() already handles errors)
            context = agent.execute(context)

            duration = round(time.time() - agent_start, 3)
            had_error = "agent_error" in context and context.get("agent_error_name") == agent.name
            status = "error" if had_error else "success"

            agent_logs.append({
                "agent_name": agent.name,
                "status": status,
                "duration_seconds": duration,
            })

            # Notify progress callback with result
            if self._progress_callback:
                try:
                    self._progress_callback(idx, total_agents, agent.name, status)
                except Exception:
                    pass

            logger.info(
                "  [{}/{}] {} → {} ({:.3f}s)",
                idx,
                total_agents,
                agent.name,
                status,
                duration,
            )

        # Attach pipeline telemetry
        pipeline_duration = round(time.time() - pipeline_start, 3)
        context["agent_logs"] = agent_logs
        context["pipeline_duration_seconds"] = pipeline_duration

        # Ensure compiled_report exists (CompilerAgent should have set it)
        if "compiled_report" in context:
            context["compiled_report"]["pipeline"]["agent_logs"] = agent_logs
            context["compiled_report"]["pipeline"]["total_duration_seconds"] = pipeline_duration

        logger.info(
            "═══ Pipeline COMPLETE ═══ | file='{}' | duration={:.3f}s | agents_ok={}/{}",
            filename,
            pipeline_duration,
            sum(1 for l in agent_logs if l["status"] == "success"),
            total_agents,
        )

        # Build flat result for API consumption
        result = {
            # Metadata
            'filename': context.get('filename', ''),
            'document_type': context.get('file_ext', ''),
            'pages': context.get('pages', 0),

            # OCR
            'ocr_method': context.get('ocr_method', ''),
            'ocr_confidence': context.get('ocr_confidence', 0.0),

            # Text - CRITICAL: include clean_text AND contract_text
            'clean_text': context.get('clean_text', context.get('raw_text', '')),
            'contract_text': context.get('clean_text', context.get('raw_text', '')),

            # NLP - Primary clause (for backward compat with inline pipeline)
            'clause': context.get('primary_clause', 'Unknown'),
            'primary_clause': context.get('primary_clause', 'Unknown'),
            'confidence': context.get('primary_confidence', 0.0),
            'primary_confidence': context.get('primary_confidence', 0.0),

            # Risk
            'risk_score': context.get('overall_risk_score', 0),
            'overall_risk_score': context.get('overall_risk_score', 0),
            'risk_level': context.get('overall_risk_level', 'Low'),
            'overall_risk_level': context.get('overall_risk_level', 'Low'),
            'risk_factors': context.get('risk_factors', []),
            'clause_risks': context.get('clause_risks', []),

            # Clauses - list of detected clause dicts
            'clauses': context.get('clauses', []),

            # Entities
            'entities': context.get('entities', {}),

            # AI Summary (from Gemini agent)
            'ai_summary': context.get('ai_summary', ''),
            'key_findings': context.get('key_findings', []),
            'recommendations': context.get('recommendations', []),

            # Completeness
            'missing_clauses': context.get('missing_clauses', []),
            'completeness_score': context.get('completeness_score', 0),

            # Summary (legacy format - list of bullet points from key_findings)
            'summary': context.get('summary') or context.get('key_findings', []),

            # Pipeline telemetry
            'agent_logs': agent_logs,
            'pipeline_duration_seconds': pipeline_duration,
            'compiled_report': context.get('compiled_report', {}),
        }

        return result
