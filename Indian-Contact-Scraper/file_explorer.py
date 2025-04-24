import os
import sys
import webbrowser
import argparse

def open_file_explorer(path):
    """Open the file explorer to the given path"""
    if os.path.exists(path):
        if sys.platform == 'win32':
            os.startfile(path)
        elif sys.platform == 'darwin':  # macOS
            webbrowser.open(f'file://{os.path.abspath(path)}')
        else:  # Linux
            try:
                os.system(f'xdg-open "{os.path.abspath(path)}"')
            except:
                print(f"Could not open file explorer to {path}")
        return True
    else:
        print(f"Path does not exist: {path}")
        return False

def list_csv_files(directory):
    """List all CSV files in the directory"""
    if not os.path.exists(directory):
        print(f"Directory does not exist: {directory}")
        return []
    
    csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]
    
    if csv_files:
        print(f"Found {len(csv_files)} CSV files in {directory}:")
        for i, file in enumerate(csv_files, 1):
            file_size = os.path.getsize(os.path.join(directory, file)) / 1024  # KB
            print(f"{i}. {file} ({file_size:.2f} KB)")
    else:
        print(f"No CSV files found in {directory}")
    
    return csv_files

def main():
    parser = argparse.ArgumentParser(description='CSV File Explorer')
    parser.add_argument('--dir', default='output', help='Directory to explore (default: output)')
    parser.add_argument('--open', action='store_true', help='Open the directory in file explorer')
    
    args = parser.parse_args()
    
    directory = args.dir
    
    # Create directory if it doesn't exist
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
            print(f"Created directory: {directory}")
        except Exception as e:
            print(f"Error creating directory {directory}: {e}")
            return
    
    # List CSV files
    csv_files = list_csv_files(directory)
    
    # Open directory in file explorer if requested
    if args.open:
        print(f"Opening directory: {directory}")
        open_file_explorer(directory)
    
    # If files exist, offer to open one
    if csv_files and not args.open:
        try:
            choice = input("\nEnter file number to open (or press Enter to exit): ")
            if choice and choice.isdigit():
                choice = int(choice)
                if 1 <= choice <= len(csv_files):
                    file_path = os.path.join(directory, csv_files[choice-1])
                    print(f"Opening {file_path}")
                    open_file_explorer(file_path)
                else:
                    print("Invalid choice")
        except KeyboardInterrupt:
            print("\nExiting...")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
