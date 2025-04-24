import csv
import argparse
import os

def fix_scientific_notation_numbers(file_path):
    """Fix phone numbers in scientific notation in a CSV file"""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
    
    # Create a backup of the original file
    backup_path = file_path + '.backup'
    try:
        with open(file_path, 'r', encoding='utf-8') as src:
            with open(backup_path, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
        print(f"Backup created: {backup_path}")
    except Exception as e:
        print(f"Error creating backup: {e}")
        return False
    
    try:
        # Read all data from the CSV
        all_rows = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            
            for row in reader:
                # Fix phone number format
                if 'phone' in row and row['phone'] != 'Not found':
                    phone = row['phone']
                    if 'E+' in phone:
                        try:
                            # Convert from scientific notation to full number
                            phone_float = float(phone)
                            
                            # Format as Indian phone number with +91 prefix
                            phone_int = int(phone_float)
                            if phone_int > 1000000000:  # Reasonable size check
                                # If it's a 12-digit number with 91 prefix
                                if phone_int > 910000000000 and phone_int < 919999999999:
                                    formatted_phone = f"+{phone_int}"
                                else:
                                    # Extract the last 10 digits and add +91 prefix
                                    last_ten = str(phone_int)[-10:]
                                    formatted_phone = f"+91{last_ten}"
                                
                                row['phone'] = formatted_phone
                                print(f"Fixed: {phone} → {formatted_phone}")
                        except Exception as e:
                            print(f"Error converting phone {phone}: {e}")
                
                all_rows.append(row)
        
        # Write the fixed data back to the file
        if all_rows:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for row in all_rows:
                    writer.writerow(row)
            
            print(f"\nSuccessfully fixed {len(all_rows)} rows in {file_path}")
            return True
    except Exception as e:
        print(f"Error processing CSV file: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Fix phone numbers in scientific notation in CSV files')
    parser.add_argument('input_file', help='Path to the CSV file to fix')
    
    args = parser.parse_args()
    fix_scientific_notation_numbers(args.input_file)

if __name__ == "__main__":
    main()
