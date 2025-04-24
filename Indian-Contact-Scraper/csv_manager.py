import os
import csv
import pandas as pd
import shutil

class CSVManager:
    """
    Utility class to manage CSV files in the output directory
    """
    
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def list_csv_files(self):
        """List all CSV files in the output directory"""
        if not os.path.exists(self.output_dir):
            return []
        
        return [f for f in os.listdir(self.output_dir) if f.endswith('.csv')]
    
    def get_file_path(self, filename):
        """Get the full path for a file in the output directory"""
        return os.path.join(self.output_dir, filename)
    
    def file_exists(self, filename):
        """Check if a file exists in the output directory"""
        return os.path.exists(self.get_file_path(filename))
    
    def read_csv(self, filename):
        """Read a CSV file into a pandas DataFrame"""
        filepath = self.get_file_path(filename)
        if not os.path.exists(filepath):
            return None
        
        try:
            return pd.read_csv(filepath)
        except Exception as e:
            print(f"Error reading CSV file {filepath}: {e}")
            return None
    
    def delete_csv(self, filename):
        """Delete a CSV file from the output directory"""
        filepath = self.get_file_path(filename)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                return True
            except Exception as e:
                print(f"Error deleting file {filepath}: {e}")
                return False
        return False
    
    def export_csv(self, filename, destination):
        """Export a CSV file to another location"""
        source_path = self.get_file_path(filename)
        if not os.path.exists(source_path):
            return False
        
        try:
            shutil.copy(source_path, destination)
            return True
        except Exception as e:
            print(f"Error exporting file {filename} to {destination}: {e}")
            return False
    
    def preview_csv(self, filename, rows=5):
        """Preview first few rows of a CSV file"""
        df = self.read_csv(filename)
        if df is not None:
            return df.head(rows)
        return None
    
    def get_stats(self, filename):
        """Get statistics about a CSV file"""
        df = self.read_csv(filename)
        if df is not None:
            return {
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': list(df.columns),
                'size_bytes': os.path.getsize(self.get_file_path(filename))
            }
        return None
    
    def fix_phone_numbers(self, filename):
        """Fix phone numbers in scientific notation in a CSV file"""
        filepath = self.get_file_path(filename)
        if not os.path.exists(filepath):
            return False
        
        try:
            # Create a backup
            backup_path = filepath + '.backup'
            shutil.copy(filepath, backup_path)
            
            # Read all data
            fixed_count = 0
            all_rows = []
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                
                for row in reader:
                    if 'phone' in row and row['phone'] != 'Not found':
                        phone = row['phone']
                        if 'E+' in phone:
                            try:
                                phone_float = float(phone)
                                phone_int = int(phone_float)
                                formatted_phone = f"+{phone_int}"
                                row['phone'] = formatted_phone
                                fixed_count += 1
                            except Exception:
                                pass
                    
                    all_rows.append(row)
            
            # Write the fixed data back
            if all_rows:
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for row in all_rows:
                        writer.writerow(row)
            
            return fixed_count
            
        except Exception as e:
            print(f"Error fixing phone numbers in {filename}: {e}")
            return False
