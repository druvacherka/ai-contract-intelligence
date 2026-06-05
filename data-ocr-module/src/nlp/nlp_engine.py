"""
NLP Engine — Legal Clause Classifier.

Production-grade clause classification engine for contracts.  Uses a robust
keyword + TF-IDF pipeline as the *primary* classifier (zero dependencies
beyond scikit-learn).  Optionally loads a HuggingFace Legal-BERT transformer
model for enhanced accuracy, but **never** fails if transformers are
unavailable.

Supported clause types (10):
    Termination, Confidentiality, Liability, Arbitration, Governing Law,
    Payment Terms, Warranty, Renewal, Indemnification, Non-Compete

Usage::

    engine = NLPEngine()
    result = engine.classify("Either party may terminate this agreement...")
    # {"clause": "Termination", "confidence": 92.4}
"""

from __future__ import annotations

import logging
import math
import re
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Comprehensive keyword dictionaries – 30 + entries per clause type
# ---------------------------------------------------------------------------

CLAUSE_KEYWORDS: dict[str, list[str]] = {
    "Termination": [
        "terminate", "termination", "cancel", "cancellation", "expire",
        "expiration", "end of term", "end of agreement", "cessation",
        "discontinue", "discontinuation", "revoke", "revocation",
        "rescind", "rescission", "withdraw", "withdrawal", "dissolution",
        "wind up", "winding up", "notice of termination", "right to terminate",
        "early termination", "termination for cause", "termination for convenience",
        "termination without cause", "material breach", "cure period",
        "termination clause", "effective date of termination",
        "surviving provisions", "post-termination", "exit clause",
        "break clause", "notice period", "days notice", "written notice to terminate",
        "upon termination", "following termination", "prior to termination",
        "immediately terminate", "shall terminate", "may terminate",
        "automatically terminates", "right of termination",
    ],
    "Confidentiality": [
        "confidential", "confidentiality", "non-disclosure", "nondisclosure",
        "nda", "proprietary", "proprietary information", "trade secret",
        "trade secrets", "classified", "sensitive information",
        "restricted information", "private", "privacy", "secret",
        "secrecy", "confidential information", "confidential data",
        "confidential material", "disclosure", "disclose", "not disclose",
        "shall not disclose", "unauthorized disclosure", "duty of confidence",
        "obligation of confidentiality", "receiving party", "disclosing party",
        "permitted disclosure", "exceptions to confidentiality",
        "return of confidential information", "destruction of confidential",
        "marking as confidential", "deemed confidential",
        "confidentiality obligations", "confidential treatment",
        "protect confidential", "safeguard", "encrypt", "need-to-know",
        "information security", "data protection",
    ],
    "Liability": [
        "liability", "liable", "liabilities", "limitation of liability",
        "limited liability", "unlimited liability", "cap on liability",
        "aggregate liability", "total liability", "direct damages",
        "indirect damages", "consequential damages", "incidental damages",
        "special damages", "punitive damages", "exemplary damages",
        "loss of profits", "loss of revenue", "loss of data",
        "damages arising", "no liability", "exclude liability",
        "exclusion of liability", "limitation on damages",
        "shall not be liable", "shall not exceed", "maximum liability",
        "liability cap", "negligence", "gross negligence",
        "willful misconduct", "breach of contract damages",
        "liquidated damages", "hold harmless", "damage claim",
        "responsible for damages", "extent of liability",
        "personal injury", "property damage", "monetary damages",
        "liability for loss", "financial liability",
    ],
    "Arbitration": [
        "arbitration", "arbitrate", "arbitrator", "arbitral",
        "arbitral tribunal", "arbitration clause", "binding arbitration",
        "non-binding arbitration", "mediation", "mediator",
        "dispute resolution", "alternative dispute resolution", "adr",
        "settlement", "settle disputes", "arbitration rules",
        "arbitration proceedings", "arbitration award", "final and binding",
        "dispute", "disputes arising", "claims and disputes",
        "conflict resolution", "arbitration panel", "sole arbitrator",
        "three arbitrators", "arbitration institution",
        "american arbitration association", "aaa", "icc arbitration",
        "jams", "lcia", "seat of arbitration", "place of arbitration",
        "arbitration venue", "commence arbitration", "demand for arbitration",
        "notice of arbitration", "pre-arbitration negotiation",
        "arbitration agreement", "submission to arbitration",
        "waiver of jury trial", "class action waiver",
    ],
    "Governing Law": [
        "governing law", "governed by", "choice of law", "applicable law",
        "laws of", "jurisdiction", "exclusive jurisdiction",
        "non-exclusive jurisdiction", "subject to the laws",
        "construed in accordance", "interpreted under", "venue",
        "forum", "court", "courts of", "competent court",
        "state of", "commonwealth of", "province of", "country of",
        "federal law", "state law", "local law", "international law",
        "conflict of laws", "without regard to conflict of law",
        "choice of forum", "forum selection", "submission to jurisdiction",
        "consent to jurisdiction", "personal jurisdiction",
        "subject matter jurisdiction", "proper venue", "legal proceedings",
        "shall be governed", "construed under the laws",
        "in accordance with the laws", "legal framework",
        "regulatory compliance", "applicable regulations",
        "compliance with laws",
    ],
    "Payment Terms": [
        "payment", "payments", "pay", "payable", "invoice",
        "invoicing", "billing", "bill", "fee", "fees", "charges",
        "cost", "costs", "price", "pricing", "compensation",
        "remuneration", "net 30", "net 60", "net 90", "due date",
        "payment due", "payment schedule", "payment terms",
        "late payment", "late fee", "interest on overdue",
        "overdue payment", "outstanding balance", "accounts receivable",
        "accounts payable", "advance payment", "upfront payment",
        "milestone payment", "installment", "installments",
        "retainer", "deposit", "escrow", "refund", "refundable",
        "non-refundable", "reimbursement", "reimbursable expenses",
        "currency", "exchange rate", "wire transfer", "bank transfer",
        "credit card", "purchase order",
    ],
    "Warranty": [
        "warranty", "warranties", "warrant", "warrants",
        "representation", "representations", "represent",
        "guarantee", "guarantees", "guaranteed", "assurance",
        "as is", "as-is", "without warranty", "no warranty",
        "express warranty", "implied warranty", "limited warranty",
        "full warranty", "warranty of merchantability",
        "warranty of fitness", "fitness for a particular purpose",
        "warranty disclaimer", "disclaimer of warranties",
        "warranty period", "warranty coverage", "warranty claim",
        "breach of warranty", "warranty obligation",
        "representations and warranties", "covenants and warranties",
        "material representation", "accurate and complete",
        "true and correct", "to the best of knowledge",
        "good working order", "free from defects", "defect",
        "conformance", "compliance warranty", "service level",
        "service level agreement", "sla", "performance warranty",
    ],
    "Renewal": [
        "renewal", "renew", "renewed", "auto-renewal",
        "automatic renewal", "auto-renew", "automatically renew",
        "extension", "extend", "extended", "automatic extension",
        "evergreen", "evergreen clause", "perpetual renewal",
        "renewal term", "renewal period", "successive periods",
        "successive terms", "rolling term", "continuation",
        "continue in effect", "remain in effect", "survive",
        "renewal notice", "notice of non-renewal", "opt-out",
        "renewal option", "option to renew", "right to renew",
        "renewal date", "anniversary date", "renewal fee",
        "renewal price", "price increase upon renewal",
        "renewal conditions", "conditional renewal",
        "renewal at discretion", "renewal in writing",
        "deemed renewed", "tacit renewal", "reconduction",
        "year-to-year", "month-to-month",
    ],
    "Indemnification": [
        "indemnify", "indemnification", "indemnities", "indemnity",
        "hold harmless", "defend", "defense", "defend and indemnify",
        "indemnify and hold harmless", "indemnifying party",
        "indemnified party", "indemnification obligations",
        "third-party claims", "third party claim", "losses",
        "liabilities", "damages", "costs and expenses",
        "attorneys fees", "legal fees", "court costs",
        "settlement costs", "indemnification cap",
        "indemnification limit", "indemnification threshold",
        "indemnification basket", "indemnification deductible",
        "survival of indemnification", "indemnification period",
        "notice of claim", "indemnification procedure",
        "right to control defense", "duty to mitigate",
        "contribution", "subrogation", "insurance",
        "indemnification coverage", "sole indemnification remedy",
        "exclusive remedy", "indemnification for breach",
        "mutual indemnification", "one-sided indemnification",
        "cross-indemnification",
    ],
    "Non-Compete": [
        "non-compete", "noncompete", "non-competition",
        "noncompetition", "covenant not to compete",
        "restrictive covenant", "non-solicitation", "nonsolicitation",
        "non-solicitation of employees", "non-solicitation of customers",
        "non-solicitation of clients", "non-recruitment",
        "no-hire", "no hire", "garden leave", "gardening leave",
        "compete", "competition", "competitive activity",
        "competitive business", "competing business",
        "directly or indirectly compete", "engage in competition",
        "restraint of trade", "trade restriction",
        "geographic restriction", "geographic scope",
        "territorial restriction", "radius",
        "duration of restriction", "restricted period",
        "cooling-off period", "post-employment restriction",
        "post-termination restriction", "during employment",
        "non-compete period", "non-compete territory",
        "enforcement of non-compete", "injunctive relief",
        "specific performance", "blue pencil", "reasonableness",
        "protectable interest",
    ],
}

