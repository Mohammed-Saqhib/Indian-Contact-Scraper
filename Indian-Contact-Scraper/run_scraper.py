from indian_contact_scraper import IndianContactScraper
import argparse
import os
import time

def main():
    parser = argparse.ArgumentParser(description='Scrape contact information for Indian professionals')
    parser.add_argument('--state', required=True, help='State in India (e.g. Maharashtra)')
    parser.add_argument('--city', required=True, help='City name (e.g. Mumbai)')
    parser.add_argument('--profession', required=True, help='Profession to search for (e.g. actor, teacher)')
    parser.add_argument('--output', help='Output CSV filename (optional)')
    parser.add_argument('--pages', type=int, default=0, 
                      help='Maximum number of search pages to process (default: 0 for unlimited)')
    
    args = parser.parse_args()
    
    # Create output directory if needed
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate default output file if not provided
    output_file = args.output
    if not output_file:
        output_file = os.path.join(output_dir, f"{args.state}_{args.city}_{args.profession}_contacts.csv")
    
    print(f"Starting contact information scraping for {args.profession}s in {args.city}, {args.state}")
    print(f"Results will be saved to: {output_file}")
    
    # Create and run scraper
    start_time = time.time()
    scraper = IndianContactScraper(
        state=args.state,
        city=args.city,
        profession=args.profession,
        output_file=output_file
    )
    
    try:
        # Convert pages=0 to None for unlimited scraping
        max_pages = None if args.pages == 0 else args.pages
        print(f"Search page limit: {'Unlimited' if max_pages is None else max_pages}")
        
        num_contacts = scraper.scrape(max_pages=max_pages)
        scraper.save_to_csv()
        
        elapsed_time = time.time() - start_time
        print(f"\nScraping completed in {elapsed_time:.2f} seconds")
        print(f"Found {num_contacts} contacts for {args.profession}s in {args.city}, {args.state}")
        
    except KeyboardInterrupt:
        print("\nScraping interrupted by user. Saving current results...")
        scraper.save_to_csv()
    except Exception as e:
        print(f"\nError during scraping: {e}")
        print("Attempting to save any results collected so far...")
        scraper.save_to_csv()

if __name__ == "__main__":
    main()
