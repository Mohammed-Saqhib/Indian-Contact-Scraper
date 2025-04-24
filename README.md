# Indian-Contact-Scraper

A professional tool to extract contact information (name, email, phone, social media profiles) of Indian professionals based on location and profession. This project provides both a command-line interface and a user-friendly web application built with Streamlit.

## 🌟 Features

- **Targeted Search**: Find professionals by state, city, and profession across India
- **Rich Contact Data**: Extract comprehensive contact information:
  - Names
  - Email addresses
  - Phone numbers (Indian format)
  - LinkedIn profiles
  - Instagram handles
  - Twitter accounts
- **Multiple Interfaces**:
  - Command-line tool for scripting and automation
  - Web interface for easy interactive use
  - Direct URL scraping for specific websites
- **Data Management**:
  - Save results in structured CSV format
  - Fix common data issues (like scientific notation in phone numbers)
  - Preview and manage extracted contacts

## 📋 Prerequisites

- Python 3.6+
- Internet connection
- [Optional] Git for cloning the repository

## 🔧 Installation

1. Clone this repository:
```
git clone https://github.com/yourusername/indian-contact-scraper.git
cd indian-contact-scraper
```

2. Install required packages:
```
pip install -r requirements.txt
```

## 🚀 Usage

### Command-Line Interface

Run the basic scraper with the following command:
```
python run_scraper.py --state "Maharashtra" --city "Mumbai" --profession "doctor" --pages 3
```

For enhanced features:
```
python run_enhanced_scraper.py --state "Karnataka" --city "Bangalore" --profession "engineer" --debug
```

### Direct URL Scraping

Test scraping on a specific website:
```
python test_scraper.py https://example.com
```

### Web Interface

Launch the Streamlit web app:
```
streamlit run app.py
```
Then open your browser at http://localhost:8501 to access the user-friendly interface.

### CSV Management

Manage your extracted data files:
```
streamlit run csv_manager_app.py
```

## 📁 Project Structure

```
indian-contact-scraper/
├── indian_contact_scraper.py   # Core scraper functionality
├── app.py                      # Streamlit web application
├── run_scraper.py              # Basic command line interface
├── run_enhanced_scraper.py     # Advanced command line interface
├── test_scraper.py             # Direct URL testing utility
├── debug_scraper.py            # Debugging utilities
├── csv_manager.py              # CSV file management utilities
├── csv_manager_app.py          # CSV management web interface
├── file_explorer.py            # Local file explorer utility
├── fix_csv_numbers.py          # Utility to fix phone number formats
├── requirements.txt            # Project dependencies
├── output/                     # Directory for scraped data
└── README.md                   # Project documentation
```

## 🎮 Command Line Arguments

### Basic Scraper
- `--state`: State in India (required)
- `--city`: City name (required)
- `--profession`: Profession to search for (required)
- `--output`: Custom output filename (optional)
- `--pages`: Number of search result pages to process (default: 0 for unlimited)

### Enhanced Scraper
- `--state`, `--city`, `--profession`: Same as basic scraper
- `--output`: Custom output filename
- `--pages`: Maximum pages to scrape
- `--debug`: Enable detailed logging
- `--fix`: Fix phone number formatting in existing CSV files

## 💾 Output Format

The tool generates CSV files containing the following information:

| Field | Description |
|-------|-------------|
| name | Person or organization name |
| email | Email address |
| phone | Phone number (formatted with country code) |
| linkedin | LinkedIn profile URL |
| instagram | Instagram profile URL |
| twitter | Twitter/X profile URL |
| profession | Specified profession |
| city | City location |
| state | State location |
| domain | Website domain name |
| source_url | Original URL where information was found |

## ⚖️ Legal and Ethical Considerations

This tool is for educational and research purposes only. When using this scraper:

- Always respect websites' terms of service and robots.txt directives
- Implement reasonable delays between requests to avoid overloading servers
- Only collect publicly available information
- Do not use the collected data for spam, harassment, or any illegal activities
- Consider data privacy regulations that might apply to your use case

Note: The user is solely responsible for ensuring that their use of this tool complies with applicable laws and regulations.

## ⚡ Examples

Find software engineers in Bangalore:
```
python run_scraper.py --state "Karnataka" --city "Bangalore" --profession "software engineer"
```

Find lawyers in Mumbai with custom output file:
```
python run_scraper.py --state "Maharashtra" --city "Mumbai" --profession "lawyer" --output "mumbai_lawyers.csv"
```

Fix phone number formatting in an existing CSV file:
```
python run_enhanced_scraper.py --state "Punjab" --city "Amritsar" --profession "doctor" --fix
```

## 🤝 Contributing

Contributions are welcome! If you'd like to improve this project:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📧 Contact

Your Name - msaqhib76@gmail.com

Project Link: https://github.com/Mohammed-Saqhib/Indian-Contact-Scraper

Don't forget to star the repository if you find it useful!
