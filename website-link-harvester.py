import os
import time
import requests
from urllib.parse import urlparse, urljoin, urldefrag
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.console import Console
from rich.table import Table

# Paths for GeckoDriver and Firefox binary
geckodriver_path = "C:/WebDrivers/geckodriver.exe"
firefox_binary_path = "C:/Program Files/Mozilla Firefox/firefox.exe"

# Set up headless Firefox options
firefox_options = Options()
firefox_options.binary_location = firefox_binary_path
firefox_options.add_argument("--headless")

driver = None
MAX_THREADS = 10  # Number of threads for concurrent processing

# Initialize console for rich display
console = Console()

def initialize_driver():
    global driver
    if driver is None:
        service = Service(geckodriver_path)
        driver = webdriver.Firefox(service=service, options=firefox_options)

def shutdown_driver():
    global driver
    if driver:
        driver.quit()
        driver = None

def fully_load_page(url):
    initialize_driver()
    driver.get(url)
    scroll_pause_time = 1
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "a"))
    )
    return driver.page_source

def save_links(links, output_dir, filename):
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w") as file:
        for link in sorted(links):
            file.write(link + "\n")
    print(f"[INFO] {filename} saved with {len(links)} links.")

def classify_link(link, domain, output_sets, from_sitemap=False):
    parsed_link, _ = urldefrag(link)
    parsed_link = urlparse(parsed_link)
    full_url = parsed_link.geturl()

    # Skip certain patterns like non-navigable assets and unnecessary external sitemaps
    if any(full_url.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif", ".css", ".js", ".svg", ".pdf"]):
        return
    if "sitemap" in full_url and from_sitemap:
        output_sets['sitemap'].add(full_url)
        return

    if parsed_link.netloc == domain:
        output_sets['internal'].add(full_url)
    elif parsed_link.netloc.endswith(f".{domain}"):
        output_sets['subdomain'].add(full_url)
    else:
        output_sets['external'].add(full_url)

def extract_links(url, domain, output_sets, from_sitemap=False):
    try:
        html_content = fully_load_page(url)
        soup = BeautifulSoup(html_content, "html.parser")
        for link_tag in soup.find_all("a", href=True):
            href = urljoin(url, link_tag["href"])
            classify_link(href, domain, output_sets, from_sitemap=from_sitemap)
    except Exception as e:
        print(f"[ERROR] Could not extract links from {url}: {e}")

def fetch_sitemap_links(sitemap_url, domain, output_sets):
    try:
        response = requests.get(sitemap_url, timeout=10)
        parse_sitemap(response.content, sitemap_url, domain, output_sets)
    except requests.RequestException as e:
        print(f"[ERROR] Could not retrieve sitemap {sitemap_url}: {e}")

def parse_sitemap(content, base_url, domain, output_sets):
    try:
        soup = BeautifulSoup(content, "xml")
        for loc in soup.find_all("loc"):
            href = loc.text.strip()
            classify_link(href, domain, output_sets, from_sitemap=True)
            if href.endswith(".xml") and domain in href:
                fetch_sitemap_links(href, domain, output_sets)
    except Exception:
        soup = BeautifulSoup(content, "html.parser")
        for link_tag in soup.find_all("a", href=True):
            href = urljoin(base_url, link_tag["href"])
            classify_link(href, domain, output_sets, from_sitemap=True)
            if href.endswith(".xml") and domain in href:
                fetch_sitemap_links(href, domain, output_sets)

def crawl_links_in_threads(domain, output_sets):
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = []
        for link in list(output_sets['internal']):
            if link not in output_sets['visited']:
                output_sets['visited'].add(link)
                futures.append(executor.submit(extract_links, link, domain, output_sets))
        
        for future in as_completed(futures):
            future.result()  # Block until all threads are completed

def spider_website(start_url):
    parsed_url = urlparse(start_url)
    domain = parsed_url.netloc
    output_dir = os.path.join("output", domain)
    os.makedirs(output_dir, exist_ok=True)
    output_sets = {
        'internal': set(),
        'external': set(),
        'subdomain': set(),
        'sitemap': set(),
        'visited': set()
    }

    print("[INFO] Starting crawl from homepage...")
    extract_links(start_url, domain, output_sets)
    crawl_links_in_threads(domain, output_sets)

    print("[INFO] Processing sitemaps...")
    sitemap_url = f"{parsed_url.scheme}://{domain}/sitemap.xml"
    fetch_sitemap_links(sitemap_url, domain, output_sets)
    crawl_links_in_threads(domain, output_sets)

    # Remove any "sitemap.xml" links from internal
    output_sets['internal'].difference_update(output_sets['sitemap'])

    save_links(output_sets['internal'], output_dir, "internal-links.txt")
    save_links(output_sets['external'], output_dir, "external-links.txt")
    save_links(output_sets['subdomain'], output_dir, "sub-domain-links.txt")
    save_links(output_sets['sitemap'], output_dir, "sitemap-links.txt")

    show_results_table(output_sets)
    shutdown_driver()

def show_results_table(output_sets):
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Link Type")
    table.add_column("Count", justify="right")
    table.add_row("Internal Links", str(len(output_sets['internal'])))
    table.add_row("Subdomain Links", str(len(output_sets['subdomain'])))
    table.add_row("External Links", str(len(output_sets['external'])))
    table.add_row("Sitemap Links", str(len(output_sets['sitemap'])))
    console.print(table)

def main():
    print("\n==========================================")
    print("Website Link Harvester by Neeraj Sihag ")
    print("Repo: https://github.com/Neeraj-Sihag/Website-Link-Harvester")
    print("==========================================\n")

    start_url = input("Enter the main website URL to start crawling: ")
    spider_website(start_url)
    print("\n[INFO] All tasks completed successfully.")

if __name__ == "__main__":
    main()