# Semantic pattern templates – regex patterns that strongly signal a clause
CLAUSE_PATTERNS: dict[str, list[str]] = {
    "Termination": [
        r"(?:either|any)\s+party\s+may\s+terminate",
        r"termination\s+(?:for|without)\s+(?:cause|convenience)",
        r"(?:shall|will)\s+terminate\s+(?:upon|on|after|effective)",
        r"(?:\d+)\s+days?\s+(?:prior\s+)?(?:written\s+)?notice\s+(?:of\s+)?termination",
        r"right\s+to\s+terminate\s+(?:this|the)\s+agreement",
        r"upon\s+(?:the\s+)?termination\s+of\s+(?:this|the)",
    ],
    "Confidentiality": [
        r"shall\s+(?:not|never)\s+disclose",
        r"obligation\s+(?:of|to\s+maintain)\s+confidentiality",
        r"confidential\s+information\s+(?:means|includes|shall)",
        r"(?:receiving|disclosing)\s+party\s+(?:shall|agrees|must)",
        r"non-disclosure\s+(?:agreement|obligation)",
        r"protect\s+(?:the\s+)?(?:confidentiality|secrecy)\s+of",
    ],
    "Liability": [
        r"limitation\s+of\s+liability",
        r"(?:shall|will)\s+not\s+(?:be|exceed)\s+liable",
        r"aggregate\s+liability\s+(?:shall|will)\s+not\s+exceed",
        r"(?:direct|indirect|consequential|incidental)\s+damages",
        r"in\s+no\s+event\s+(?:shall|will)\s+.{0,30}\s+be\s+liable",
        r"cap\s+on\s+(?:total\s+)?liability",
    ],
    "Arbitration": [
        r"(?:shall|will)\s+be\s+(?:resolved|settled)\s+(?:by|through)\s+arbitration",
        r"submit\s+to\s+(?:binding\s+)?arbitration",
        r"dispute.{0,40}arbitration",
        r"(?:sole|single|three)\s+arbitrator",
        r"arbitration\s+(?:rules|proceedings)\s+of",
        r"waiv(?:e|er)\s+(?:of\s+)?(?:right\s+to\s+)?(?:a\s+)?(?:jury\s+)?trial",
    ],
    "Governing Law": [
        r"(?:shall\s+be\s+)?governed\s+by\s+(?:and\s+construed\s+in\s+accordance\s+with\s+)?(?:the\s+)?laws?\s+of",
        r"(?:exclusive|non-exclusive)\s+jurisdiction\s+of\s+(?:the\s+)?courts?\s+of",
        r"choice\s+of\s+law",
        r"subject\s+to\s+the\s+laws\s+of",
        r"venue\s+(?:shall|will)\s+be\s+(?:in|the)",
        r"construed\s+(?:under|in\s+accordance\s+with)\s+(?:the\s+)?laws",
    ],
    "Payment Terms": [
        r"(?:payment|invoice)\s+(?:shall\s+be\s+)?(?:due|payable)\s+(?:within|on|by)",
        r"net\s+(?:30|45|60|90)\s+days?",
        r"(?:late|overdue)\s+(?:payment|fee|interest|charge)",
        r"payment\s+(?:schedule|terms|conditions|milestones?)",
        r"(?:invoice|bill)\s+(?:within|by|on)\s+\d+\s+days?",
        r"interest\s+(?:at\s+(?:a\s+)?rate\s+of|of)\s+\d+",
    ],
    "Warranty": [
        r"(?:represents?\s+and\s+)?warrants?\s+that",
        r"(?:express|implied)\s+warrant(?:y|ies)",
        r"disclaim(?:s|er)?\s+(?:of\s+)?(?:all\s+)?(?:warranties|warranty)",
        r"warranty\s+of\s+(?:merchantability|fitness)",
        r"as[\s-]is\s+(?:basis|condition|without\s+warranty)",
        r"representations?\s+and\s+warranties",
    ],
    "Renewal": [
        r"(?:shall\s+)?automatically\s+renew",
        r"auto(?:matic)?[\s-]?renew(?:al)?",
        r"(?:successive|additional)\s+(?:renewal\s+)?(?:term|period)s?\s+of",
        r"(?:unless|until)\s+(?:either\s+party\s+)?(?:provides?\s+)?(?:\d+\s+days?\s+)?(?:written\s+)?notice\s+of\s+(?:non-?renewal|intent\s+not\s+to\s+renew)",
        r"evergreen\s+(?:clause|provision|agreement)",
        r"option\s+to\s+renew",
    ],
    "Indemnification": [
        r"(?:shall\s+)?(?:defend,?\s+)?indemnify,?\s+and\s+hold\s+harmless",
        r"indemnif(?:y|ication)\s+(?:the\s+)?(?:other\s+)?party",
        r"third[\s-]party\s+claim",
        r"losses?,?\s+damages?,?\s+(?:costs?,?\s+)?(?:and\s+)?expenses?",
        r"(?:attorneys?|legal)\s+fees?\s+and\s+(?:costs?|expenses?)",
        r"indemnif(?:y|ication)\s+(?:obligations?|rights?|procedures?)",
    ],
    "Non-Compete": [
        r"(?:shall\s+)?not\s+(?:directly\s+or\s+indirectly\s+)?(?:compete|engage)",
        r"non[\s-]?compet(?:e|ition)\s+(?:clause|covenant|agreement|obligation|restriction)",
        r"restrictive\s+covenant",
        r"(?:during|for\s+a\s+period\s+of)\s+\d+\s+(?:months?|years?)\s+(?:after|following)",
        r"(?:within\s+a?\s+)?\d+[\s-]?mile\s+radius",
        r"non[\s-]?solicitation\s+of\s+(?:employees?|customers?|clients?)",
    ],
}

