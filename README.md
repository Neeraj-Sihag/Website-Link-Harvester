# Website Link Harvester

A Python-based tool to efficiently harvest, categorize, and save links from any website. **Website Link Harvester** explores all pages to extract **internal links, external links, subdomain links, and sitemap links**. It’s designed for in-depth crawling, handling dynamic content, and organizing output files for easy access.

---

## Features

- **Comprehensive Link Extraction**: Crawls through all pages to capture every link, including dynamically loaded content.
- **Categorization**: Separates links into internal, external, subdomain, and sitemap categories.
- **Dynamic Content Loading**: Uses Selenium to load JavaScript-heavy sites and scroll pages for full content visibility.
- **Recursive Sitemap Exploration**: Finds and processes XML and HTML sitemaps, following additional sitemap links if found.
- **Automated Output**: Saves links into organized text files (internal-links.txt, external-links.txt, etc.).

---

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Neeraj-Sihag/Website-Link-Harvester.git
   cd Website-Link-Harvester
   ```

2. **Install Required Libraries**
   - **Using `requirements.txt`**:
     ```bash
     pip install -r requirements.txt
     ```
   - **Or install manually**:
     ```bash
     pip install selenium beautifulsoup4 rich
     ```

3. **GeckoDriver Setup**  
   Ensure `geckodriver` (for Firefox) is installed and accessible. Update `geckodriver_path` and `firefox_binary_path` in `website-link-harvester.py` as needed.

---

## Usage

Run the script with the main website URL to begin the crawl.

```bash
python website-link-harvester.py
```

Upon running, it will prompt for the main URL and start crawling:

```text
Enter the main website URL to start crawling: https://example.com
```

The output is saved in the `output/{domain_name}` folder, containing:

- **internal-links.txt**: All internal links found on the site
- **external-links.txt**: External links leading outside the domain
- **sub-domain-links.txt**: Links pointing to subdomains of the site
- **sitemap-links.txt**: Links collected specifically from sitemaps

---

## Example

```plaintext
python website-link-harvester.py

Enter the main website URL to start crawling: https://example.com
[INFO] Starting crawl from homepage...
[INFO] Processing sitemaps...
[INFO] internal-links.txt saved with 28 links.
[INFO] external-links.txt saved with 32 links.
[INFO] sub-domain-links.txt saved with 1 link.
[INFO] sitemap-links.txt saved with 5 links.
All tasks completed successfully.
```

### Output Summary:
- **Internal Links**: 28
- **External Links**: 32
- **Subdomain Links**: 1
- **Sitemap Links**: 5

---

## Requirements

- **Python 3.8+**
- **Selenium**: For navigating and loading dynamic content
- **BeautifulSoup**: For HTML/XML parsing
- **Rich**: For console output formatting

---

## Configuration

Edit `website-link-harvester.py` to modify the paths for `geckodriver` and `firefox`:

```python
geckodriver_path = "C:/WebDrivers/geckodriver.exe"
firefox_binary_path = "C:/Program Files/Mozilla Firefox/firefox.exe"
```

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## Contributions

Feel free to open issues or submit pull requests. All contributions are welcome!
