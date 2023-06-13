import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urldefrag

def extract_unique_absolute_urls(url, visited_links=None, depth_limit=3, current_depth=0):
    if visited_links is None:
        visited_links = set()

    if current_depth > depth_limit:
        return visited_links

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    absolute_urls = set()
    for link in soup.find_all("a"):
        href = link.get("href")
        if href and not href.startswith("http") and not href.startswith("#"):
            absolute_url = urljoin(url, href)
            absolute_url_without_fragment = urldefrag(absolute_url).url
            if absolute_url_without_fragment not in visited_links:
                absolute_urls.add(absolute_url)
                visited_links.add(absolute_url_without_fragment)

    for absolute_url in absolute_urls:
        visited_links = extract_unique_absolute_urls(absolute_url, visited_links, depth_limit, current_depth + 1)

    return visited_links


# all_unique_absolute_urls = extract_unique_absolute_urls(website_url, depth_limit=depth_limit)
