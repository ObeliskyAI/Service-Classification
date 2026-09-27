# from controllers.BaseController import BaseController
# from rapidfuzz import process, fuzz


# class DirectClassifyService(BaseController):
      
#     def __init__(self):
#         super().__init__()






#     def fuzzy_contains(self, text: str, keywords: list, threshold=80):
#         if not text:
#             return False

#         text = str(text).lower().strip()

#         for keyword in keywords:
#             keyword = str(keyword).lower().strip()

#             # Exact substring match gets priority
#             if keyword in text:
#                 print(f"Exact match: '{keyword}' in '{text}'")
#                 return True

#             # Fuzzy comparison
#             score = fuzz.partial_ratio(keyword, text)

#             print(f"Keyword: '{keyword}' | Score: {score}")

#             if score >= threshold:
#                 return True

#         return False



#     def direct_classify_service(self, data:dict):


#         emergency = str(data.get("EMERGENCY", "")).strip().lower()
#         provider_name = str(data.get("Provider Name", "")).strip().lower()
#         service_description = str(
#             data.get("SERVICE DESC", "")
#         ).strip().lower()

#         # Rule 1: Explicit emergency
#         if emergency == "yes":
#             return "Emergency"

#         # Rule 2: Hospital
#         hospital_keywords = self.get_hospital_keywords()


#         # Rule 3: Laboratory
#         lab_keywords = self.get_lab_keywords()

#         if (
#             self.fuzzy_contains(service_description, lab_keywords)
#             or
#             self.fuzzy_contains(provider_name, lab_keywords)
             
#         ):
#             return "Lab"


#         # Rule 4: Radiology
#         radiology_keywords = self.get_radiology_keywords()
#         if (
#             self.fuzzy_contains(service_description, radiology_keywords)
#             or
#             self.fuzzy_contains(provider_name, radiology_keywords)
             
#         ):
#             return "Radiology"

  

#         # Rule 5: Physiotherapy
#         physiotherapy_keywords = self.get_physiotherapy_keywords()

#         if (
#             self.fuzzy_contains(service_description, physiotherapy_keywords)
#             or
#             self.fuzzy_contains(provider_name, physiotherapy_keywords)
            
            
#         ):
#             return "Physiotherapy"

#         if any(keyword in provider_name for keyword in hospital_keywords):
#           return "Emergency"

#         return "Unknown"







    











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
