from controllers.BaseController import BaseController
from rapidfuzz import fuzz
import re


class BenfitsController(BaseController):

    COMBINED_BENEFIT = "(Critical - Chronic - Pre-Existing)"
    OPTICAL_TARGET = "optical"

    # regex patterns for combined benfit (Critical - Chronic - Pre-Existing)
    COMBINED_PATTERNS = {
        "critical": r'\bcrit',          # critical, critcal, crit, criticle
        "chronic": r'\bchron',          # chronic, cronic-ish, chron
        "pre_existing": r'\bpre\s?e?x', # pre-ex, preex, prexisting, pre-existing
    }


    # regex patterns for optical sub names (eyes, glasses, lens, laisk, prescription, vision, sight)
    OPTICAL_PATTERN = (
        r'\b(optical|optic|optics|optician|optometr\w*|ophthalm\w*|'
        r'eyes?|eyeglass\w*|glasses|spectacles?|lens|lenses|'
        r'lasik|cataract\w*|glaucoma|retina\w*|sight|vision|prescription )\b'
    )

    # aliases
    BENEFIT_ALIASES = {
        OPTICAL_PATTERN: OPTICAL_TARGET,
        r'\bpre\s?e?x': "Pre-Existing",
    }

    RISK_ALIASES = {
        OPTICAL_PATTERN: OPTICAL_TARGET,
        r'\bpre\s?e?x': "Pre-Existing",
        r'\bpregnan': "Prengnancy",
        r'\bmatern': "maternity",
    }





    def __init__(self):
        super().__init__()

    def fuzzy_score(self, text: str, keywords: list):
        if not text:
            return 0

        text = str(text).lower().strip()
        best_score = 0

        for keyword in keywords:
            keyword = str(keyword).lower().strip()

            if not keyword:
                continue

            if keyword in text:
                score = 100
            else:
                score = fuzz.partial_ratio(keyword, text)

            if score > best_score:
                best_score = score

        return best_score

    def split_drc_code(self, drc_code: str):
        """
        Split DRC code based on special chars

        Example:
            GDRC-7988: Chronic Cases , Critical Cases and
            Pre-existing Cases covered up to annual ceiling

        Returns:
            [
                "GDRC-7988",
                "Chronic Cases",
                "Critical Cases",
                "Pre-existing Cases covered up to annual ceiling"
            ]
        """

        if not drc_code:
            return []

        text = str(drc_code).strip() # remove extra white spaces

        # Split by :,;
        parts = re.split(r'[:,;]', text)

        final_parts = []

        for part in parts:
            part = part.strip()

            if not part:
                continue

            # Split by "and"
            sub_parts = re.split(
                r'\s+and\s+',
                part,
                flags=re.IGNORECASE
            )

            for sub_part in sub_parts:
                sub_part = sub_part.strip()

                if sub_part:
                    final_parts.append(sub_part)

        return final_parts


    @staticmethod
    def _normalize(text: str) -> str:
        """lowercase + treat hyphens/underscores/multiple spaces as one space"""
        return re.sub(r'[-_\s]+', ' ', str(text).lower()).strip()


    def _find_best(self, text: str, keywords: list, aliases: dict, threshold: int):
        """
        Shared matcher. Returns (name, score) for the ONE best match,
        or (None, 0) if nothing reaches the threshold.

        1. Critical + Chronic + Pre-Existing all present -> combined benefit
        2. Regex aliases
        3. Fuzzy keyword matching (combined keyword is skipped here)
        priority: highest score, then earliest in text, then longest keyword.
        """
        if not text:
            return None, 0

        text_norm = self._normalize(text)

        # ---------- Rule 1: all 3 keywords must be present (Critical - Chronic - Pre-Existing)----------
        if all(
            re.search(p, text_norm)
            for p in self.COMBINED_PATTERNS.values()
        ):
            return self.COMBINED_BENEFIT, 100

        sections = self.split_drc_code(text)
        candidates = []  # (name, score, position_in_text)

        # ---------- Rule 2: aliases ----------
        for pattern, target in aliases.items():
            m = re.search(pattern, text_norm)
            if m:
                candidates.append((target, 100, m.start()))

        # ---------- Rule 3: keyword matching ----------
        for keyword in keywords:

            # combined keyword is only produced by Rule 1
            if str(keyword).strip() == self.COMBINED_BENEFIT:
                continue

            keyword_clean = self._normalize(keyword)
            if not keyword_clean:
                continue

            best_score = 0
            for section in sections:
                section_clean = self._normalize(section)
                if not section_clean:
                    continue

                if keyword_clean in section_clean:
                    score = 100
                else:
                    score = fuzz.partial_ratio(keyword_clean, section_clean)

                best_score = max(best_score, score)

            if best_score >= threshold:
                pos = text_norm.find(keyword_clean)
                candidates.append(
                    (keyword, best_score, pos if pos >= 0 else len(text_norm))
                )

        if not candidates:
            return None, 0

        candidates.sort(key=lambda c: (-c[1], c[2], -len(str(c[0]))))
        # print("ahooo: ",candidates[0])
        name, score, _ = candidates[0]

        # any eye-related keyword from the lists -> the optical target
        if re.search(self.OPTICAL_PATTERN, self._normalize(name)):
            name = self.OPTICAL_TARGET

        return name, score




    def risk_match(self, text: str, threshold: int = 80):
        return self._find_best(
            text,
            self.get_risk_keywords(),
            self.RISK_ALIASES,
            threshold,
        )




    def benefit_match(self, text: str, threshold: int = 70):

        name, _ = self._find_best(
            text,
            self.get_benfits_keywords(),
            self.BENEFIT_ALIASES,
            threshold,
        )
        return name




    def orchestrator(
        self,
        drc_code: str,
        exception_threshold: int = 100,
        risk_threshold: int = 100,
        benefit_threshold: int = 70,
    ):
        """
        Full DRC decision flow:

        1. Check if DRC contains an Exception keyword.
        2. If YES -> look for matching risk.
        3. If NO  -> look for matching benefits.

        Returns:

            Empty DRC:
            {
                "is_exception": False,
                "benfit_name": "None"
            }

            Exception + risk:
            {
                "is_exception": True,
                "risk_name": "<name>"
            }

            Exception without risk:
            {
                "is_exception": True,
                "risk_name": "None"
            }

            Benefits found:
            {
                "is_exception": False,
                "benfit_name": ["<name1>", "<name2>"]
            }

            No benefits:
            {
                "is_exception": False,
                "benfit_name": "None"
            }
        """

        if not drc_code:
            return {
                "is_exception": False,
                "benfit_name": "None"
            }

        # Check for exception keyword
        exception_score = self.fuzzy_score(
            drc_code,
            self.get_exception_keywords()
        )


        #case 1: Exception found -> check risk
  
        if exception_score >= exception_threshold:

            risk_name, risk_score = self.risk_match(
                drc_code,
                threshold=risk_threshold
            )

            if risk_name:
                return {
                    "is_exception": True,
                    "risk_name": risk_name
                }

            return {
                "is_exception": True,
                "risk_name": "None"
            }

        # case 2: No exception -> check benefits
       

        benefit = self.benefit_match(
            drc_code,
            threshold=benefit_threshold
        )

        return {
            "is_exception": False,
            "benfit_name": benefit if benefit else "None"
        }
