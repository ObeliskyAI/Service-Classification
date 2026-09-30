# Wethaq Medical Services

### Steps to start the project

- conda create --name service

- conda activate service

- cd src

- pip install -r requirements.txt

- python main.py

- open another terminal tab and run --> cd src --> python ngrok.py

### Classfication service

- in this task we want to classify the patient Ambulatory services to fixed categoris
  1- LAB
  2- Physiotherapy
  3- Emergency
  4- Radiology

- How to know this?

  We have some rules first we should look at the Emergency column if it is "YES" then this service is "Emergency"

  if "NO" then look at the Service Desc column and check if it has any keyword belongs to LAB, Radiology or Physotherapy

  if Service Desc hasn't useful information look at the provider name and check if it is "Hospital" then this service is "Emergency"

  if the provider name is a name of lab cenetr or radiology center or physotherapy center then pass it to it's category

- We have two solutions to do that:

  1- using the direct keyword search and this is a strict rules with fuzzy match algorithm

  2- using agent to know the category and feed it with a prompt have those rules and some keywords and make the agent know the other keywords related to this task

### Benfits Classfier Service

from the DRC code column if i found:

1. Exception Keyword ==> then I should return exception and check if beside the word exception smth related to risk English names

   and if i found a risk name return { is_exception: True , risk_name: ""}

   if not found a risk name return { is_exception: True , risk_name: "None"}

2. No Exception Keyword ==> the i will compare the DRC column with the benfits English name

   if found matching return { is_exception: False , benfit_name : []}

   if no matching return { is_exception: False , benfit_name : "None"}

How i made that?

- i split the drc_code by special characters beacuse the drc code sometimes be a large string and also if i split it by white spaces(word by word) it will take to much time in check

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

- i will take the sub string from drc code and check it with my all Benfits keywords and if there is a match i will return this keyword and same thing with exception and risk

- then i have 3 stages to find the benfit ==>
  1. all 3 keywords must be present (Critical - Chronic - Pre-Existing)
  2. check the keywords aliases
  3. normal keyword matching

  at the end i have a candidate list that have all the matched benfits from the above 3 stages, then i will sort candidate by score and i will return only one benfit

### Notes Classfier Service

the notes router will take two inputs drc_code, list of notes

first i get the benfits from drc_code then i will search using those benfits words inside every note in the Notes

and if i found match i will return this benfit keyword

how i do this?

- first i made a regex(pattern) for every benfit keyword and use re.search(pattern, note) and if found any pattern match return it's benfit name

this is more powerful than using fuzzy match
