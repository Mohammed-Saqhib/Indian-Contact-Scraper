from indian_contact_scraper import IndianContactScraper
import argparse
import os
import time
import csv

def validate_csv_file(file_path):
    """Check if a CSV file has proper phone number formatting"""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Check phone number format
                if 'phone' in row and row['phone'] != 'Not found':
                    phone = row['phone']
                    if 'E+' in phone:  # Scientific notation detected
                        print(f"❌ Scientific notation found in phone number: {phone}")
                        return False
        print(f"✅ CSV validation passed: {file_path}")
        return True
    except Exception as e:
        print(f"Error validating CSV: {e}")
        return False

def fix_csv_phone_numbers(file_path):
    """Fix any phone numbers in scientific notation in an existing CSV file"""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
        
    try:
        # Read the existing data
        rows = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                # Fix phone number format if in scientific notation
                if 'phone' in row and row['phone'] != 'Not found':
                    phone = row['phone']
                    if 'E+' in phone:
                        # Convert from scientific notation to full number string
                        try:
                            phone_float = float(phone)
                            phone = f"+{int(phone_float)}"
                            row['phone'] = phone
                        except Exception as e:
                            print(f"Error converting phone: {phone} - {e}")
                rows.append(row)
                
        # Write the fixed data back
        if rows:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for row in rows:
                    writer.writerow(row)
            print(f"✅ Fixed phone numbers in: {file_path}")
            return True
    except Exception as e:
        print(f"Error fixing CSV: {e}")
    return False

def main():
    parser = argparse.ArgumentParser(description='Enhanced scraper for Indian professional contact information')
    parser.add_argument('--state', required=True, help='State in India (e.g. Maharashtra)')
    parser.add_argument('--city', required=True, help='City name (e.g. Mumbai)')
    parser.add_argument('--profession', required=True, help='Profession to search for (e.g. doctor, teacher)')
    parser.add_argument('--output', help='Output CSV filename (optional)')
    parser.add_argument('--pages', type=int, default=0, help='Maximum number of search pages to process (0 for unlimited)')
    parser.add_argument('--fix', action='store_true', help='Fix an existing CSV file with scientific notation')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode for more verbose output')
    
    args = parser.parse_args()
    
    # Create output directory if needed
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate default output file if not provided
    output_file = args.output
    if not output_file:
        output_file = os.path.join(output_dir, f"{args.state}_{args.city}_{args.profession}_contacts.csv")
    
    # If --fix is specified, just fix an existing file
    if args.fix:
        fix_csv_phone_numbers(output_file)
        return
    
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
    
    # Enable debug mode if requested
    if args.debug:
        scraper.debug = True
        print("Debug mode enabled: You'll see more detailed information during scraping")
    
    try:
        # Convert pages=0 to None for unlimited scraping
        max_pages = None if args.pages == 0 else args.pages
        print(f"Search page limit: {'Unlimited' if max_pages is None else max_pages}")
        
        num_contacts = scraper.scrape(max_pages=max_pages)
        scraper.save_to_csv()
        
        elapsed_time = time.time() - start_time
        print(f"\nScraping completed in {elapsed_time:.2f} seconds")
        print(f"Found {num_contacts} contacts for {args.profession}s in {args.city}, {args.state}")
        
        # Validate the output file
        validate_csv_file(output_file)
        
    except KeyboardInterrupt:
        print("\nScraping interrupted by user. Saving current results...")
        scraper.save_to_csv()
    except Exception as e:
        print(f"\nError during scraping: {e}")
        print("Attempting to save any results collected so far...")
        scraper.save_to_csv()

if __name__ == "__main__":
    main()
