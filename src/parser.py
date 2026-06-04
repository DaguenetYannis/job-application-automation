from __future__ import annotations

import re
import unicodedata

from src.models import ParsedJob


class JobParser:
    FRENCH_MARKERS = {
        "vous",
        "nous",
        "poste",
        "competences",
        "candidature",
        "mission",
        "missions",
        "responsabilites",
        "donnees",
        "etudes",
    }
    ENGLISH_MARKERS = {"you", "we", "role", "skills", "application", "responsibilities"}
    ROLE_KEYWORDS = {
        "01_data_analyst": [
            "data analyst",
            "analyse de donnees",
            "data analysis",
            "sql",
            "python",
            "pandas",
            "data cleaning",
            "nettoyage",
            "donnees",
            "dataset",
            "etl",
            "kpi",
        ],
        "02_bi_reporting_analytics": [
            "power bi",
            "business intelligence",
            "bi",
            "dashboard",
            "tableau de bord",
            "reporting",
            "kpi",
            "power query",
            "dax",
            "data model",
            "modele de donnees",
            "visualisation",
            "pilotage",
        ],
        "03_public_policy_statistics": [
            "statistiques publiques",
            "charge d'etudes",
            "ministere",
            "dares",
            "depp",
            "insee",
            "ssm",
            "action publique",
            "politiques publiques",
            "indicateurs",
            "territoire",
            "territorial",
            "donnees territoriales",
            "evaluation",
        ],
        "04_economist_policy_analyst": [
            "economiste",
            "economist",
            "policy analyst",
            "analyse economique",
            "economic analysis",
            "econometrie",
            "econometrics",
            "evaluation des politiques publiques",
            "public policy",
            "note d'analyse",
            "synthese",
        ],
        "05_climate_transition_sustainability": [
            "climat",
            "climate",
            "sustainability",
            "esg",
            "carbone",
            "carbon",
            "emissions",
            "ghg",
            "sbti",
            "beges",
            "transition ecologique",
            "decarbonation",
            "adaptation",
            "biodiversite",
        ],
        "06_industrial_policy_competition": [
            "politique industrielle",
            "industrial policy",
            "concurrence",
            "competition",
            "regulation",
            "marche",
            "market analysis",
            "competitivite",
            "cbam",
            "macf",
            "ets",
            "chaines de valeur",
            "value chains",
        ],
        "07_research_data_science": [
            "recherche",
            "research",
            "research assistant",
            "ingenieur de recherche",
            "data science",
            "machine learning",
            "ml",
            "statistiques",
            "scientific programming",
            "reproductibilite",
            "reproducibility",
            "python",
            "r",
        ],
        "08_public_sector_consulting": [
            "conseil",
            "consulting",
            "secteur public",
            "public sector",
            "transformation publique",
            "accompagnement",
            "diagnostic",
            "recommandations",
            "parties prenantes",
            "stakeholder",
            "conduite du changement",
            "performance",
        ],
        "09_international_organizations": [
            "oecd",
            "ocde",
            "world bank",
            "european union",
            "international organization",
            "organisation internationale",
            "developpement",
            "development",
            "cross-country",
            "survey",
            "policy analyst",
            "english",
            "anglais",
        ],
    }
    REQUIRED_SKILLS = [
        "SQL",
        "Python",
        "R",
        "Power BI",
        "Power Query",
        "DAX",
        "Excel",
        "Tableau",
        "Stata",
        "Git",
        "Machine Learning",
        "Econometrics",
        "Data cleaning",
        "ETL",
        "KPI",
        "Reporting",
        "GHG Protocol",
        "SBTi",
        "BigQuery",
        "PostgreSQL",
        "DuckDB",
    ]
    MISSION_MARKERS = [
        "mission",
        "missions",
        "responsabilites",
        "responsibilities",
        "vous serez charge",
        "you will",
        "contribute",
        "contribuer",
        "produire",
        "build",
        "develop",
    ]

    def parse(self, job_description: str) -> ParsedJob:
        normalized_text = self._normalize(job_description)
        words = set(re.findall(r"[a-z]+", normalized_text))
        french_count = len(words & self.FRENCH_MARKERS)
        english_count = len(words & self.ENGLISH_MARKERS)

        if french_count >= 2 and french_count > english_count:
            language = "fr"
        elif english_count >= 2 and english_count > french_count:
            language = "en"
        else:
            language = "unknown"

        category_scores, detected_keywords = self._detect_categories(normalized_text)
        detected_role_categories = self._select_categories(category_scores, language)
        detected_required_skills = self._detect_required_skills(normalized_text)
        detected_main_missions = self._extract_missions(job_description)

        return ParsedJob(
            language=language,
            job_family=detected_role_categories,
            required_skills=detected_required_skills,
            main_missions=detected_main_missions,
            keywords=detected_keywords,
            detected_role_categories=detected_role_categories,
            detected_keywords=detected_keywords,
            detected_required_skills=detected_required_skills,
            detected_main_missions=detected_main_missions,
        )

    def _words(self, text: str) -> set[str]:
        return set(re.findall(r"[a-z]+", self._normalize(text)))

    def _normalize(self, text: str) -> str:
        replacements = {
            "Ã©": "e",
            "Ã¨": "e",
            "Ãª": "e",
            "Ã ": "a",
            "Ã¹": "u",
            "Ã§": "c",
            "é": "e",
            "è": "e",
            "ê": "e",
            "à": "a",
            "ù": "u",
            "ç": "c",
            "î": "i",
            "ï": "i",
            "ô": "o",
        }
        lowered = text.lower()
        for source, target in replacements.items():
            lowered = lowered.replace(source, target)
        normalized = unicodedata.normalize("NFKD", lowered)
        return normalized.encode("ascii", "ignore").decode("ascii")

    def _detect_categories(self, normalized_text: str) -> tuple[dict[str, int], list[str]]:
        scores: dict[str, int] = {}
        matches: set[str] = set()
        for category_id, keywords in self.ROLE_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                normalized_keyword = self._normalize(keyword)
                if self._contains_keyword(normalized_text, normalized_keyword):
                    score += 1
                    matches.add(keyword)
            scores[category_id] = score
        return scores, sorted(matches, key=str.lower)

    def _select_categories(self, scores: dict[str, int], language: str) -> list[str]:
        selected = [
            category_id
            for category_id, score in sorted(scores.items(), key=lambda item: (-item[1], item[0]))
            if score >= 2
        ][:3]
        if selected:
            return selected
        if language == "en" and scores.get("09_international_organizations", 0) > 0:
            return ["09_international_organizations"]
        return ["01_data_analyst"]

    def _detect_required_skills(self, normalized_text: str) -> list[str]:
        found = []
        for skill in self.REQUIRED_SKILLS:
            if self._contains_keyword(normalized_text, self._normalize(skill)):
                found.append(skill)
        return sorted(dict.fromkeys(found), key=str.lower)

    def _extract_missions(self, text: str) -> list[str]:
        candidates = re.split(r"[\n.;•]+", text)
        missions = []
        for candidate in candidates:
            cleaned = " ".join(candidate.strip().split())
            if not cleaned:
                continue
            normalized = self._normalize(cleaned)
            if any(marker in normalized for marker in self.MISSION_MARKERS):
                missions.append(cleaned)
            if len(missions) >= 8:
                break
        return missions

    def _contains_keyword(self, normalized_text: str, normalized_keyword: str) -> bool:
        if len(normalized_keyword) <= 2:
            pattern = rf"(?<![a-z0-9]){re.escape(normalized_keyword)}(?![a-z0-9])"
            return bool(re.search(pattern, normalized_text))
        return normalized_keyword in normalized_text
