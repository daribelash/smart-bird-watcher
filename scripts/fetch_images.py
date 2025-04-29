import asyncio
import aiohttp
import aiofiles
import os
import re
import sys
import pandas as pd
from typing import Any, Dict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config.config import OBSERVATION_URL, API_REQUEST_INTERVAL, PAGES_TO_FETCH, TEXAS_BIRDS_CSV, RAW_DATA_PATH

birds_df = pd.read_csv(TEXAS_BIRDS_CSV)

# async -> the function can pause its execution and let other tasks run.
# they return coroutine objects that the event loop (managed by asyncio.run(main())) 
# schedules and runs concurrently
async def fetch_page(session: aiohttp.ClientSession, params: Dict[str, Any], semaphore: asyncio.Semaphore) -> Dict[str, Any]:
    """
    Fetches a single page of observations from the iNaturalist API.
    This function uses an asynchronous context manager with a semaphore to ensure that only a limited
    number of API calls are made concurrently. It sends a GET request with the specified query parameters,
    parses the response JSON, and enforces a delay to respect API rate limits.
    Args:
        session (aiohttp.ClientSession): The aiohttp session used for making HTTP requests.
        params (Dict[str, Any]): A dictionary of query parameters for the API request.
        semaphore (asyncio.Semaphore): Semaphore to limit the number of concurrent API calls.
    Returns:
        Dict[str, Any]: The JSON data returned from the API as a dictionary.
    """
    async with semaphore:  # global semaphore
        async with session.get(OBSERVATION_URL, params=params) as response:
            data = await response.json()
            await asyncio.sleep(API_REQUEST_INTERVAL)  # enforce delay globally
            return data
    
async def download_content(session: aiohttp.ClientSession, url: str, filename: str) -> None:
    """
    Downloads content from a given URL and saves it to a specified filename asynchronously.
    This function makes an asynchronous GET request to the given URL. If the request is successful,
    it opens (or creates) the specified file in binary write mode and writes the content into the file.
    If the request fails, it prints an error message.
    Args:
        session (aiohttp.ClientSession): The aiohttp session used for making HTTP requests.
        url (str): The URL of the content to download (typically an image URL).
        filename (str): The local file path where the downloaded content should be saved.
    Returns:
        None
    """
    try:
       async with session.get(url) as response:
            if response.status == 200:
                async with aiofiles.open(filename, "wb") as f:
                    content = await response.read()
                    await f.write(content)
                    #print(f"Content downloaded to: {filename}")
            else:
                print(f"Failed to download {url}: status {response.status}")
    except Exception as e:
       print(f"Cannot download {url}: {e}")
    
async def process_species(session: aiohttp.ClientSession, bird_name: str, taxon_id: int, pages_to_fetch: int, semaphore: asyncio.Semaphore) -> None:
    """
    Processes observations for a specific bird species by fetching observation pages and downloading images.
    For a given bird species (specified by its name and taxon ID), this function:
      - Creates a dedicated output directory under ../data using a safe version of the bird's name.
      - Fetches a specified number of pages of observation data from the iNaturalist API.
      - Extracts image URLs from the observations, converts them to medium-sized image URLs,
        and queues download tasks for each image.
      - Downloads all queued images concurrently.
    Args:
        session (aiohttp.ClientSession): The aiohttp session used for making HTTP requests.
        bird_name (str): The common name of the bird species.
        taxon_id (int): The iNaturalist taxon ID for the species.
        pages_to_fetch (int): The number of pages of observation data to fetch.
        semaphore (asyncio.Semaphore): The global semaphore for rate limiting.
    Returns:
        None
    """
    bird_name_replace = re.sub(r"[- ]", "_", bird_name).lower()
    species_dir = os.path.join(RAW_DATA_PATH, bird_name_replace)
    os.makedirs(species_dir, exist_ok=True)

    fetch_tasks = []
    licensing_metadata = []
    for page in range(1, pages_to_fetch + 1):
        params = {
            "taxon_id": taxon_id,
            "photos": "true",
            "per_page": 200,
            "page": page,
            "photo_license": "cc0,cc-by,cc-by-nc",
            "swlat": 25.80,
            "swlng": -101.50,
            "nelat": 33.75,
            "nelng": -93.50
        }
        fetch_tasks.append(fetch_page(session, params, semaphore))

    results = await asyncio.gather(*fetch_tasks)

    image_download_tasks = []
    image_counter = 1

    for result in results:
        if result and "results" in result:
            for obs in result["results"]:
                species = obs.get("species_guess", "")
                obs_id = obs.get("id", "")
                for photo in obs.get("photos", []):
                    photo_url = photo.get("url", "")
                    license_code: str = photo.get("license_code", "unknown")
                    attribution: str = photo.get("attribution", "")
                    if photo_url:
                        medium_url = photo_url.replace("square", "medium")
                        filename = os.path.join(species_dir, f"{bird_name_replace}_{image_counter}.jpg")
                        image_download_tasks.append(download_content(session, medium_url, filename))
                        licensing_metadata.append({
                            "observation_id": obs_id,
                            "species": species,
                            "photo_url": photo_url,
                            "medium_url": medium_url,
                            "license_code": license_code,
                            "attribution": attribution,
                            "filename": f"{bird_name_replace}_{image_counter}.jpg"
                        })
                        image_counter += 1

    print(f"{bird_name}: Total images queued for download: {image_counter - 1}")
    await asyncio.gather(*image_download_tasks)
    return licensing_metadata

async def main():
  # the session is automatically closed when the block is exited to ensure proper cleanup
  # Passing the same session object to each asynchronous function 
  # (like fetch_page and download_content) allows to reuse HTTP connections
    all_licensing = []
    global_semaphore = asyncio.Semaphore(1)
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for index, row in birds_df.iterrows():
            bird_name = row["bird_name"]
            taxon_id = row["taxon_id"]
            tasks.append(process_species(session, bird_name, taxon_id, PAGES_TO_FETCH, global_semaphore))
        results = await asyncio.gather(*tasks)
        for metadata in results:
            all_licensing.extend(metadata)

    licensing_csv = os.path.join(RAW_DATA_PATH, "attribution_credit.csv")
    pd.DataFrame(all_licensing).to_csv(licensing_csv, index=False)
    print(f"Licensing metadata saved to {licensing_csv}")

if __name__ == "__main__":
    asyncio.run(main())