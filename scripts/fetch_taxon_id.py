import requests

def get_taxon_id_by_name(url: str, species_name: str) -> int | None:
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
  response = requests.get(url, params=params)

  if response.status_code == 200:
    results = response.json()["results"]    # returns matched taxon ID
    if results:
      return results[0]["id"]
  else:
    print("Error:", response.status_code)