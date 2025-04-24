from indian_contact_scraper import IndianContactScraper
import sys

def test_direct_url_scraping():
    """Test scraping functionality directly on a single URL"""
    print("Starting test scraper...")
    
    # Test URL - be sure to use a URL that contains contact information
    test_url = "https://www.example.com"  # Replace with a real website URL
    
    # If URL provided as argument, use that instead
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    
    print(f"Testing URL: {test_url}")
    
    # Create scraper instance
    scraper = IndianContactScraper(
        state="Karnataka", 
        city="Bangalore", 
        profession="Engineer",
        output_file="output/test_output.csv"
    )
    
    # Enable debug mode
    scraper.debug = True
    
    # Scrape the URL
    print("Starting scrape...")
    result = scraper.scrape_specific_url(test_url)
    
    # Show results
    if result['success']:
        print(f"Scraping successful! Found {len(scraper.contacts)} contacts")
        
        # Print the first contact if available
        if scraper.contacts:
            print("\nFirst contact found:")
            for key, value in scraper.contacts[0].items():
                print(f"  {key}: {value}")
        else:
            print("No contacts were found.")
            
        # Save results to CSV
        scraper.save_to_csv()
        print(f"Results saved to: {scraper.output_file}")
    else:
        print(f"Scraping failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    test_direct_url_scraping()
