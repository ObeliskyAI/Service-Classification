from controllers.BaseController import BaseController
from rapidfuzz import fuzz


class DirectClassifyService(BaseController):

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

    def score_categories(self, text: str, category_keywords: dict):
        return {
            category: self.fuzzy_score(text, keywords)
            for category, keywords in category_keywords.items()
        }

    def direct_classify_service(self, data: dict, threshold=80):

        emergency = str(data.get("EMERGENCY", "")).strip().lower()
        provider_name = str(data.get("Provider Name", "")).strip().lower()
        service_description = str(data.get("SERVICE DESC", "")).strip().lower()

        # Rule 1: Explicit emergency
        if emergency == "yes":
            return "Emergency"

        hospital_keywords = self.get_hospital_keywords()

        category_keywords = {
            "Lab": self.get_lab_keywords(),
            "Radiology": self.get_radiology_keywords(),
            "Physiotherapy": self.get_physiotherapy_keywords(),
        }

        # Step 1: Try service description first
        desc_scores = self.score_categories(service_description, category_keywords)
        print(f"Description scores: {desc_scores}")

        best_desc_category = max(desc_scores, key=desc_scores.get)
        best_desc_score = desc_scores[best_desc_category]

        if best_desc_score >= threshold:
            return best_desc_category

        # Step 2: Fall back to provider name only if description gave no match
        provider_scores = self.score_categories(provider_name, category_keywords)
        print(f"Provider name scores: {provider_scores}")

        best_provider_category = max(provider_scores, key=provider_scores.get)
        best_provider_score = provider_scores[best_provider_category]

        if best_provider_score >= threshold:
            return best_provider_category

        # Step 3: Hospital fallback
        if any(keyword in provider_name for keyword in hospital_keywords):
            return "Emergency"

        return "Unknown"
