import os

# API handling parameters
TAXA_URL = "https://api.inaturalist.org/v1/taxa"
OBSERVATION_URL = "https://api.inaturalist.org/v1/observations"
API_REQUEST_INTERVAL = 5
PAGES_TO_FETCH = 2

# Paths
TEXAS_BIRDS_CSV = "../config/texas_birds.csv"
RAW_DATA_PATH = "../../datasets/data_original"
DATASET_PATH = "../../datasets/texas_birds_dataset"
MODEL_SAVE_PATH = "../models/best_effnetb2.pth"
RESULTS_SAVE_PATH = "../models/model_results_effnetb2.json"

# Training parameters
BATCH_SIZE = 32
NUM_WORKERS = os.cpu_count()
SEED = 42
TRAIN_SPLIT_RATIO = 0.8
NUM_CLASSES = 35
LEARNING_RATE = 1e-4
EPOCHS = 10

# Early stopping parameters
EARLY_STOPPING_PATIENCE = 3
EARLY_STOPPING_DELTA = 0.0