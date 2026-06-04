from __future__ import annotations

from dataclasses import asdict
from typing import Any

from src.models import JobInput, ParsedJob


class DocumentStrategyBuilder:
    QUALITY_TARGETS = {
        "min_experience_bullets": 4,
        "max_experience_bullets": 6,
        "min_skill_groups": 4,
        "max_skill_groups": 6,
        "include_all_languages": True,
        "include_all_relevant_education": True,
    }

    ROLE_RULES = {
        "02_bi_reporting_analytics": {
            "primary_positioning": "Data Analyst BI focused on Power BI, SQL, KPI and reporting",
            "must_include": ["Power BI", "SQL", "reporting", "KPI", "Greenly", "DataForGood"],
            "guidance": "Prioritize BI reporting, dashboards, KPI logic, SQL and concrete reporting outputs.",
        },
        "04_economist_policy_analyst": {
            "primary_positioning": "junior economist with quantitative, econometric and data analysis skills",
            "must_include": [
                "Dauphine",
                "econometrics",
                "international/development economics",
                "statistical analysis",
                "writing/synthesis",
            ],
            "guidance": "Connect quantitative methods, economic analysis, policy writing and evidence synthesis.",
        },
        "09_international_organizations": {
            "primary_positioning": "internationally oriented economist and data analyst",
            "must_include": [
                "English C2",
                "Maastricht",
                "international/development economics",
                "policy analysis",
            ],
            "guidance": "Emphasize international education, English fluency, policy analysis and cross-country orientation.",
        },
        "05_climate_transition_sustainability": {
            "primary_positioning": "data analyst and economist specialized in climate transition and carbon/ESG data",
            "must_include": [
                "Greenly",
                "carbon data",
                "GHG Protocol",
                "SBTi/FLAG",
                "transition thesis",
            ],
            "guidance": "Anchor climate claims in carbon/ESG data, reporting methods and the transition thesis.",
        },
        "03_public_policy_statistics": {
            "primary_positioning": (
                "data analyst and economist focused on public statistics, indicators and public decision support"
            ),
            "must_include": [
                "DataForGood / Reclaim Finance",
                "territorial data",
                "indicators",
                "public policy analysis",
            ],
            "guidance": "Show public statistics, territorial indicators, documentation and policy support.",
        },
    }

    def build(
        self,
        job_input: JobInput,
        parsed_job: ParsedJob,
        selected_context: dict,
    ) -> dict:
        categories = selected_context.get("selected_role_categories") or parsed_job.detected_role_categories
        rules = [self.ROLE_RULES[category] for category in categories if category in self.ROLE_RULES]
        primary_rule = rules[0] if rules else {}
        primary = primary_rule.get("primary_positioning", "data analyst with quantitative and reporting skills")
        secondary = self._secondary_positioning(rules)
        must_include = self._unique(
            self._available_terms([term for rule in rules for term in rule.get("must_include", [])], selected_context)
            + self._collect_concrete_evidence(selected_context)
            + self._job_terms(parsed_job)
        )

        return {
            "primary_positioning": primary,
            "secondary_positioning": secondary,
            "recommended_cv_title": self._recommended_title(job_input, primary),
            "cv_section_priorities": self._section_priorities(categories),
            "cover_letter_argument": self._cover_letter_argument(job_input, primary),
            "must_include_evidence": must_include[:40],
            "must_avoid": [
                "unsupported seniority",
                "unsupported expert claims",
                "generic motivation",
                "manual LaTeX commands",
                "em dash characters",
            ],
            "role_specific_guidance": self._unique([rule.get("guidance", "") for rule in rules if rule.get("guidance")]),
            "quality_targets": dict(self.QUALITY_TARGETS),
            "source_summary": {
                "job_title": job_input.job_title,
                "company": job_input.company or "",
                "parsed_job": asdict(parsed_job),
            },
        }

    def _secondary_positioning(self, rules: list[dict[str, Any]]) -> str:
        if len(rules) < 2:
            return ""
        return rules[1].get("primary_positioning", "")

    def _recommended_title(self, job_input: JobInput, primary: str) -> str:
        title = job_input.job_title.strip()
        return title if title else primary[:80]

    def _section_priorities(self, categories: list[str]) -> list[str]:
        priorities = ["profile", "skills", "professional_experience"]
        if any(category in categories for category in ["04_economist_policy_analyst", "09_international_organizations"]):
            priorities.append("education")
        if any(category in categories for category in ["03_public_policy_statistics", "05_climate_transition_sustainability"]):
            priorities.append("projects")
        priorities.extend(["languages", "certifications"])
        return self._unique(priorities)

    def _cover_letter_argument(self, job_input: JobInput, primary: str) -> str:
        company = job_input.company or "the organization"
        return f"Position the application to {company} as {primary}, using concrete evidence from selected context."

    def _available_terms(self, terms: list[str], selected_context: dict) -> list[str]:
        searchable = self._searchable_text(selected_context).lower()
        available: list[str] = []
        for term in terms:
            lowered = term.lower()
            if lowered in searchable or "/" in term or "DataForGood" in term:
                available.append(term)
        return available

    def _collect_concrete_evidence(self, selected_context: dict) -> list[str]:
        evidence: list[str] = []
        for block in selected_context.get("selected_skill_blocks", []):
            evidence.extend(str(item) for item in block.get("evidence", []))
            evidence.extend(str(item) for item in block.get("keywords", []))
        for detail_key in ["selected_experience_details", "selected_project_details"]:
            for detail in selected_context.get(detail_key, []):
                evidence.extend(str(item) for item in detail.get("keywords", []))
                for values in detail.get("evidence", {}).values():
                    evidence.extend(str(value) for value in values)
                evidence.extend(str(item) for item in detail.get("achievements", []))
        return [item for item in evidence if item.strip()]

    def _job_terms(self, parsed_job: ParsedJob) -> list[str]:
        return self._unique(
            parsed_job.detected_required_skills
            + parsed_job.required_skills
            + parsed_job.detected_keywords
            + parsed_job.keywords
        )

    def _searchable_text(self, value: Any) -> str:
        if isinstance(value, dict):
            return " ".join(self._searchable_text(item) for item in value.values())
        if isinstance(value, list):
            return " ".join(self._searchable_text(item) for item in value)
        return str(value)

    def _unique(self, values: list[str]) -> list[str]:
        seen: set[str] = set()
        unique_values: list[str] = []
        for value in values:
            cleaned = " ".join(str(value).split())
            key = cleaned.lower()
            if cleaned and key not in seen:
                seen.add(key)
                unique_values.append(cleaned)
        return unique_values
