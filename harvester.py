import requests
import json

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
            break

        if not data.get('success'):
            print("API request was not successful.")
            break

        if total_datasets is None:
            total_datasets = data['result']['count']
            print(f"Total datasets found in catalog: {total_datasets}")

        results = data['result']['results']
        
        if not results:
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

    return list(xml_links)

if __name__ == "__main__":
    found_links = get_iso_xml_links()
    output_file = "datasets-index.html"
    with open(output_file, "w") as f:
        f.write("<html><body>")
        for link in found_links:
            f.write(f"<a href=\"{link}\">{link}</a>\n")
        f.write("</body></html>\n")
    print(f"\nAll links have been saved to {output_file}")
