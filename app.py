from flask import Flask, request, render_template
import requests
from bs4 import BeautifulSoup
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

@app.route("/", methods=["GET", "POST"])
def index():
    try:
        if request.method == "POST":
            website_url = request.form.get("website_url")
            if not website_url:
                return render_template('index.html', error="Please enter a website URL.")

            app.logger.debug(f"Fetching website: {website_url}")
            try:
                # Fetch the website content with a timeout
                response = requests.get(website_url, timeout=5)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                app.logger.error(f"Error fetching the website: {e}")
                return render_template('index.html', error=f"Error fetching the website: {e}")

            html_content = response.text

            # Parse the HTML content
            app.logger.debug("Parsing HTML content")
            soup = BeautifulSoup(html_content, 'html.parser')

            # Check for title tag
            title_tag = soup.find('title')
            title = title_tag.text if title_tag else "No Title Tag Found!"

            # Check for meta description
            meta_description = soup.find('meta', attrs={'name': 'description'})
            meta = meta_description['content'] if meta_description else "No Meta Description Found!"

            # Check for headings
            headings = {
                "h1": [h1.text for h1 in soup.find_all('h1')],
                "h2": [h2.text for h2 in soup.find_all('h2')],
                "h3": [h3.text for h3 in soup.find_all('h3')],
            }

            # Check for image alt text
            images = []
            for img in soup.find_all('img'):
                images.append({
                    "src": img.get('src', 'No src'),
                    "alt": img.get('alt', 'No alt text')
                })

            # Find all links on the page (limit to 10 links to avoid timeouts)
            app.logger.debug("Checking for broken links")
            links = soup.find_all('a', href=True)[:10]
            broken_links = []

            for link in links:
                href = link['href']
                if href.startswith('http'):  # Check only external links
                    try:
                        # Check the link with a timeout
                        link_response = requests.get(href, timeout=5)
                        if link_response.status_code == 404:
                            broken_links.append(href)
                    except Exception as e:
                        app.logger.error(f"Error checking link {href}: {e}")
                        broken_links.append(href)

            # Create a report
            report_data = {
                "Website": website_url,
                "Title Tag": title,
                "Meta Description": meta,
                "Headings": headings,
                "Images": images,
                "Broken Links": broken_links
            }

            # Display the results
            app.logger.debug("Rendering results")
            return render_template('index.html', results=report_data)

        # Render the form for GET requests
        app.logger.debug("Rendering form")
        return render_template('index.html')

    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return render_template('index.html', error="An unexpected error occurred. Please try again.")

if __name__ == "__main__":
    app.run(debug=True)