from flask import Flask, request, render_template
import requests
from bs4 import BeautifulSoup
import pandas as pd

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        website_url = request.form["website_url"]
        try:
            # Fetch the website content
            response = requests.get(website_url)
            response.raise_for_status()
            html_content = response.text

            # Parse the HTML content
            soup = BeautifulSoup(html_content, 'html.parser')

            # Check for title tag
            title_tag = soup.find('title')
            title = title_tag.text if title_tag else "No Title Tag Found!"

            # Check for meta description
            meta_description = soup.find('meta', attrs={'name': 'description'})
            meta = meta_description['content'] if meta_description else "No Meta Description Found!"

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

            # Create a report
            report_data = {
                "Website": website_url,
                "Title Tag": title,
                "Meta Description": meta,
                "Broken Links": broken_links
            }

            # Save the report to a CSV file
            report_df = pd.DataFrame([report_data])
            report_df.to_csv('seo_audit_report.csv', index=False)

            # Display the results
            return render_template('index.html', results=report_data)

        except requests.exceptions.RequestException as e:
            return render_template('index.html', error=f"Error fetching the website: {e}")

    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)