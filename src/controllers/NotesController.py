from controllers.BaseController import BaseController
from docx import Document
import argostranslate.package
import argostranslate.translate
from rapidfuzz import fuzz
import re





class NotesController(BaseController):

    def __init__(self):
        super().__init__()

    # def extract_notes(self, file_name: str):

    #     document = Document(file_name)

    #     if not document.tables:
    #         return [
    #             paragraph.text.strip()
    #             for paragraph in document.paragraphs
    #             if paragraph.text.strip()
    #         ]

    #     last_table = document.tables[-1]
    #     last_table_element = last_table._element

    #     notes = []
    #     collect = False

    #     for element in document.element.body:

    #         if element is last_table_element:
    #             collect = True
    #             continue

    #         if collect and element.tag.endswith('}p'):
    #             text = ''.join(
    #                 node.text or ''
    #                 for node in element.iter()
    #                 if node.tag.endswith('}t')
    #             ).strip()

    #             if text:
    #                 notes.append(text)

    #     return notes

    COMBINED_BENEFIT = "(Critical - Chronic - Pre-Existing)"
    OPTICAL_TARGET = "optical"

    # all three must appear in the DRC text to produce the combined benefit
    COMBINED_PATTERNS = {
        "critical": r'\bcrit',           # critical, critcal, crit, criticle
        "chronic": r'\bchron',           # chronic, cronic-ish, chron
        "pre_existing": r'\bpre\s?e?x',  # pre-ex, preex, prexisting, pre-existing
    }

    # eye-related words -> optical
    OPTICAL_PATTERN = (
        r'\b(optical|optic|optics|optician|optometr\w*|ophthalm\w*|'
        r'eyes?|eyeglass\w*|glasses|spectacles?|lens|lenses|'
        r'lasik|cataract\w*|glaucoma|retina\w*|sight|vision|prescription)\b'
    )


        # regex per benefit keyword, key = self._normalize(keyword)
    KEYWORD_PATTERNS = {
        "dental":               r'\b(dent\w*|teeth|tooth|orthodont\w*)\b',
        "covid 19":             r'\b(covid|corona(virus)?|sars)\b',
        "critical cases":       r'\bcrit\w*',
        "chronic":              r'\bchron\w*',
        "pre existing":         r'\bpre\s?e?x\w*',
        "autoimmune":           r'\bauto\s?immun\w*',
        "maternity":            r'\b(matern\w*|pregnan\w*|obstetric\w*|childbirth|deliver(y|ies))\b',
        "genetic":              r'\b(gene?tic\w*|hereditar\w*|genom\w*)\b',
        "congenital":           r'\b(congenit\w*|birth defect\w*)\b',
        "laser":                r'\blaser\w*',
        "immune":               r'\bimmun\w*',   # immunized, immunity, immunization...,
    }


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



    def _pattern_match(self, benefit: str, text_norm: str) -> bool:
        """True if the benefit's regex pattern  matches the normalized text."""


        # normalize
        benefit_norm = self._normalize(benefit)

        # check on combined benefit: all three parts must be present
        if str(benefit).strip() == self.COMBINED_BENEFIT:
            return all(re.search(p, text_norm) for p in self.COMBINED_PATTERNS.values())

        # check on optical alias: any eye-related benefit is detected by the optical pattern
        if re.search(self.OPTICAL_PATTERN, benefit_norm):
            return bool(re.search(self.OPTICAL_PATTERN, text_norm))

        # at the end check on other keywords patterns
        pattern = self.KEYWORD_PATTERNS.get(benefit_norm)
        return bool(pattern and re.search(pattern, text_norm))


    
    def _match_section(self, section_norm: str, keywords: list):

        matches = [
            kw for kw in keywords
            if kw in section_norm or self._pattern_match(kw, section_norm)
        ]

        return [
            kw for kw in matches
            if not any(
                kw != other and kw in other
                for other in matches
            )
        ]

    
    def get_all_benefits_from_DRC_CODE(self, drc_code: str):
        if not drc_code:
            return []

        found = {}

        def add(benefit):
            found.setdefault(self._normalize(benefit), benefit)

        # Normalize the DRC code
        text = self._normalize(drc_code)

        # Check if Critical + Chronic + Pre-Existing exist together
        combined = all(
            re.search(pattern, text)
            for pattern in self.COMBINED_PATTERNS.values()
        )

        if combined:
            add(self.COMBINED_BENEFIT)

        # Get normal benefits only
        keywords = [
            self._normalize(benefit)
            for benefit in self.get_benfits_keywords()
            if benefit != self.COMBINED_BENEFIT
        ]

        # Check every DRC section
        for section in self.split_drc_code(text):

            section_norm = self._normalize(section)

            # Optical
            if re.search(self.OPTICAL_PATTERN, section_norm):
                add(self.OPTICAL_TARGET)
                continue

            # Skip Critical / Chronic / Pre-Existing
            # when they were already handled as combined
            if combined and any(
                re.search(pattern, section_norm)
                for pattern in self.COMBINED_PATTERNS.values()
            ):
                continue

            # Normal benefits
            for benefit in self._match_section(section_norm, keywords):
                add(benefit)

        return list(found.values())



    def translation(self,notes:list):

      all_translation = []
        
      argostranslate.package.update_package_index()

      packages = argostranslate.package.get_available_packages()

      package = next(
          p for p in packages
          if p.from_code == "ar" and p.to_code == "en"
      )

      argostranslate.package.install_from_path(package.download())

      for note in notes:
        
        translated = argostranslate.translate.translate(
            note,
            "ar",
            "en"
        )

        all_translation.append(translated)


        # for i in all_translation:
        #     print(i)



      return all_translation


  
    def find_benefit_matches(self, notes, benefits):
        results = []

        for note in notes:
            note_norm = self._normalize(note)
            matches = []

            for benefit in benefits:

                # Regex pattern match 
                print("benfits is : ", benefit, "note_norm is: ", note_norm)
                if self._pattern_match(benefit, note_norm):
                    print("hello2")
                    matches.append(benefit)

                # # 3. Fuzzy partial match
                # else:
                #     score = fuzz.partial_ratio(benefit_norm, note_norm)

            results.append({
                "note": note,
                "matches": matches
            })

        return results


