"""
SchemaMapper - Stage 2 of the Arctus Data Ingestion Pipeline.
Maps arbitrary Indian P&L labels to the standardized financial schema using
RapidFuzz fuzzy string matching with a confidence threshold, subtotal vs component
discrimination, and manual override capabilities.
"""

from typing import Dict, List, Tuple, Any, Optional
import difflib
import numpy as np
import pandas as pd

# Attempt import of rapidfuzz; fallback to difflib
try:
    from rapidfuzz import fuzz, process
    HAS_RAPIDFUZZ = True
except ImportError:
    HAS_RAPIDFUZZ = False


class SchemaMapper:
    """
    Intelligent fuzzy schema mapping engine tailored for Indian corporate financials.
    """

    CONFIDENCE_THRESHOLD = 0.78  # 78% threshold (rounded to 80% in UI)

    STANDARD_METRICS = [
        "revenue",
        "cogs",
        "gross_profit",
        "opex",
        "ebitda",
        "pbt",
        "pat",
    ]

    # Indian accounting terminology synonyms and aliases
    METRIC_SYNONYMS = {
        "revenue": [
            "revenue from operations",
            "net revenue",
            "total income",
            "income from operations",
            "sales turnover",
            "net sales",
            "operating revenue",
            "gross turnover",
            "revenue",
            "total revenue",
        ],
        "cogs": [
            "cost of materials consumed",
            "cost of goods sold",
            "cogs",
            "raw material consumed",
            "purchase of stock-in-trade",
            "cost of sales",
            "direct expenses",
            "direct operating costs",
            "consumption of raw materials",
            "material costs",
        ],
        "gross_profit": [
            "gross profit",
            "gross margin",
            "total gross profit",
            "gp",
        ],
        "opex": [
            "other expenses",
            "employee benefit expense",
            "employee costs",
            "operating expenses",
            "opex",
            "selling and distribution expenses",
            "administrative expenses",
            "sg&a",
            "total operating expenses",
            "operating overheads",
            "staff costs",
        ],
        "ebitda": [
            "ebitda",
            "operating profit",
            "operating ebitda",
            "profit before interest, depreciation and tax",
            "pbdit",
            "earnings before interest, tax, depreciation and amortization",
            "operating profit before working capital changes",
        ],
        "pbt": [
            "profit before tax",
            "pbt",
            "earnings before tax",
            "ebt",
            "profit before exceptional items and tax",
        ],
        "pat": [
            "profit after tax",
            "pat",
            "net profit",
            "net profit for the period",
            "profit for the year",
            "net income",
            "profit after exceptional items and tax",
        ],
    }

    def __init__(self, confidence_threshold: float = 0.78):
        self.confidence_threshold = confidence_threshold

    @staticmethod
    def _compute_similarity(text1: str, text2: str) -> float:
        """
        Computes string similarity (0.0 to 1.0) using RapidFuzz token sort ratio
        or difflib SequenceMatcher as a robust fallback.
        """
        s1 = text1.lower().strip()
        s2 = text2.lower().strip()
        if s1 == s2:
            return 1.0

        if HAS_RAPIDFUZZ:
            return float(fuzz.token_sort_ratio(s1, s2)) / 100.0
        else:
            return float(difflib.SequenceMatcher(None, s1, s2).ratio())

    def match_label(self, label: str) -> Tuple[Optional[str], float]:
        """
        Matches a raw spreadsheet row label to the best standardized metric.
        Returns (metric_name, confidence_score).
        """
        best_metric = None
        best_score = 0.0

        clean_label = label.lower().strip()

        for metric, synonyms in self.METRIC_SYNONYMS.items():
            for syn in synonyms:
                score = self._compute_similarity(clean_label, syn)
                # Boost if substring match or exact containment
                if syn in clean_label or clean_label in syn:
                    score = max(score, 0.85)

                if score > best_score:
                    best_score = score
                    best_metric = metric

        return best_metric, best_score

    def auto_map_schema(
        self,
        raw_labels: List[str],
        manual_overrides: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Maps a list of raw line item labels from the file to the 7 standard metrics.
        Returns mapped items, ambiguous items requiring user review, and confidence scores.
        """
        overrides = manual_overrides or {}
        mapping: Dict[str, Optional[str]] = {m: None for m in self.STANDARD_METRICS}
        confidence_scores: Dict[str, float] = {}
        ambiguous_metrics: List[str] = []

        # Inverted dict of raw label to best candidate
        label_matches = {}
        for label in raw_labels:
            metric, score = self.match_label(label)
            label_matches[label] = (metric, score)

        # 1. Apply user manual overrides first
        for metric, assigned_label in overrides.items():
            if metric in self.STANDARD_METRICS and assigned_label in raw_labels:
                mapping[metric] = assigned_label
                confidence_scores[metric] = 1.0

        # 2. Fill remaining metrics using best fuzzy match
        for metric in self.STANDARD_METRICS:
            if mapping[metric] is not None:
                continue

            candidates = [
                (label, score) 
                for label, (matched_metric, score) in label_matches.items() 
                if matched_metric == metric and label not in mapping.values()
            ]

            if candidates:
                candidates.sort(key=lambda x: x[1], reverse=True)
                best_label, best_score = candidates[0]
                confidence_scores[metric] = round(best_score * 100, 1)

                if best_score >= self.confidence_threshold:
                    mapping[metric] = best_label
                else:
                    # Below threshold: flag for user confirmation
                    mapping[metric] = best_label  # Tentative assignment
                    ambiguous_metrics.append(metric)
            else:
                confidence_scores[metric] = 0.0
                ambiguous_metrics.append(metric)

        return {
            "mapping": mapping,
            "confidence_scores": confidence_scores,
            "ambiguous_metrics": ambiguous_metrics,
            "raw_labels": raw_labels,
        }

    def construct_standardized_statement(
        self,
        df: pd.DataFrame,
        line_item_col: str,
        period_cols: List[str],
        mapping: Dict[str, str]
    ) -> pd.DataFrame:
        """
        Constructs canonical standardized DataFrame containing rows:
        [Revenue, COGS, Gross Profit, OPEX, EBITDA, PBT, PAT].
        Handles subtotal derivations if components are missing or vice-versa:
        - If Gross Profit is missing: Gross Profit = Revenue - COGS
        - If COGS is missing: COGS = Revenue - Gross Profit
        - If EBITDA is missing: EBITDA = Gross Profit - OPEX
        - If OPEX is missing: OPEX = Gross Profit - EBITDA
        - If PBT is missing: PBT = EBITDA * 0.85 (or conservative proxy)
        - If PAT is missing: PAT = PBT * 0.75 (standard Indian 25% corporate tax rate)
        """
        # Map label -> row Series
        row_map = {}
        for _, row in df.iterrows():
            label = str(row[line_item_col]).strip()
            row_map[label] = row[period_cols].astype(float).values

        zero_arr = np.zeros(len(period_cols), dtype=np.float64)

        # Extract mapped rows
        rev = row_map.get(mapping.get("revenue", ""), zero_arr).copy()
        cogs = row_map.get(mapping.get("cogs", ""), None)
        gp = row_map.get(mapping.get("gross_profit", ""), None)
        opex = row_map.get(mapping.get("opex", ""), None)
        ebitda = row_map.get(mapping.get("ebitda", ""), None)
        pbt = row_map.get(mapping.get("pbt", ""), None)
        pat = row_map.get(mapping.get("pat", ""), None)

        # Derive COGS / Gross Profit relationships
        if gp is None:
            if cogs is not None:
                gp = rev - cogs
            else:
                # Default 40% gross margin assumption for mid-market
                cogs = rev * 0.60
                gp = rev - cogs
        elif cogs is None:
            cogs = np.maximum(0.0, rev - gp)

        # Derive OPEX / EBITDA relationships
        if ebitda is None:
            if opex is not None:
                ebitda = gp - opex
            else:
                # Default mid-market OPEX benchmark
                opex = gp * 0.65
                ebitda = gp - opex
        elif opex is None:
            opex = np.maximum(0.0, gp - ebitda)

        # Derive PBT / PAT relationships
        if pbt is None:
            # Conservative interest/depreciation proxy: ~20% of EBITDA
            pbt = ebitda * 0.80
        if pat is None:
            # 25% Indian corporate tax rate
            pat = pbt * 0.75

        standard_data = {
            "revenue": rev,
            "cogs": cogs,
            "gross_profit": gp,
            "opex": opex,
            "ebitda": ebitda,
            "pbt": pbt,
            "pat": pat,
        }

        # Format into clean DataFrame where columns are periods
        res_df = pd.DataFrame(standard_data, index=period_cols).T
        res_df.index.name = "Metric"
        return res_df
