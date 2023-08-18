import os
from bs4 import BeautifulSoup
import re
from concurrent.futures import ThreadPoolExecutor

# Directory containing HTML files
html_directory = "scrape_results/usmd/html"

# Directory to save extracted text and numbers
txt_directory = "scrape_results/usmd/txt"
os.makedirs(txt_directory, exist_ok=True)

# File to save the combined text
mega_text_file = "data/usmd/usmd_site_text.txt"

# Initialize ThreadPoolExecutor for multithreading
max_threads = 14  # Adjust based on your CPU's capabilities
executor = ThreadPoolExecutor(max_threads)

# Function to process HTML file
def process_html_file(html_file):
    html_path = os.path.join(html_directory, html_file)
        
    with open(html_path, "r", encoding="utf-8") as file:
        html_content = file.read()
    
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Extract text and numbers from the HTML
    text_content = "\n".join(line.strip() for line in soup.get_text().splitlines() if line.strip())
    numbers = re.findall(r'\b\d+\b', text_content)  # Extract numbers using regex
    
    # Combine text and numbers
    combined_content = text_content + "\n\n" + "\n".join(numbers)
    
    # Save combined content to a corresponding .txt file
    txt_file_name = os.path.splitext(html_file)[0] + ".txt"
    txt_file_path = os.path.join(txt_directory, txt_file_name)
    
    with open(txt_file_path, "w", encoding="utf-8") as file:
        file.write(combined_content)
    
    # Append to the mega text file
    with open(mega_text_file, "a", encoding="utf-8") as file:
        file.write(combined_content + "\n\n")

# List HTML files
html_files = [file for file in os.listdir(html_directory) if file.endswith(".html")]

# Process HTML files using ThreadPoolExecutor
executor.map(process_html_file, html_files)

print("Text and numbers extracted and saved.")
