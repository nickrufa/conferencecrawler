import requests

base_url = "http://local.dev.meetings.com/IDWEEK/_viewPosterData.cfm?thisID=#id#"
urls = [base_url.replace('#id#', str(i)) for i in range(1, 3)]  # Reduced to 2 URLs for brevity

def print_html_snippet(html_content, chars=500):
    print(f"First {chars} characters of HTML content:")
    print(html_content[:chars])
    print("...")

for url in urls:
    try:
        print(f"\nProcessing URL: {url}")
        response = requests.get(url)
        response.raise_for_status()
        
        print(f"Response status code: {response.status_code}")
        print(f"Response content length: {len(response.text)}")
        
        print_html_snippet(response.text)
        
        # Write the full HTML content to a file
        with open(f'raw_html_{url.split("=")[-1]}.html', 'w', encoding='utf-8') as file:
            file.write(response.text)
        print(f"Full HTML content written to raw_html_{url.split('=')[-1]}.html")

    except requests.RequestException as e:
        print(f"Error processing {url}: {e}")

print("Data retrieval complete. Check the raw HTML files for results.")