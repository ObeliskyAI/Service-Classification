"""
return only one benfit
"""


# from controllers.BaseController import BaseController
# from rapidfuzz import fuzz
# import re


# class BenfitsController(BaseController):

#     COMBINED_BENEFIT = "(Critical - Chronic - Pre-Existing)"
#     OPTICAL_TARGET = "optical"

#     # regex patterns for combined benfit (Critical - Chronic - Pre-Existing)
#     COMBINED_PATTERNS = {
#         "critical": r'\bcrit',          # critical, critcal, crit, criticle
#         "chronic": r'\bchron',          # chronic, cronic-ish, chron
#         "pre_existing": r'\bpre\s?e?x', # pre-ex, preex, prexisting, pre-existing
#     }


#     # regex patterns for optical sub names (eyes, glasses, lens, laisk, prescription, vision, sight)
#     OPTICAL_PATTERN = (
#         r'\b(optical|optic|optics|optician|optometr\w*|ophthalm\w*|'
#         r'eyes?|eyeglass\w*|glasses|spectacles?|lens|lenses|'
#         r'lasik|cataract\w*|glaucoma|retina\w*|sight|vision|prescription )\b'
#     )

#     # aliases
#     BENEFIT_ALIASES = {
#         OPTICAL_PATTERN: OPTICAL_TARGET,
#         r'\bpre\s?e?x': "Pre-Existing",
#     }

#     RISK_ALIASES = {
#         OPTICAL_PATTERN: OPTICAL_TARGET,
#         r'\bpre\s?e?x': "Pre-Existing",
#         r'\bpregnan': "Prengnancy",
#         r'\bmatern': "maternity",
#     }





#     def __init__(self):
#         super().__init__()

#     def fuzzy_score(self, text: str, keywords: list):
#         if not text:
#             return 0

#         text = str(text).lower().strip()
#         best_score = 0

#         for keyword in keywords:
#             keyword = str(keyword).lower().strip()

#             if not keyword:
#                 continue

#             if keyword in text:
#                 score = 100
#             else:
#                 score = fuzz.partial_ratio(keyword, text)

#             if score > best_score:
#                 best_score = score

#         return best_score

#     def split_drc_code(self, drc_code: str):
#         """
#         Split DRC code based on special chars

#         Example:
#             GDRC-7988: Chronic Cases , Critical Cases and
#             Pre-existing Cases covered up to annual ceiling

#         Returns:
#             [
#                 "GDRC-7988",
#                 "Chronic Cases",
#                 "Critical Cases",
#                 "Pre-existing Cases covered up to annual ceiling"
#             ]
#         """

#         if not drc_code:
#             return []

#         text = str(drc_code).strip() # remove extra white spaces

#         # Split by :,;
#         parts = re.split(r'[:,;]', text)

#         final_parts = []

#         for part in parts:
#             part = part.strip()

#             if not part:
#                 continue

#             # Split by "and"
#             sub_parts = re.split(
#                 r'\s+and\s+',
#                 part,
#                 flags=re.IGNORECASE
#             )

#             for sub_part in sub_parts:
#                 sub_part = sub_part.strip()

#                 if sub_part:
#                     final_parts.append(sub_part)

#         return final_parts


#     @staticmethod
#     def _normalize(text: str) -> str:
#         """lowercase + treat hyphens/underscores/multiple spaces as one space"""
#         return re.sub(r'[-_\s]+', ' ', str(text).lower()).strip()


#     def _find_best(self, text: str, keywords: list, aliases: dict, threshold: int):
#         """
#         Shared matcher. Returns (name, score) for the ONE best match,
#         or (None, 0) if nothing reaches the threshold.

#         1. Critical + Chronic + Pre-Existing all present -> combined benefit
#         2. Regex aliases
#         3. Fuzzy keyword matching (combined keyword is skipped here)
#         priority: highest score, then earliest in text, then longest keyword.
#         """
#         if not text:
#             return None, 0

#         text_norm = self._normalize(text)

#         # ---------- Rule 1: all 3 keywords must be present (Critical - Chronic - Pre-Existing)----------
#         if all(
#             re.search(p, text_norm)
#             for p in self.COMBINED_PATTERNS.values()
#         ):
#             return self.COMBINED_BENEFIT, 100

#         sections = self.split_drc_code(text)
#         candidates = []  # (name, score, position_in_text)

