#this code give list elements of departments from the given URL and save it to a CSV file


import requests
from bs4 import BeautifulSoup
import csv

URL = 'https://gr.maharashtra.gov.in/1145/Government-Resolutions'
r = requests.get(URL)

soup = BeautifulSoup(r.content, 'html.parser')
print(soup.prettify())  # Print the HTML content for debugging

departments = []  # a list to store departments

# Find the department dropdown
table = soup.find('select', attrs={'id': 'SitePH_ddlDepartmentType'})

if table:
    # Extract all options except the first default one ("-- Select --")
    for option in table.find_all('option')[1:]:
        dept = {
            'value': option['value'],
            'name': option.get_text(strip=True)
        }
        departments.append(dept)
else:
    print("Department dropdown not found on the page")

# Save to CSV
filename = 'maharashtra_departments.csv'
with open(filename, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['value', 'name'])
    writer.writeheader()
    writer.writerows(departments)

print(f"Successfully saved {len(departments)} departments to {filename}")