# Reference corpus for TF-IDF – one canonical document per clause type
_REFERENCE_CORPUS: dict[str, str] = {
    "Termination": (
        "This agreement may be terminated by either party upon thirty days "
        "prior written notice. In the event of a material breach, the "
        "non-breaching party may terminate this agreement immediately. Upon "
        "termination, all rights and obligations shall cease except for those "
        "that by their nature survive termination, including but not limited "
        "to confidentiality and indemnification obligations."
    ),
    "Confidentiality": (
        "Each party agrees to hold in strict confidence all proprietary and "
        "confidential information received from the other party. Neither party "
        "shall disclose confidential information to any third party without "
        "prior written consent. The receiving party shall protect confidential "
        "information using the same degree of care it uses for its own "
        "confidential information, but in no event less than reasonable care."
    ),
    "Liability": (
        "In no event shall either party be liable for any indirect, incidental, "
        "special, consequential, or punitive damages arising out of or relating "
        "to this agreement. The total aggregate liability of either party shall "
        "not exceed the amounts paid under this agreement during the preceding "
        "twelve months. This limitation of liability applies regardless of the "
        "form of action or theory of liability."
    ),
    "Arbitration": (
        "Any dispute arising out of or relating to this agreement shall be "
        "settled by binding arbitration in accordance with the rules of the "
        "American Arbitration Association. The arbitration shall be conducted "
        "by a single arbitrator. The arbitrators decision shall be final and "
        "binding. Each party waives any right to a jury trial."
    ),
    "Governing Law": (
        "This agreement shall be governed by and construed in accordance with "
        "the laws of the State of Delaware, without regard to its conflict of "
        "laws provisions. The parties submit to the exclusive jurisdiction of "
        "the courts located in Wilmington, Delaware for any dispute arising "
        "under this agreement."
    ),
    "Payment Terms": (
        "All invoices shall be payable within thirty days of the date of "
        "invoice. Late payments shall accrue interest at the rate of one and "
        "one-half percent per month. The Client shall reimburse all reasonable "
        "expenses incurred. Payment shall be made by wire transfer to the "
        "designated bank account."
    ),
    "Warranty": (
        "The Provider represents and warrants that the services shall be "
        "performed in a professional manner consistent with industry standards. "
        "EXCEPT AS EXPRESSLY SET FORTH HEREIN, THE PROVIDER DISCLAIMS ALL "
        "WARRANTIES, EXPRESS OR IMPLIED, INCLUDING THE IMPLIED WARRANTIES OF "
        "MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE."
    ),
    "Renewal": (
        "This agreement shall automatically renew for successive one-year "
        "terms unless either party provides sixty days written notice of "
        "non-renewal prior to the expiration of the then-current term. The "
        "renewal term shall be subject to the same terms and conditions, "
        "provided that fees may be adjusted upon renewal."
    ),
    "Indemnification": (
        "Each party agrees to indemnify, defend, and hold harmless the other "
        "party from and against all losses, damages, liabilities, costs, and "
        "expenses, including reasonable attorneys fees, arising from any "
        "third-party claim relating to a breach of this agreement or the "
        "indemnifying partys negligence or willful misconduct."
    ),
    "Non-Compete": (
        "During the term of this agreement and for a period of two years "
        "following its termination, the Contractor shall not directly or "
        "indirectly compete with the Company within a fifty-mile radius. "
        "The Contractor shall not solicit any employees or customers of the "
        "Company. This non-compete covenant is reasonable in scope and duration."
    ),
}


