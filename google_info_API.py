GOOGLE_SEARCH_ENGINE_ID =  "c51e2a70bf5174ccc"
GOOGLE_API_KEY = "AIzaSyCJKCZR7VFuRcW6GxmqcNVHJN9OxC1iLr0"
import requests



def get_url_from_name(query = "Bosch germany"):

    endpoint = "https://www.googleapis.com/customsearch/v1"

    # Construct the API endpoint URL and search query parameters
    params = {"key": GOOGLE_API_KEY, "cx": GOOGLE_SEARCH_ENGINE_ID, "q": query}

    # Send the API request with authentication headers
    response = requests.get(endpoint, params=params)

    # Parse the JSON response and extract the search results
    json_data = response.json()
    search_results = json_data["items"]
    urls = []
    # Print the URLs of the search results
    for result in search_results:
        urls.append(result["link"])
    start_url = urls[0]
    print(start_url)

    return start_url, result

if __name__ == "__main__":
    start_url, result = get_url_from_name()
    print(result)