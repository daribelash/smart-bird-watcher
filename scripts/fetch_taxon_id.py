import sys
import os
import pandas as pd
import requests
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config.config import TEXAS_BIRDS_CSV, TAXA_URL

birds_df = pd.read_csv(TEXAS_BIRDS_CSV)

def get_taxon_id_by_name(species_name: str) -> int | None:
  """
  Fetch the iNaturalist taxon ID for a provided bird species.
  Args:
    species_name (str): Name of the bird species.
  Returns:
    int | None: Taxon ID if found, otherwise None.
  """
  params = {
    "q" : species_name,
    "rank" : "species",
    "per_page" : 1
  }
  response = requests.get(TAXA_URL, params=params)

  if response.status_code == 200:
    results = response.json()["results"]    # returns matched taxon ID
    if results:
      return results[0]["id"]
  else:
    print("Error:", response.status_code)

taxon_ids = []

for bird in birds_df["bird_name"]:
  print(f"Fetching taxon_id for '{bird}'")
  taxon_id = get_taxon_id_by_name(bird)
  taxon_ids.append(taxon_id)
  time.sleep(1) # 1 second sleep to follow API rate limits

birds_df.insert(1, column = "taxon_id", value = taxon_ids)
birds_df.to_csv(TEXAS_BIRDS_CSV, index=False)