#         # ---------- Rule 2: aliases ----------
#         for pattern, target in aliases.items():
#             m = re.search(pattern, text_norm)
#             if m:
#                 candidates.append((target, 100, m.start()))

#         # ---------- Rule 3: keyword matching ----------
#         for keyword in keywords:

#             # combined keyword is only produced by Rule 1
#             if str(keyword).strip() == self.COMBINED_BENEFIT:
#                 continue

#             keyword_clean = self._normalize(keyword)
#             if not keyword_clean:
#                 continue

#             best_score = 0
#             for section in sections:
#                 section_clean = self._normalize(section)
#                 if not section_clean:
#                     continue

#                 if keyword_clean in section_clean:
#                     score = 100
#                 else:
#                     score = fuzz.partial_ratio(keyword_clean, section_clean)

#                 best_score = max(best_score, score)

#             if best_score >= threshold:
#                 pos = text_norm.find(keyword_clean)
#                 candidates.append(
#                     (keyword, best_score, pos if pos >= 0 else len(text_norm))
#                 )

#         if not candidates:
#             return None, 0

#         candidates.sort(key=lambda c: (-c[1], c[2], -len(str(c[0]))))
#         # print("ahooo: ",candidates[0])
#         name, score, _ = candidates[0]

#         # any eye-related keyword from the lists -> the optical target
#         if re.search(self.OPTICAL_PATTERN, self._normalize(name)):
#             name = self.OPTICAL_TARGET

#         return name, score




#     def risk_match(self, text: str, threshold: int = 80):
#         return self._find_best(
#             text,
#             self.get_risk_keywords(),
#             self.RISK_ALIASES,
#             threshold,
#         )




#     def benefit_match(self, text: str, threshold: int = 70):

#         name, _ = self._find_best(
#             text,
#             self.get_benfits_keywords(),
#             self.BENEFIT_ALIASES,
#             threshold,
#         )
#         return name




#     def orchestrator(
#         self,
#         drc_code: str,
#         exception_threshold: int = 100,
#         risk_threshold: int = 100,
#         benefit_threshold: int = 70,
#     ):
#         """
#         Full DRC decision flow:

#         1. Check if DRC contains an Exception keyword.
#         2. If YES -> look for matching risk.
#         3. If NO  -> look for matching benefits.

#         Returns:

#             Empty DRC:
#             {
#                 "is_exception": False,
#                 "benfit_name": "None"
#             }

#             Exception + risk:
#             {
#                 "is_exception": True,
#                 "risk_name": "<name>"
#             }

#             Exception without risk:
#             {
#                 "is_exception": True,
#                 "risk_name": "None"
#             }

#             Benefits found:
#             {
#                 "is_exception": False,
#                 "benfit_name": ["<name1>", "<name2>"]
#             }

#             No benefits:
#             {
#                 "is_exception": False,
#                 "benfit_name": "None"
#             }
#         """

#         if not drc_code:
#             return {
#                 "is_exception": False,
#                 "benfit_name": "None"
#             }

#         # Check for exception keyword
#         exception_score = self.fuzzy_score(
#             drc_code,
#             self.get_exception_keywords()
#         )


#         #case 1: Exception found -> check risk
  
#         if exception_score >= exception_threshold:

#             risk_name, risk_score = self.risk_match(
#                 drc_code,
#                 threshold=risk_threshold
#             )

#             if risk_name:
#                 return {
#                     "is_exception": True,
#                     "risk_name": risk_name
#                 }

#             return {
#                 "is_exception": True,
#                 "risk_name": "None"
#             }

#         # case 2: No exception -> check benefits
       

#         benefit = self.benefit_match(
#             drc_code,
#             threshold=benefit_threshold
#         )

#         return {
#             "is_exception": False,
#             "benfit_name": benefit if benefit else "None"
#         }











"""
return all  matched benfits
"""



from controllers.BaseController import BaseController
import re


