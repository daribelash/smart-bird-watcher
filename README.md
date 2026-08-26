# smart-bird-watcher

Watches a webcam feed, classifies whatever bird shows up using a custom-trained model, and
pops a Chrome notification when it's confident about the species. Built around a backyard
feeder pointed at Texas birds, but the pipeline works for any camera and any species list.

## How it works

```
webcam --> preprocess --> EfficientNet-B2 --> confidence > 0.95?
                                                    |
                                                    v
                                     log to CSV, save frame, POST to local API
                                                    |
                                                    v
                                   Chrome extension polls the API, fires a
                                   notification, links to a live dashboard
```

1. `app/camera.py` grabs frames from the webcam with OpenCV.
2. `app/preprocess.py` resizes and normalizes a frame into a model input tensor.
3. `app/inference.py` runs it through a fine-tuned EfficientNet-B2 and returns the top
   species and its confidence.
4. `app/main.py` is the detection loop: on a confident prediction, it logs the result to
   `logs/detections.csv`, saves the frame to `static/latest.jpg`, and posts the prediction to
   a local FastAPI server (`app/server.py`).
5. The Chrome extension in `chrome-extension/` (loaded unpacked, name "WingWatch") polls that
   server every second and raises a system notification on a new species. Clicking it opens
   `dashboard.html`, which shows the detected image and keeps polling for the next one.

## The model

`config/texas_birds.csv` lists 35 Texas bird species. The data pipeline in `scripts/` builds a
training set for them from iNaturalist:

1. `fetch_taxon_id.py` looks up each species' iNaturalist taxon ID.
2. `fetch_images.py` downloads CC-licensed observation photos for each taxon, scoped to a
   Texas bounding box, and records licensing metadata for each image.
3. `rename_files.py` normalizes filenames to `<species>_<index>.jpg`.

`notebooks/scripts.ipynb` does the rest: splits the images into train/test, fine-tunes an
EfficientNet-B2 (PyTorch, `torchvision.models`), and evaluates with a confusion matrix and a
prediction-vs-truth breakdown. The current checkpoint (`models/best_effnetb2.pth`) hit about
95% test accuracy after 10 epochs.

## Running it locally

```bash
git clone https://github.com/daribelash/smart-bird-watcher.git
cd smart-bird-watcher

python3 -m venv birds-env
source birds-env/bin/activate   # on Windows: birds-env\Scripts\activate

pip install -r requirements.txt
```

You'll need a trained model at `models/best_effnetb2.pth` (train one from the notebook, or drop
in an existing checkpoint) before detection will run.

**Start detection and the API together:**

```bash
./run.sh
```

This starts the FastAPI server (`uvicorn app.server:app`) in the background and then runs the
detection loop against your webcam. Stop it with Ctrl+C.

**Or run the pieces separately:**

```bash
uvicorn app.server:app --reload   # API, serves predictions and images on :8000
python run.py                     # detection loop, needs the API running to post results
```

**Load the Chrome extension:**

1. Go to `chrome://extensions`, enable Developer mode.
2. "Load unpacked" and select the `chrome-extension/` folder.
3. Keep the API running (`localhost:8000`); the extension polls it for new detections.

**View the dashboard:**

`dashboard.html` expects to be served, not opened as a file (it fetches from `localhost:8000`
and the notification click target is hardcoded to `localhost:5500/dashboard.html`). Any static
file server on port 5500 works, for example VS Code's Live Server extension.

## Project layout

```
app/                detection loop, camera, preprocessing, inference, FastAPI server
chrome-extension/   the "WingWatch" notification extension (unpacked, not published)
config/             paths, training hyperparameters, the Texas species list
scripts/            iNaturalist data collection (taxon lookup, image fetch, renaming)
notebooks/          dataset prep, model training, evaluation
models/             trained checkpoint + training results (not committed, see below)
static/, logs/      runtime output: latest detected frame, prediction JSON, detections.csv
```

`datasets/`, `models/*.pth`, and `logs/` are generated locally and aren't committed. `config.py`
resolves all paths relative to the repo root, so cloning fresh and running the scripts/notebook
recreates them in the right place.
