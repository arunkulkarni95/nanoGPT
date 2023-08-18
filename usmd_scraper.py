import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
import string

# Base URLs of the website
base_urls = ["https://www.usmd.edu", "https://www.usmd.edu/usm"]

# Set up headers to mimic a web browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}

# Directory to save HTML files
html_directory = "scrape_results/usmd/html"
os.makedirs(html_directory, exist_ok=True)

# Set of non-HTML extensions to exclude
common_static_extensions = [
    ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx", ".csv", ".txt",
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tif", ".tiff", ".zip", ".rar", ".gz", ".tar",
    ".mp3", ".wav", ".ogg", ".flac", ".mp4", ".mov", ".avi", ".mkv", ".wmv", ".webm", ".flv",
    ".m4a", ".aac", ".ogg", ".wma", ".mpg", ".mpeg", ".3gp", ".3g2", ".swf", ".asf", ".rm", ".rmvb",
    ".mka", ".opus", ".aiff", ".m3u", ".pls", ".mid", ".midi"
]

# Set to store visited URLs and saved filenames
visited_urls = set()
saved_files = set()

# Function to sanitize a string for use in filenames
def sanitize_for_filename(name):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    return ''.join(c for c in name if c in valid_chars)

# Function to crawl a URL and save HTML content to a file
def crawl_and_save(url):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200 and is_valid_url(url):
            soup = BeautifulSoup(response.content, "html.parser")
            page_title = soup.title.string.strip() if soup.title else None

            if page_title:
                # Sanitize the title for use as a filename
                sanitized_title = sanitize_for_filename(page_title)

                # Save HTML content to a file
                file_name = os.path.join(html_directory, f"{sanitized_title}.html")
                if file_name not in saved_files:
                    with open(file_name, "w", encoding="utf-8") as file:
                        file.write(response.text)
                    saved_files.add(file_name)
                    print(f"Saved {file_name}")
    except Exception as e:
        print(f"Error accessing {url}: {e}")

# Function to check if a URL is valid for crawling (HTML content)
def is_valid_url(url):
    return all(not url.lower().endswith(ext) for ext in common_static_extensions)

# Initialize the queue with the base URLs
queue = base_urls.copy()

# Use ThreadPoolExecutor for multithreading
max_threads = 14
with ThreadPoolExecutor(max_threads) as executor:
    while queue:
        current_url = queue.pop(0)

        if current_url in visited_urls:
            continue

        visited_urls.add(current_url)

        # Submit the crawling task to the thread pool
        executor.submit(crawl_and_save, current_url)

        try:
            response = requests.get(current_url, headers=headers)
            if response.status_code == 200 and is_valid_url(current_url):
                try:
                    decoded_text = response.text.encode(response.encoding).decode("utf-8")
                except UnicodeDecodeError:
                    print(f"Skipped {current_url} due to decoding issues.")
                    continue

                soup = BeautifulSoup(decoded_text, "html.parser")

                # Find and enqueue links to other pages on the same domain
                for link in soup.find_all("a"):
                    link_url = link.get("href")
                    if link_url:
                        absolute_link = urljoin(current_url, link_url)
                        if any(absolute_link.startswith(base_url) for base_url in base_urls) and absolute_link not in visited_urls:
                            queue.append(absolute_link)

        except Exception as e:
            print(f"Error accessing {current_url}: {e}")

print("Web scraping is complete.")
