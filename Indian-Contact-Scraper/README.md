# Indian Contact Information Scraper

A tool to extract contact information (name, email, phone, social media) of Indian professionals based on state, city, and profession.

## Features

- Search for professionals by state, city, and profession
- Extract multiple types of contact information:
  - Names
  - Email addresses
  - Phone numbers (Indian format)
  - LinkedIn profiles
  - Instagram profiles
  - Twitter profiles
- Save results to CSV file for easy analysis

## Installation

1. Clone this repository
2. Install required packages:

```bash
pip install -r requirements.txt
```

## Usage

Run the scraper with the following command:

```bash
python run_scraper.py --state "Maharashtra" --city "Mumbai" --profession "doctor" --pages 3
```

### Command Line Arguments

- `--state`: State in India (required)
- `--city`: City name (required)
- `--profession`: Profession to search for (required)
- `--output`: Custom output filename (optional)
- `--pages`: Number of search result pages to process (default: 5)

## Output

The script generates a CSV file containing the following information for each contact found:

- Name
- Email address
- Phone number
- LinkedIn profile URL
- Instagram profile URL
- Twitter profile URL
- Profession
- City
- State
- Source domain
- Source URL

## Legal Notice

This tool is for educational purposes only. When scraping websites:

1. Respect the website's terms of service
2. Follow the guidelines in robots.txt
3. Be mindful of rate limits and use reasonable delays
4. Respect privacy and only collect publicly available information
5. Do not use the collected information for spam or harassment

## Examples

Find software engineers in Bangalore:
```bash
python run_scraper.py --state "Karnataka" --city "Bangalore" --profession "software engineer"
```

Find actors in Mumbai:
```bash
python run_scraper.py --state "Maharashtra" --city "Mumbai" --profession "actor"
```

Find teachers in Delhi with custom output file:
```bash
python run_scraper.py --state "Delhi" --city "New Delhi" --profession "teacher" --output "delhi_teachers.csv"
```
