import pandas as pd
import requests
import time

birds_dataframe = pd.read_csv("../config/texas_birds.csv")

def get_taxon_id_by_name(species_name):
  url = "https://api.inaturalist.org/v1/taxa"
  params = {
    "q" : species_name,
    "rank" : "species",
    "per_page" : 1
  }
  response = requests.get(url, params=params)

  if response.status_code == 200:
    results = response.json()["results"]
    if results:
      return results[0]["id"]
  else:
    print("Error:", response.status_code)

taxon_ids = []

for bird in birds_dataframe["bird_name"]:
  print(f"Fetching taxon_id for '{bird}'")
  taxon_id = get_taxon_id_by_name(bird)
  taxon_ids.append(taxon_id)
  time.sleep(1)

birds_dataframe.insert(1, column = "taxon_id", value = taxon_ids)
birds_dataframe.to_csv("../config/texas_birds.csv", index=False)

print("Done!")