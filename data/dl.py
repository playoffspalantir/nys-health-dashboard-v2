# download_data.py
import requests
import os

# --- Configuration ---
URL = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/new-york-counties.geojson"
FINAL_GEOJSON_NAME = "NYS_Counties.geojson"
DATA_FOLDER = "data"


def download_geojson():
    """Downloads the NYS Counties GeoJSON file."""
    print(f"Starting download from: {URL}")

    try:
        if not os.path.exists(DATA_FOLDER):
            os.makedirs(DATA_FOLDER)
            print(f"Created '{DATA_FOLDER}' directory.")

        response = requests.get(URL)
        response.raise_for_status()  # Raise an exception for bad status codes

        final_path = os.path.join(DATA_FOLDER, FINAL_GEOJSON_NAME)
        with open(final_path, 'w') as f:
            f.write(response.text)

        print(f"\n✅ Success! '{FINAL_GEOJSON_NAME}' is now in your '{DATA_FOLDER}' folder.")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ ERROR: Could not download the file. Please check your internet connection. Details: {e}")
    except Exception as e:
        print(f"\n❌ ERROR: An unexpected error occurred. Details: {e}")


if __name__ == "__main__":
    download_geojson()