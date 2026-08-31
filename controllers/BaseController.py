from helpers.config import get_settings, Settings
from utils.Keywords import Keywords
import os
import random
import string

class BaseController:
    
    def __init__(self):

        self.app_settings = get_settings()

        self.keywords = Keywords()

        self.keywords_dict = self.keywords.get_keywords()

    def get_hospital_keywords(self):

      return self.keywords_dict["HOSPITAL"]
    
    def get_lab_keywords(self):
      return self.keywords_dict["LABORATORY"]

    def get_radiology_keywords(self):
      return self.keywords_dict["RADIOLOGY"]

    def get_physiotherapy_keywords(self):
      return self.keywords_dict["PHYSIOTHERAPY"]


