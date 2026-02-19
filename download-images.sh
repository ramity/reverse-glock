#!/bin/bash

JSON_FILE="url-set.json"
OUTPUT_DIR="./photos"

# Create download directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Read the JSON file and extract URLs WITHOUT using jq
urls=$(cat "$JSON_FILE" | grep -o '"https://.*\.png"' | tr -d '"')

# Loop through each URL and download the file
for url in $urls; do
  echo "Downloading: $url"
  # Use curl to download the file and save it to the download directory
  # -O option uses the remote filename for the local file
  # -s option makes curl silent (less verbose)
  # --create-dirs ensures the directory path exists
  curl -s -O --create-dirs "$url"
  # Move the downloaded file to the specified directory
  mv "$(basename "$url")" "$OUTPUT_DIR/"
done

echo "Download complete. Files saved in $OUTPUT_DIR directory."
