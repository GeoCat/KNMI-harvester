import requests
import json
import sys

# Base URL for the KNMI CKAN API
CKAN_BASE_URL = "https://dataplatform.knmi.nl"
SEARCH_ENDPOINT = f"{CKAN_BASE_URL}/api/3/action/package_search"

def get_iso_xml_links():
    xml_links = set()
    rows_per_page = 100
    start = 0
    total_datasets = None

    print(f"Connecting to {CKAN_BASE_URL}...")

    while True:
        # Parameters for pagination
        params = {
            'q': '*:*',          # Search query (all datasets)
            'rows': rows_per_page,
            'start': start
        }
        
        try:
            response = requests.get(SEARCH_ENDPOINT, params=params)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to the API: {e}")
            return None
        except ValueError as e:
            print(f"Error parsing API response: {e}")
            return None

        if not data.get('success'):
            print("API request was not successful.")
            return None

        if total_datasets is None:
            if 'result' not in data or 'count' not in data['result']:
                print("API response missing 'result' or 'count'.")
                return None
            total_datasets = data['result']['count']
            print(f"Total datasets found in catalog: {total_datasets}")

        results = data.get('result', {}).get('results', [])
        
        if not results:
            if total_datasets is not None and start < total_datasets:
                print(f"Unexpected end of results: processed {start} of {total_datasets} datasets.")
                return None
            break

        for dataset in results:
            
            for resource in dataset.get('resources', []):
                url = resource.get('url', '')
                format_type = resource.get('format', '').upper()
                
                if url.endswith('.xml') or format_type == 'XML':
                    xml_links.add(url)

            for extra in dataset.get('extras', []):
                val = extra.get('value', '')
                if isinstance(val, str) and val.endswith('.xml') and val.startswith('http'):
                    xml_links.add(val)

        start += rows_per_page
        print(f"Processed {min(start, total_datasets)} / {total_datasets} datasets...")

        if total_datasets is not None and start >= total_datasets:
            break

    return list(xml_links)

if __name__ == "__main__":
    try:
        found_links = get_iso_xml_links()
    except Exception as e:
        print(f"Error occurred while retrieving ISO XML links: {e}")
        found_links = None

    if found_links is None:
        print("Harvesting failed. datasets-index.html was not overwritten.")
        sys.exit(1)

    if not found_links:
        print("No ISO XML links found in datasets. datasets-index.html was not overwritten.")
        sys.exit(1)

    output_file = "datasets-index.html"
    with open(output_file, "w") as f:
        f.write("<html><body>")
        for link in found_links:
            f.write(f"<a href=\"{link}\">{link}</a>\n")
        f.write("</body></html>\n")
    print(f"\nAll links have been saved to {output_file}")