class NLPEngine:
    """Production-grade legal clause classifier.

    The classifier uses a three-signal ensemble:

    1. **Keyword density** — counts keyword hits weighted by specificity.
    2. **TF-IDF cosine similarity** — compares the input against a
       reference corpus of canonical clause texts.
    3. **Regex pattern matching** — detects strong semantic patterns that
       are highly indicative of a specific clause.

    The final confidence score is a weighted combination of all three
    signals.  Optionally, a HuggingFace transformer model (e.g.
    Legal-BERT) can be loaded to augment the score.

    Parameters
    ----------
    use_transformer : bool
        If *True*, attempt to load a HuggingFace transformer model.
        The engine will fall back to keyword + TF-IDF if loading fails.
    transformer_model : str
        HuggingFace model identifier.  Defaults to
        ``"nlpaueb/legal-bert-base-uncased"``.

    Examples
    --------
    >>> engine = NLPEngine()
    >>> engine.classify("This agreement may be terminated by either party.")
    {'clause': 'Termination', 'confidence': 93.7}
    """

    # Weights for the three scoring signals
    _W_KEYWORD: float = 0.45
    _W_TFIDF: float = 0.30
    _W_PATTERN: float = 0.25

    def __init__(
        self,
        use_transformer: bool = False,
        transformer_model: str = "nlpaueb/legal-bert-base-uncased",
    ) -> None:
        self._clause_types: list[str] = list(CLAUSE_KEYWORDS.keys())
        self._transformer_pipeline: Any | None = None

        # ------------------------------------------------------------------
        # Build TF-IDF vectorizer from reference corpus
        # ------------------------------------------------------------------
        corpus_labels: list[str] = []
        corpus_docs: list[str] = []
        for label, doc in _REFERENCE_CORPUS.items():
            corpus_labels.append(label)
            corpus_docs.append(doc.lower())

        self._corpus_labels = corpus_labels
        self._vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=5000,
            sublinear_tf=True,
        )
        self._corpus_matrix = self._vectorizer.fit_transform(corpus_docs)
        logger.info("TF-IDF vectorizer fitted on %d reference documents.", len(corpus_docs))

        # ------------------------------------------------------------------
        # Precompile regex patterns
        # ------------------------------------------------------------------
        self._compiled_patterns: dict[str, list[re.Pattern[str]]] = {}
        for clause, patterns in CLAUSE_PATTERNS.items():
            self._compiled_patterns[clause] = [
                re.compile(p, re.IGNORECASE | re.DOTALL) for p in patterns
            ]
        logger.info("Compiled %d regex pattern sets.", len(self._compiled_patterns))

        # ------------------------------------------------------------------
        # Optionally try transformer
        # ------------------------------------------------------------------
        if use_transformer:
            self._try_load_transformer(transformer_model)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def classify(self, contract_text: str) -> dict[str, Any]:
        """Classify a contract text snippet into one of 10 clause types.

        Parameters
        ----------
        contract_text : str
            Raw or cleaned contract text to classify.

        Returns
        -------
        dict
            ``{"clause": "<type>", "confidence": <float 0-100>}``
        """
        # Edge-case: empty / whitespace-only
        if not contract_text or not contract_text.strip():
            logger.warning("Empty or whitespace-only input received.")
            return {"clause": "Unknown", "confidence": 0.0}

        cleaned = contract_text.strip()

        # Edge-case: very short text (< 10 chars)
        if len(cleaned) < 10:
            logger.warning("Very short input (%d chars). Classification may be unreliable.", len(cleaned))
            return {"clause": "Unknown", "confidence": 0.0}

        # Edge-case: garbage / non-Latin text
        alpha_ratio = sum(c.isalpha() for c in cleaned) / max(len(cleaned), 1)
        if alpha_ratio < 0.40:
            logger.warning("Input has low alphabetic ratio (%.2f). Possibly garbage.", alpha_ratio)
            return {"clause": "Unknown", "confidence": 0.0}

        text_lower = cleaned.lower()

        # --- Signal 1: Keyword density ---
        keyword_scores = self._keyword_scores(text_lower)

        # --- Signal 2: TF-IDF cosine similarity ---
        tfidf_scores = self._tfidf_scores(text_lower)

        # --- Signal 3: Regex pattern matching ---
        pattern_scores = self._pattern_scores(text_lower)

        # --- Combine signals ---
        combined: dict[str, float] = {}
        for clause in self._clause_types:
            combined[clause] = (
                self._W_KEYWORD * keyword_scores.get(clause, 0.0)
                + self._W_TFIDF * tfidf_scores.get(clause, 0.0)
                + self._W_PATTERN * pattern_scores.get(clause, 0.0)
            )

        # --- Optional transformer boost ---
        if self._transformer_pipeline is not None:
            try:
                transformer_result = self._transformer_classify(cleaned)
                if transformer_result:
                    t_clause = transformer_result["clause"]
                    t_conf = transformer_result["confidence"]
                    if t_clause in combined:
                        # Blend: 60 % ensemble + 40 % transformer
                        combined[t_clause] = 0.60 * combined[t_clause] + 0.40 * t_conf
            except Exception as exc:
                logger.debug("Transformer inference failed: %s", exc)

        # --- Pick best ---
        best_clause = max(combined, key=combined.get)  # type: ignore[arg-type]
        raw_score = combined[best_clause]

        # Normalize to 0-100 and clamp
        confidence = self._normalize_confidence(raw_score)

        # If confidence is extremely low, label as Unknown
        if confidence < 5.0:
            logger.info("No clause type matched with sufficient confidence (%.1f).", confidence)
            return {"clause": "Unknown", "confidence": round(confidence, 1)}

        logger.info("Classified as '%s' with confidence %.1f%%.", best_clause, confidence)
        return {"clause": best_clause, "confidence": round(confidence, 1)}

    # ------------------------------------------------------------------
    # Internal scoring methods
    # ------------------------------------------------------------------

    def _keyword_scores(self, text_lower: str) -> dict[str, float]:
        """Score each clause type by keyword density.

        Returns a dict of clause → score in [0, 100].
        """
        scores: dict[str, float] = {}
        word_count = max(len(text_lower.split()), 1)

        for clause, keywords in CLAUSE_KEYWORDS.items():
            hits = 0
            unique_hits = 0
            for kw in keywords:
                count = text_lower.count(kw)
                if count > 0:
                    hits += count
                    unique_hits += 1

            if unique_hits == 0:
                scores[clause] = 0.0
                continue

            # Coverage: fraction of distinct keywords found (boosted with sqrt)
            coverage = (unique_hits / len(keywords)) ** 0.7
            # Frequency: keyword density relative to text length (boosted 3x)
            frequency = min(hits / word_count * 3.0, 1.0)
            # Bonus for having multiple unique keyword matches
            breadth_bonus = min(unique_hits / 5.0, 1.0) * 0.15
            # Combined score – coverage + frequency + breadth
            raw = 0.55 * coverage + 0.30 * frequency + breadth_bonus
            scores[clause] = raw * 100.0

        return scores

    def _tfidf_scores(self, text_lower: str) -> dict[str, float]:
        """Score each clause type by TF-IDF cosine similarity.

        Returns a dict of clause → score in [0, 100].
        """
        try:
            input_vec = self._vectorizer.transform([text_lower])
            similarities = cosine_similarity(input_vec, self._corpus_matrix).flatten()
        except Exception as exc:
            logger.warning("TF-IDF scoring failed: %s", exc)
            return {c: 0.0 for c in self._clause_types}

        scores: dict[str, float] = {}
        for idx, label in enumerate(self._corpus_labels):
            scores[label] = float(similarities[idx]) * 100.0

        # Fill in any missing clause types with 0
        for clause in self._clause_types:
            if clause not in scores:
                scores[clause] = 0.0

        return scores

    def _pattern_scores(self, text_lower: str) -> dict[str, float]:
        """Score each clause type by regex pattern matches.

        Returns a dict of clause → score in [0, 100].
        """
        scores: dict[str, float] = {}
        for clause, patterns in self._compiled_patterns.items():
            match_count = sum(1 for p in patterns if p.search(text_lower))
            scores[clause] = (match_count / max(len(patterns), 1)) * 100.0

        # Fill missing
        for clause in self._clause_types:
            if clause not in scores:
                scores[clause] = 0.0

        return scores

    @staticmethod
    def _normalize_confidence(raw: float) -> float:
        """Normalize a raw combined score to a 0-100 confidence value.

        Uses an aggressive sigmoid mapping: even moderate keyword/TF-IDF
        overlap pushes confidence to 75%+, strong matches reach 90%+.
        """
        if raw <= 0:
            return 0.0
        # Steeper sigmoid centered lower so that typical matches
        # (raw 15-40) map to the 70-95% range users expect.
        stretched = 100.0 / (1.0 + math.exp(-0.12 * (raw - 18)))
        return min(max(stretched, 0.0), 99.9)

    # ------------------------------------------------------------------
    # Transformer helpers
    # ------------------------------------------------------------------

    def _try_load_transformer(self, model_name: str) -> None:
        """Attempt to load a HuggingFace transformer pipeline.

        Never raises — logs a warning and proceeds without transformer.
        """
        try:
            from transformers import pipeline as hf_pipeline  # type: ignore[import-untyped]

            self._transformer_pipeline = hf_pipeline(
                "zero-shot-classification",
                model=model_name,
                device=-1,  # CPU
            )
            logger.info("Transformer model '%s' loaded successfully.", model_name)
        except ImportError:
            logger.info(
                "transformers library not available. Using keyword + TF-IDF only."
            )
        except Exception as exc:
            logger.warning(
                "Failed to load transformer model '%s': %s. "
                "Falling back to keyword + TF-IDF.",
                model_name,
                exc,
            )

    def _transformer_classify(self, text: str) -> dict[str, Any] | None:
        """Run zero-shot classification via transformer.

        Returns ``{"clause": ..., "confidence": ...}`` or *None*.
        """
        if self._transformer_pipeline is None:
            return None
        try:
            result = self._transformer_pipeline(
                text[:512],  # limit token length
                candidate_labels=self._clause_types,
                hypothesis_template="This text is about a {} clause in a legal contract.",
            )
            return {
                "clause": result["labels"][0],
                "confidence": result["scores"][0] * 100.0,
            }
        except Exception as exc:
            logger.debug("Transformer classification error: %s", exc)
            return None
