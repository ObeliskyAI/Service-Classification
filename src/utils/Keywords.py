

class Keywords():

  
  def __init__(self):

    self.KEYWORDS = {
      "HOSPITAL":[
          "hospital",
          "medical hospital"
      ],
        "LABORATORY": [
            "lab",
            "laboratory",
            "CBC",
            "blood test",
            "glucose",
            "tests",
            "test"
        ],
        "RADIOLOGY": [
          "radiology",
          "x-ray",
          "mri",
          "ct",
          "ultrasound",
          "scan",
          "ultrasonography"
        ],
        "PHYSIOTHERAPY": [
          "physiotherapy",
          "physical therapy",
          "rehabilitation",
          "physio",
        ],

    
      "RISK": [
        "Risk1",
        "Glasses",
        "Over Celling",
        "Covid - 19",
        "Lasik",
        "Prengnancy",
        "Sight & Optical",
        "Epilepsy Cases",
        "Laboratory & Radiology",
        "Clinic supplies",
        "Dental",
        "Covid 19",
        "prescription glasses",
        "Critical Cases",
        "Chronic",
        "Pre-Existing",
        "(Critical - Chronic - Pre-Existing)",
        "Autoimmune",
        "maternity"
      ],

      "EXCEPTION" :
      [
        "exception",
        "exceptions"
      ],


      "BENFITS":
      [
        "Dental",
        "Covid 19",
        "prescription glasses",
        "Critical Cases",
        "Chronic",
        "Pre-Existing",
        "(Critical - Chronic - Pre-Existing)",
        "AUTOIMMUNE",
        "maternity"
    ]
}

    pass


  def get_keywords(self):
    return self.KEYWORDS


