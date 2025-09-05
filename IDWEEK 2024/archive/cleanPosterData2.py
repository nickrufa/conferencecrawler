import requests
from bs4 import BeautifulSoup

base_url = "http://local.dev.meetings.com/IDWEEK/_viewPosterData.cfm?thisID=#id#"
urls = [base_url.replace('#id#', str(i)) for i in range(1, 3)]  # Reduced to 2 URLs for brevity

def print_html_snippet(html_content, chars=500):
    print(f"First {chars} characters of HTML content:")
    print(html_content[:chars])
    print("...")

with open('extracted_poster_data.txt', 'w', encoding='utf-8') as output_file:
    for url in urls:
        try:
            print(f"\nProcessing URL: {url}")
            response = requests.get(url)
            response.raise_for_status()
            
            print(f"Response status code: {response.status_code}")
            print(f"Response content length: {len(response.text)}")
            
            print_html_snippet(response.text)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the main content div
            content_div = soup.find('div', id=lambda x: x and x.startswith('poster-info-'))
            
            if content_div:
                print("Main content div found. Content:")
                print(content_div.prettify()[:500])  # Print first 500 characters of the content div
            else:
                print("Main content div not found. Searching for alternative structures...")
                
                # Look for other potential identifying elements
                h1_elem = soup.find('h1')
                if h1_elem:
                    print("Found h1 element:", h1_elem.text.strip())
                
                col_md_12 = soup.find('div', class_='col-md-12')
                if col_md_12:
                    print("Found div with class 'col-md-12':", col_md_12.text.strip()[:100])
                
                pres_tidbits = soup.find_all('div', class_='pres-tidbit')
                if pres_tidbits:
                    print(f"Found {len(pres_tidbits)} 'pres-tidbit' elements")
                    for tidbit in pres_tidbits[:3]:  # Print first 3 tidbits
                        print(" -", tidbit.text.strip())

            print(f"Processed: {url}")

        except requests.RequestException as e:
            print(f"Error processing {url}: {e}")

print("Data extraction complete. Check 'extracted_poster_data.txt' for results.")