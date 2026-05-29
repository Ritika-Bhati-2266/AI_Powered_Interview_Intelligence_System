import os
import urllib.request
import zipfile
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("downloader")

VOSK_MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
TARGET_DIR = os.path.dirname(os.path.abspath(__file__))
VOSK_DIR = os.path.join(TARGET_DIR, "vosk_models")

def download_and_extract_vosk():
    """
    Downloads and unpacks the default lightweight Vosk english model for local offline STT.
    """
    if not os.path.exists(VOSK_DIR):
        os.makedirs(VOSK_DIR)

    zip_path = os.path.join(VOSK_DIR, "vosk-model.zip")
    extracted_model_name = "vosk-model-small-en-us-0.15"
    extracted_model_path = os.path.join(VOSK_DIR, extracted_model_name)

    if os.path.exists(extracted_model_path):
        logger.info(f"Vosk model already present at: '{extracted_model_path}'. Skipping download.")
        return

    try:
        logger.info(f"Downloading lightweight offline Vosk model from {VOSK_MODEL_URL}...")
        logger.info("This download is ~40MB and runs fully locally once downloaded...")
        
        # Download file
        urllib.request.urlretrieve(VOSK_MODEL_URL, zip_path)
        logger.info("Download complete. Extracting file...")
        
        # Unzip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(VOSK_DIR)
            
        logger.info(f"Model successfully extracted to '{extracted_model_path}'")
        
        # Clean up zip
        if os.path.exists(zip_path):
            os.remove(zip_path)
            
        logger.info("Temporary files cleaned up. Download process complete.")
    except Exception as e:
        logger.error(f"Failed to download and extract Vosk model: {e}")
        logger.error("Please download the model manually from alphacephei.com/vosk/models and extract it to models/vosk_models/")

if __name__ == "__main__":
    download_and_extract_vosk()
