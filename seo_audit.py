from flask import Flask, request, render_template_string
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
                "Website": [website_url],
                "Title Tag": [title],
                "Meta Description": [meta],
                "Broken Links": [", ".join(broken_links) if broken_links else "None"]
            }

            # Convert to a DataFrame
            report_df = pd.DataFrame(report_data)

            # Save the report to a CSV file
            report_df.to_csv('seo_audit_report.csv', index=False)

            # Display the results
            return render_template_string('''
                <h1>SEO Audit Results</h1>
                <p><strong>Website:</strong> {{ website_url }}</p>
                <p><strong>Title Tag:</strong> {{ title }}</p>
                <p><strong>Meta Description:</strong> {{ meta }}</p>
                <p><strong>Broken Links:</strong> {{ broken_links }}</p>
                <a href="/">Back</a>
            ''', website_url=website_url, title=title, meta=meta, broken_links=", ".join(broken_links) if broken_links else "None")

        except requests.exceptions.RequestException as e:
            return f"Error fetching the website: {e}"

    return render_template_string('''
        <h1>SEO Audit Tool</h1>
        <form method="POST">
            <label for="website_url">Enter Website URL:</label>
            <input type="text" id="website_url" name="website_url" required>
            <button type="submit">Audit</button>
        </form>
    ''')

if __name__ == "__main__":
    app.run(debug=True)