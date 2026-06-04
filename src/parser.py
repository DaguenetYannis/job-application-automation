from __future__ import annotations

import re

from src.models import ParsedJob


class JobParser:
    FRENCH_MARKERS = {"vous", "nous", "poste", "competences", "candidature", "mission"}
    ENGLISH_MARKERS = {"you", "we", "role", "skills", "application", "responsibilities"}

    def parse(self, job_description: str) -> ParsedJob:
        words = self._words(job_description)
        french_count = len(words & self.FRENCH_MARKERS)
        english_count = len(words & self.ENGLISH_MARKERS)

        if french_count >= 2 and french_count > english_count:
            language = "fr"
        elif english_count >= 2 and english_count > french_count:
            language = "en"
        else:
            language = "unknown"

        return ParsedJob(language=language)

    def _words(self, text: str) -> set[str]:
        normalized = (
            text.lower()
            .replace("é", "e")
            .replace("è", "e")
            .replace("ê", "e")
            .replace("à", "a")
            .replace("ù", "u")
            .replace("ç", "c")
        )
        return set(re.findall(r"[a-z]+", normalized))
