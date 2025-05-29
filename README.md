# web_scraping
this script helps to automate pdf downloading process 

# Maharashtra Government Resolutions Scraper

This repository contains two Python scripts for working with Maharashtra Government Resolutions (GRs):
1. A web scraper to extract department lists from the GR portal
2. An automated PDF downloader for specific department GRs

## Script 1: Department List Extractor (`departments_scraper.py`)

### Description
This script scrapes the Maharashtra GR portal to extract a list of all government departments and saves them to a CSV file.

### Features
- Uses `requests` and `BeautifulSoup` for web scraping
- Extracts department names and their corresponding values
- Saves data to `maharashtra_departments.csv`
- Lightweight and fast

### Usage
```bash
python departments_scraper.py