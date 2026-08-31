

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
        ]
    }

    pass


  def get_keywords(self):
    return self.KEYWORDS


