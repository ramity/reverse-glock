#!/bin/bash

JSON_FILE="url-set.json"
OUTPUT_DIR="./photos"

# Create download directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Read the JSON file and extract URLs WITHOUT using jq
urls=$(grep -o '"https://.*\.png"' "$JSON_FILE" | tr -d '"')

# Initialize counter
counter=0

# Loop through each URL and download the file
for url in $urls; do
  printf -v filename "%03d.png" "$counter"

  echo "Downloading: $url -> $filename"

  # Download directly to numbered filename inside OUTPUT_DIR
  curl -s -L "$url" -o "$OUTPUT_DIR/$filename"

  ((counter++))
done

echo "Download complete. Files saved in $OUTPUT_DIR directory."
