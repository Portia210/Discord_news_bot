#!/usr/bin/env python3
"""
Helper script to download the required spaCy model for NER processing.
Run this script once to set up the spaCy model.
"""

import subprocess
import sys
from utils import logger

def download_spacy_model():
    """Download the English spaCy model for NER processing."""
    try:
        logger.info("🔄 Downloading spaCy English model...")
        subprocess.run([
            sys.executable, "-m", "spacy", "download", "en_core_web_sm"
        ], check=True)
        logger.info("✅ spaCy model downloaded successfully!")
        logger.info("You can now run the news clustering pipeline.")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to download spaCy model: {e}")
        logger.info("Please try running: python -m spacy download en_core_web_sm")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    download_spacy_model()
