**Proof of Concept (PoC) to connect to a commercial LLM via API with Python and do some tasks**

The notebook API_Gemini.ipynb sends simple queries to each of the five (5) available Google Gemini models and prints the different answers. 
It measures how long each query takes for each model.
You can observe that it takes as long for one (1) query than for a batch of five (5) queries.

The code in What's_up_for_the_week.py selects randomly one (1) of the four (4) office locations of a specific software company and then:
1. connects to a weather API and plots the weather forecast for the next 4 days (temperature, likelihood of precipitations and how much in hourly mm)
2. connects to a Google Gemini model, browses the web, and prints two (2) activities to do close to such office location during the next three (3) days.