class BenfitsController(BaseController):

    COMBINED_BENEFIT = "(Critical - Chronic - Pre-Existing)"
    OPTICAL_TARGET = "optical"

    # all three must appear in the DRC text to produce the combined benefit
    COMBINED_PATTERNS = {
        "critical": r'\bcrit',            # critical, critcal, crit, criticle
        "chronic": r'\bchron',            # chronic, chron
        "pre_existing": r'\bpre\s?e?x',   # pre-ex, preex, prexisting, pre-existing
    }

    # eye-related words -> optical
    OPTICAL_PATTERN = (
        r'\b(optical|optic|optics|optician|optometr\w*|ophthalm\w*|'
        r'eyes?|eyeglass\w*|glasses|spectacles?|lens|lenses|'
        r'lasik|cataract\w*|glaucoma|retina\w*|sight|vision|prescription)\b'
    )

    # regex per keyword, key = self._normalize(keyword)
    KEYWORD_PATTERNS = {
        "dental":         r'\b(dent\w*|teeth|tooth|orthodont\w*)\b',
        "covid 19":       r'\b(covid|corona(virus)?|sars)\b',
        "critical cases": r'\bcrit\w*',
        "chronic":        r'\bchron\w*',
        "pre existing":   r'\bpre\s?e?x\w*',
        "autoimmune":     r'\bauto\s?immun\w*',
        "maternity":      r'\b(matern\w*|pregnan\w*|obstetric\w*|childbirth|deliver(y|ies))\b',
        "genetic":        r'\b(gene?tic\w*|hereditar\w*|genom\w*)\b',
        "congenital":     r'\b(congenit\w*|birth defect\w*)\b',
        "laser":          r'\blaser\w*',
        "immune":         r'\bimmun\w*',
    }

    # aliases: regex -> name to return (checked before keywords)
    BENEFIT_ALIASES = {
        OPTICAL_PATTERN: OPTICAL_TARGET,
        r'\bpre\s?e?x': "Pre-Existing",
    }

    # regex per RISK keyword, key = self._normalize(keyword)
    # (reuses the benefit patterns and adds the risk-only ones)
    RISK_PATTERNS = {
        **KEYWORD_PATTERNS,
        "covid 19":               r'\b(covid|corona(virus)?|sars)\b',
        "prengnancy":             r'\bpr[ea]?n?gn?an\w*',                  # pregnancy, pregnant, prengnancy
        "maternity":              r'\b(matern\w*|obstetric\w*|childbirth|deliver(y|ies))\b',  # no pregnan* (own risk)
        "over celling":           r'\b(over|above|exceed\w*)\s(the\s)?(annual\s)?ce(i|e)?l+\w*',
        "epilepsy cases":         r'\b(epilep\w*|seizure\w*|convuls\w*)\b',
        "laboratory & radiology": r'\b(lab|labs|laborator\w*|radiolog\w*|x ?rays?|imaging|mri)\b',
        "clinic supplies":        r'\b(clinic\w*|medical)\s(suppl\w*|consumable\w*)|\bconsumable\w*',
        # "risk1" has no entry -> falls back to a literal whole-word match
        # optical keywords (glasses, lasik, sight & optical, prescription glasses)
        # are handled by OPTICAL_PATTERN -> "optical"
    }

    RISK_ALIASES = {
        OPTICAL_PATTERN: OPTICAL_TARGET,
        r'\bpre\s?e?x': "Pre-Existing",
    }

    def __init__(self):
        super().__init__()

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _normalize(text: str) -> str:
        """lowercase + treat hyphens/underscores/multiple spaces as one space"""
        return re.sub(r'[-_\s]+', ' ', str(text).lower()).strip()

    def split_drc_code(self, drc_code: str):
        """
        Split DRC code into small sections by : , ; & and the word "and".

        "GDRC-7988: Chronic Cases , Critical Cases and Pre-existing Cases"
        -> ["GDRC-7988", "Chronic Cases", "Critical Cases", "Pre-existing Cases"]
        """
        if not drc_code:
            return []

        sections = []
        for part in re.split(r'[:,;&]', str(drc_code).strip()):
            for sub_part in re.split(r'\s+and\s+', part, flags=re.IGNORECASE):
                sub_part = sub_part.strip()
                if sub_part:
                    sections.append(sub_part)
        return sections

    def _has_combined(self, text_norm: str) -> bool:
        return all(re.search(p, text_norm) for p in self.COMBINED_PATTERNS.values())

    def _has_combined_part(self, text_norm: str) -> bool:
        return any(re.search(p, text_norm) for p in self.COMBINED_PATTERNS.values())

    def _keyword_pattern(self, keyword: str, patterns: dict):
        """
        Regex for a keyword: the custom one from `patterns` if it exists,
        otherwise a literal word-boundary match on the keyword itself.
        """
        norm = self._normalize(keyword)
        if not norm:
            return None
        return patterns.get(norm, r'\b' + re.escape(norm) + r's?\b')

    def _pattern_match(self, keyword: str, text_norm: str, patterns: dict) -> bool:
        """True if the keyword's regex matches the normalized text."""
        if str(keyword).strip() == self.COMBINED_BENEFIT:
            return self._has_combined(text_norm)

        # any eye-related keyword is detected by the optical pattern
        if re.search(self.OPTICAL_PATTERN, self._normalize(keyword)):
            return bool(re.search(self.OPTICAL_PATTERN, text_norm))

        pattern = self._keyword_pattern(keyword, patterns)
        return bool(pattern and re.search(pattern, text_norm))

    def _match_section(self, section_norm: str, keywords: list, patterns: dict):
        """All keywords matching one section, dropping ones contained in a longer match."""
        matches = [kw for kw in keywords if self._pattern_match(kw, section_norm, patterns)]

        return [
            kw for kw in matches
            if not any(
                self._normalize(kw) != self._normalize(other)
                and self._normalize(kw) in self._normalize(other)
                for other in matches
            )
        ]

    def _find_all(self, text: str, keywords: list, aliases: dict, patterns: dict):
        """
        Regex-only matcher. Returns a list of ALL matched names (no duplicates),
        in the order they appear in the text.

        1. Critical + Chronic + Pre-Existing all present -> combined benefit
        2. Per section: regex aliases (optical, pre-existing, ...)
        3. Per section: keyword regex patterns
        """
        if not text:
            return []

        found = {}

        def add(name):
            found.setdefault(self._normalize(name), name)

        text_norm = self._normalize(text)

        # ---------- Rule 1: combined ----------
        combined = self._has_combined(text_norm)
        if combined:
            add(self.COMBINED_BENEFIT)

        keywords = [k for k in keywords if str(k).strip() != self.COMBINED_BENEFIT]

        for section in self.split_drc_code(text_norm):
            section_norm = self._normalize(section)

            # already covered by the combined benefit
            if combined and self._has_combined_part(section_norm):
                continue

            # ---------- Rule 2: aliases ----------
            alias_hit = False
            for pattern, target in aliases.items():
                if re.search(pattern, section_norm):
                    add(target)
                    alias_hit = True
            if alias_hit:
                continue

            # ---------- Rule 3: keyword patterns ----------
            for kw in self._match_section(section_norm, keywords, patterns):
                # any eye-related keyword -> optical target
                if re.search(self.OPTICAL_PATTERN, self._normalize(kw)):
                    add(self.OPTICAL_TARGET)
                else:
                    add(kw)

        return list(found.values())

    def has_exception(self, text: str) -> bool:
        """True if any exception keyword appears in the text (plain substring)."""
        text_norm = self._normalize(text)
        for kw in self.get_exception_keywords():
            kw_norm = self._normalize(kw)
            if kw_norm and kw_norm in text_norm:
                return True
        return False

    # ------------------------------------------------------------------
    # public matchers
    # ------------------------------------------------------------------
    def risk_match(self, text: str):
        """Returns a list of ALL matching risk names (empty list if none)."""
        return self._find_all(
            text,
            self.get_risk_keywords(),
            self.RISK_ALIASES,
            self.RISK_PATTERNS,
        )

    def benefit_match(self, text: str):
        """Returns a list of all matching benefit names (empty list if none)."""
        return self._find_all(
            text,
            self.get_benfits_keywords(),
            self.BENEFIT_ALIASES,
            self.KEYWORD_PATTERNS,
        )

    def orchestrator(self, drc_code: str):
        """
        Full DRC decision flow:

        1. Check if DRC contains an Exception keyword.
        2. If YES -> look for matching risk.
        3. If NO  -> look for matching benefits.

        Returns:
            Empty DRC / no benefits : {"is_exception": False, "benfit_name": "None"}
            Exception + risks       : {"is_exception": True,  "risk_name": ["<name1>", ...]}
            Exception without risk  : {"is_exception": True,  "risk_name": "None"}
            Benefits found          : {"is_exception": False, "benfit_name": ["<name1>", ...]}
        """
        if not drc_code:
            return {"is_exception": False, "benfit_name": "None"}

        # case 1: exception found -> check risk
        if self.has_exception(drc_code):
            risks = self.risk_match(drc_code)
            return {
                "is_exception": True,
                "risk_name": risks if risks else "None",
            }

        # case 2: no exception -> check benefits
        benefits = self.benefit_match(drc_code)
        return {
            "is_exception": False,
            "benfit_name": benefits if benefits else "None",
        }