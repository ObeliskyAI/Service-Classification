# Steps to start the project

- conda create --name service

- conda activate service

- cd src

- pip install -r requirements.txt

- python main.py

- open another terminal tab and run --> cd src --> python ngrok.py

# Service Classifier

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
