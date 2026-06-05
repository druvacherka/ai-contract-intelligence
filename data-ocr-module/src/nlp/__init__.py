"""
NLP Module — Contract Intelligence Platform.

Provides legal clause classification (NLPEngine) and contract risk
scoring (RiskEngine) for the AI Contract Intelligence pipeline.
"""

from src.nlp.nlp_engine import NLPEngine
from src.nlp.risk_engine import RiskEngine

__all__ = ["NLPEngine", "RiskEngine"]
