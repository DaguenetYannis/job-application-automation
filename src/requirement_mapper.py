from __future__ import annotations

import re
import unicodedata

from src.models import ParsedJob


class RequirementMapper:
    RULES = [
        {
            "terms": ["sql"],
            "job_requirement": "SQL",
            "candidate_evidence": [
                "Greenly BigQuery/PostgreSQL queries on carbon and ESG data",
                "DataForGood DuckDB/SQL logic on territorial fiscal data",
            ],
            "recommended_use": ["cv_skills", "cv_experience", "cover_letter"],
        },
        {
            "terms": ["python"],
            "job_requirement": "Python",
            "candidate_evidence": [
                "Greenly Python automation for Excel/CSV cleaning and standardization",
                "DataForGood reproducible Python pipelines",
            ],
            "recommended_use": ["cv_skills", "cv_experience", "cover_letter"],
        },
        {
            "terms": ["power bi", "dashboard", "dashboards", "reporting", "kpi"],
            "job_requirement": "Power BI/dashboard/reporting",
            "candidate_evidence": [
                "Power BI reporting skill block",
                "Greenly reporting materials for clients and internal teams",
                "DataForGood Power BI prototype for territorial indicators",
            ],
            "recommended_use": ["cv_skills", "cv_experience", "cover_letter"],
        },
        {
            "terms": ["econometrics", "econometrie", "statistics", "statistical analysis", "statistiques", "regression"],
            "job_requirement": "econometrics/statistics",
            "candidate_evidence": [
                "Dauphine econometrics and statistical analysis training",
                "R/Stata/econometrics skill block",
                "supervised machine learning pipeline with regression and cross-validation",
            ],
            "recommended_use": ["cv_skills", "cv_education", "cover_letter"],
        },
        {
            "terms": ["database updating", "data quality", "quality checks", "parquet", "dictionary", "dictionnaire"],
            "job_requirement": "database updating",
            "candidate_evidence": [
                "DataForGood pipeline over fiscal data",
                "variable dictionary and documentation",
                "Parquet conversion and quality checks",
            ],
            "recommended_use": ["cv_experience", "cover_letter"],
        },
        {
            "terms": ["macroeconomic", "economic analysis", "analyse economique", "development economics", "international economics"],
            "job_requirement": "macroeconomic/economic analysis",
            "candidate_evidence": [
                "Dauphine international and development economics training",
                "transition thesis on green industrial sectors",
            ],
            "recommended_use": ["cv_education", "cv_projects", "cover_letter"],
        },
        {
            "terms": ["presentation", "presentations", "reports", "report", "slides", "synthesis", "synthese"],
            "job_requirement": "presentations/reports",
            "candidate_evidence": [
                "Greenly client deliverables and reporting slides",
                "policy notes and writing synthesis",
            ],
            "recommended_use": ["cv_experience", "cover_letter"],
        },
        {
            "terms": ["international environment", "international", "english", "anglais", "cross-country"],
            "job_requirement": "international environment",
            "candidate_evidence": [
                "Maastricht University European affairs training",
                "English C2",
                "international organizations profile",
            ],
            "recommended_use": ["cv_education", "cv_languages", "cover_letter"],
        },
        {
            "terms": ["climate", "climat", "carbon", "carbone", "esg", "ghg", "sbti", "flag"],
            "job_requirement": "climate/carbon/ESG",
            "candidate_evidence": [
                "Greenly carbon data and climate reporting",
                "climate policy skill block",
                "transition thesis on green industrial sectors",
            ],
            "recommended_use": ["cv_skills", "cv_experience", "cv_projects", "cover_letter"],
        },
    ]

    def build_mapping(self, parsed_job: ParsedJob, selected_context: dict) -> list[dict]:
        searchable = self._normalize(" ".join(self._job_terms(parsed_job)))
        mappings: list[dict] = []
        for rule in self.RULES:
            if any(self._contains(searchable, self._normalize(term)) for term in rule["terms"]):
                evidence = self._filter_available_evidence(rule["candidate_evidence"], selected_context)
                mappings.append(
                    {
                        "job_requirement": rule["job_requirement"],
                        "candidate_evidence": evidence,
                        "recommended_use": list(rule["recommended_use"]),
                    }
                )
        return mappings

    def _job_terms(self, parsed_job: ParsedJob) -> list[str]:
        return (
            parsed_job.required_skills
            + parsed_job.preferred_skills
            + parsed_job.main_missions
            + parsed_job.keywords
            + parsed_job.detected_required_skills
            + parsed_job.detected_keywords
            + parsed_job.detected_main_missions
        )

    def _filter_available_evidence(self, evidence_items: list[str], selected_context: dict) -> list[str]:
        context_text = self._normalize(self._context_text(selected_context))
        available: list[str] = []
        for item in evidence_items:
            item_text = self._normalize(item)
            tokens = [token for token in re.findall(r"[a-z0-9]+", item_text) if len(token) > 3]
            if not tokens or any(token in context_text for token in tokens[:3]):
                available.append(item)
            else:
                available.append(item)
        return available

    def _context_text(self, value: object) -> str:
        if isinstance(value, dict):
            return " ".join(self._context_text(item) for item in value.values())
        if isinstance(value, list):
            return " ".join(self._context_text(item) for item in value)
        return str(value)

    def _contains(self, text: str, term: str) -> bool:
        if len(term) <= 2:
            return bool(re.search(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", text))
        return term in text

    def _normalize(self, text: str) -> str:
        normalized = unicodedata.normalize("NFKD", str(text).lower())
        return normalized.encode("ascii", "ignore").decode("ascii")
