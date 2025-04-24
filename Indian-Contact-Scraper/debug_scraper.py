import requests
from bs4 import BeautifulSoup
import argparse
import time
import random
import os
from urllib.parse import quote
from indian_contact_scraper import IndianContactScraper

def debug_search_results(query, state, city, profession):
    """Test search result fetching and URL extraction"""
    print(f"Testing search query: {query}")
    
    # Create a scraper instance
    scraper = IndianContactScraper(
        state=state,
        city=city,
        profession=profession
    )
    
    # Enable debug mode
    scraper.debug = True
    
    # Fetch search results
    html = scraper.fetch_google_search_results(query)
    
    if not html:
        print("❌ Failed to fetch search results")
        return
        
    print(f"✅ Successfully fetched search results (HTML length: {len(html)})")
    
    # Extract URLs
    urls = scraper.extract_urls_from_search_results(html)
    
    if not urls:
        print("❌ No URLs extracted from search results")
        # Save HTML for debugging
        debug_dir = "debug_output"
        if not os.path.exists(debug_dir):
            os.makedirs(debug_dir)
        with open(os.path.join(debug_dir, "search_results.html"), "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Search results HTML saved to {os.path.join(debug_dir, 'search_results.html')}")
        return
        
    print(f"✅ Successfully extracted {len(urls)} URLs")
    
    # Test URL visiting and contact extraction for the first 3 URLs
    test_urls = urls[:3]
    
    for i, url in enumerate(test_urls):
        print(f"\nTesting URL {i+1}/{len(test_urls)}: {url}")
        contact_info = scraper.extract_contact_info_from_page(url)
        
        if not contact_info:
            print(f"❌ No contact info extracted from {url}")
        else:
            print(f"✅ Contact info extraction results:")
            for key, value in contact_info.items():
                if isinstance(value, list):
                    print(f"  - {key}: {len(value)} items")
                    if value:
                        print(f"    Examples: {value[:2]}")
                else:
                    print(f"  - {key}: {value}")
        
        # Add delay between requests
        if i < len(test_urls) - 1:
            time.sleep(random.uniform(2, 4))

def main():
    parser = argparse.ArgumentParser(description='Debug Indian Contact Scraper')
    parser.add_argument('--state', required=True, help='State in India (e.g. Karnataka)')
    parser.add_argument('--city', required=True, help='City name (e.g. Bangalore)')
    parser.add_argument('--profession', required=True, help='Profession to search for (e.g. lawyer)')
    
    args = parser.parse_args()
    
    print(f"=== Debug Session for {args.profession}s in {args.city}, {args.state} ===\n")
    
    # Create a scraper instance for generating queries
    temp_scraper = IndianContactScraper(
        state=args.state,
        city=args.city,
        profession=args.profession
    )
    
    # Get search queries
    search_queries = temp_scraper.generate_search_queries()
    
    # Test the first query
    if search_queries:
        debug_search_results(search_queries[0], args.state, args.city, args.profession)
    else:
        print("No search queries generated")

if __name__ == "__main__":
    main()
