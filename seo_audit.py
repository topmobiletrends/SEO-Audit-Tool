import requests
from bs4 import BeautifulSoup
import pandas as pd

# Ask the user for the website URL
website_url = input("Enter the website URL to audit (e.g., https://example.com): ")

# Fetch the website content
try:
    response = requests.get(website_url)
    response.raise_for_status()  # Check for errors
    html_content = response.text
except requests.exceptions.RequestException as e:
    print(f"Error fetching the website: {e}")
    exit()

# Parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Check for title tag
title_tag = soup.find('title')
if title_tag:
    print(f"Title Tag: {title_tag.text}")
else:
    print("No Title Tag Found!")

# Check for meta description
meta_description = soup.find('meta', attrs={'name': 'description'})
if meta_description:
    print(f"Meta Description: {meta_description['content']}")
else:
    print("No Meta Description Found!")

# Find all links on the page
links = soup.find_all('a', href=True)
broken_links = []

for link in links:
    href = link['href']
    if href.startswith('http'):  # Check only external links
        try:
            link_response = requests.get(href)
            if link_response.status_code == 404:
                broken_links.append(href)
        except:
            broken_links.append(href)

# Print broken links
if broken_links:
    print("\nBroken Links Found:")
    for broken_link in broken_links:
        print(broken_link)
else:
    print("\nNo Broken Links Found!")

# Create a report
report_data = {
    "Website": [website_url],
    "Title Tag": [title_tag.text if title_tag else "Missing"],
    "Meta Description": [meta_description['content'] if meta_description else "Missing"],
    "Broken Links": [", ".join(broken_links) if broken_links else "None"]
}

# Convert to a DataFrame
report_df = pd.DataFrame(report_data)

# Save the report to a CSV file
report_df.to_csv('seo_audit_report.csv', index=False)
print("\nSEO Audit Report saved to 'seo_audit_report.csv'!")