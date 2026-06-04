from __future__ import annotations

import re
import unicodedata


class Slugifier:
    @staticmethod
    def slugify(text: str) -> str:
        normalized = unicodedata.normalize("NFKD", text)
        ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
        lowercase = ascii_text.lower()
        replaced = re.sub(r"[^a-z0-9]+", "-", lowercase)
        collapsed = re.sub(r"-+", "-", replaced)
        return collapsed.strip("-") or "unknown"
