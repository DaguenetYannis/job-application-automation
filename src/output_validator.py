from __future__ import annotations

from typing import Any


class GeneratedContentValidator:
    GENERIC_PHRASES = [
        "dynamic environment",
        "strong quantitative approach",
        "complex datasets",
        "clear and usable outputs",
        "closely aligned with my profile",
        "make a significant impact",
        "passionate about",
        "excited to apply",
        "proven track record",
    ]

    def validate(self, generated: dict, selected_context: dict, document_strategy: dict) -> list[str]:
        warnings: list[str] = []
        cv = generated.get("cv", {}) if isinstance(generated, dict) else {}
        cover_letter = generated.get("cover_letter", {}) if isinstance(generated, dict) else {}
        quality_targets = document_strategy.get("quality_targets", {})

        skill_groups = cv.get("skill_groups", []) or []
        if len(skill_groups) < int(quality_targets.get("min_skill_groups", 4)):
            warnings.append("CV has fewer than 4 skill groups.")

        experiences = cv.get("experiences", []) or []
        if len(selected_context.get("selected_experiences", [])) >= 2 and len(experiences) < 2:
            warnings.append("CV has fewer than 2 experiences while selected context had at least 2.")

        min_bullets = int(quality_targets.get("min_experience_bullets", 4))
        if experiences:
            main_bullets = experiences[0].get("bullets", []) or []
            if len(main_bullets) < min_bullets:
                warnings.append("Main experience has fewer than 4 bullets.")

        if not cv.get("education"):
            warnings.append("Education is missing.")

        profile_languages = selected_context.get("candidate_languages", []) or []
        generated_languages = cv.get("languages", "")
        if profile_languages and (not generated_languages or self._language_count(generated_languages) <= 1):
            warnings.append("Languages are missing or only one language is listed while profile has several.")

        cv_text = self._flatten_text(cv)
        selected_tools = self._selected_evidence_terms(selected_context, ["tools"])
        if selected_tools and not self._contains_any(cv_text, selected_tools):
            warnings.append("No selected concrete tools appear in CV.")

        selected_data_methods = self._selected_evidence_terms(selected_context, ["datasets", "methods"])
        if selected_data_methods and not self._contains_any(cv_text, selected_data_methods):
            warnings.append("No selected concrete datasets or methods appear in CV.")

        paragraphs = cover_letter.get("paragraphs", []) or []
        if len(paragraphs) < 4:
            warnings.append("Cover letter has fewer than 4 paragraphs.")

        company = document_strategy.get("source_summary", {}).get("company", "")
        cover_text = self._flatten_text(cover_letter)
        if company and company.lower() not in cover_text.lower():
            warnings.append("Cover letter does not mention company when company is available.")

        all_text = self._flatten_text(generated)
        for phrase in self.GENERIC_PHRASES:
            if phrase in all_text.lower():
                warnings.append(f"Cover letter or CV contains generic phrase: {phrase}.")
                break

        must_include = document_strategy.get("must_include_evidence", []) or []
        if must_include and not self._contains_any(all_text, must_include):
            warnings.append("Generated content does not include any must_include_evidence from document strategy.")

        return warnings

    def _selected_evidence_terms(self, selected_context: dict, buckets: list[str]) -> list[str]:
        terms: list[str] = []
        for detail_key in ["selected_experience_details", "selected_project_details"]:
            for detail in selected_context.get(detail_key, []):
                evidence = detail.get("evidence", {})
                for bucket in buckets:
                    terms.extend(str(item) for item in evidence.get(bucket, []))
        for block in selected_context.get("selected_skill_blocks", []):
            terms.extend(str(item) for item in block.get("keywords", []))
        return self._unique(terms)

    def _contains_any(self, text: str, terms: list[str]) -> bool:
        text_lower = text.lower()
        return any(str(term).lower() in text_lower for term in terms if str(term).strip())

    def _language_count(self, value: Any) -> int:
        if isinstance(value, list):
            return len(value)
        text = str(value)
        separators = [",", ";", "\n", "|"]
        count = 1 if text.strip() else 0
        for separator in separators:
            if separator in text:
                return len([part for part in text.split(separator) if part.strip()])
        return count

    def _flatten_text(self, value: Any) -> str:
        if isinstance(value, dict):
            return " ".join(self._flatten_text(item) for item in value.values())
        if isinstance(value, list):
            return " ".join(self._flatten_text(item) for item in value)
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
