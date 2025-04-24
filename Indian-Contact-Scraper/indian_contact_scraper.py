import requests
from bs4 import BeautifulSoup
import re
import time
import random
import csv
import os
from urllib.parse import urlparse, quote

class IndianContactScraper:
    def __init__(self, state, city, profession, output_file=None):
        self.state = state
        self.city = city
        self.profession = profession
        self.output_file = output_file or f"{state}_{city}_{profession}_contacts.csv"
        self.headers_list = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
        ]
        
        # Regular expression patterns
        self.email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        
        # Updated phone pattern to catch more variations
        self.indian_phone_pattern = r"(?:\+?91[-\s]*)?(?:[0]?)?[6-9][0-9\s\-]{8,11}"
        
        self.linkedin_pattern = r"(?:https?:\/\/)?(?:www\.)?linkedin\.com\/(?:in|company)\/[a-zA-Z0-9_-]+"
        self.instagram_pattern = r"(?:https?:\/\/)?(?:www\.)?instagram\.com\/[a-zA-Z0-9_.]+"
        self.twitter_pattern = r"(?:https?:\/\/)?(?:www\.)?(?:twitter|x)\.com\/[a-zA-Z0-9_]+"
        self.name_pattern = r"(?:[A-Z][a-z]+(?:\s[A-Z][a-z]+){1,3})"
        
        # Additional patterns for doctor-specific information
        self.designation_pattern = r"(?:Dr\.|Prof\.|Doctor|Professor|MD|MBBS|MS|MDS|DM|DNB|MCh)[,\s]+(?:[A-Z][a-zA-Z\s\.]+)"
        self.specialization_pattern = r"(?:Specialist|Speciality|Specialization)[\s\:]+([A-Za-z\s\&]+)"
        self.qualification_pattern = r"(?:MBBS|MD|MS|DNB|DM|MCh|BDS|MDS|DO|DCH|DTCD|FRCS|MRCP)(?:\([A-Za-z]+\))?"
        
        # Storage for extracted contacts
        self.contacts = []
        self.visited_urls = set()
        
        # Filters
        self.disposable_email_domains = [
            "mailinator.com", "yopmail.com", "10minutemail.com", "guerrillamail.com", 
            "tempmail.com", "example.com", "test.com"
        ]
        
        # Additional fields to extract
        self.additional_fields = [
            "designation", "qualification", "specialization", 
            "clinic_hospital", "address", "experience"
        ]
        
        # Add debug flag and counter
        self.debug = False
        self.search_attempts = 0
        self.successful_searches = 0

    def generate_search_queries(self):
        """Generate search queries based on state, city and profession"""
        base_queries = [
            f"{self.profession} in {self.city} {self.state} India contact",
            f"{self.profession} {self.city} {self.state} email phone",
            f"top {self.profession} in {self.city} {self.state} contact information",
            f"{self.city} {self.state} {self.profession} directory",
            f"{self.profession} association members {self.city} {self.state}",
            f"contact details of {self.profession} in {self.city} {self.state}"
        ]
        
        # For doctors, add more specific queries
        if self.profession.lower() == "doctor":
            base_queries.extend([
                f"medical practitioners in {self.city} {self.state} contact details",
                f"specialist doctors in {self.city} {self.state}",
                f"hospitals in {self.city} {self.state} doctors contact",
                f"clinics in {self.city} {self.state} doctor information"
            ])
            
        return base_queries

    def get_random_headers(self):
        """Get random user agent headers to avoid detection"""
        user_agent = random.choice(self.headers_list)
        return {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.google.com/",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }

    def fetch_google_search_results(self, query, start=0):
        """Fetch search results from Google with the given query and start index"""
        encoded_query = quote(query)
        url = f"https://www.google.com/search?q={encoded_query}&start={start}"
        
        try:
            headers = self.get_random_headers()
            response = requests.get(url, headers=headers, timeout=15)
            
            # Track search attempts
            self.search_attempts += 1
            
            # Check if we're getting a valid response
            if response.status_code == 200:
                self.successful_searches += 1
                return response.text
            else:
                print(f"Search request failed with status code: {response.status_code}")
                # Add delay to avoid triggering anti-scraping measures
                time.sleep(random.uniform(5, 10))
                return None
                
        except requests.RequestException as e:
            print(f"Error fetching search results for '{query}' (page {start//10 + 1}): {e}")
            # Add longer delay after an error
            time.sleep(random.uniform(10, 15))
            return None

    def extract_urls_from_search_results(self, html):
        """Extract URLs from Google search results HTML"""
        if not html:
            return []
            
        urls = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Google search results can have different structures, try multiple selectors
        selectors = [
            'div.yuRUbf a',           # Common modern structure
            'div.g div.yuRUbf a',     # Alternative structure
            'div.rc a',               # Older structure
            'h3.LC20lb a',            # Another variation
            'a[href^="http"]',        # Fallback: any external link
            'div.g a[href^="http"]'   # Another fallback
        ]
        
        for selector in selectors:
            results = soup.select(selector)
            if results:
                for result in results:
                    href = result.get('href')
                    if href and href.startswith('http') and 'google.com' not in href:
                        urls.append(href)
        
        # Alternative method for different Google layouts
        if not urls:
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                if href.startswith('/url?q='):
                    actual_url = href.split('/url?q=')[1].split('&')[0]
                    if 'google.com' not in actual_url:
                        urls.append(actual_url)
                elif href.startswith('http') and 'google.com' not in href:
                    urls.append(href)
        
        if self.debug:
            print(f"Found {len(urls)} URLs in search results")
            
        return list(set(urls))  # Remove duplicates

    def extract_and_filter_emails(self, html_content):
        """Extract email addresses from HTML content and filter out disposable/fake ones"""
        emails = []
        
        # Find all email addresses
        email_matches = re.findall(self.email_pattern, html_content)
        
        # Filter the emails
        for email in email_matches:
            # Skip very short emails
            if len(email) < 5:
                continue
                
            # Skip emails with disposable domains
            domain = email.split('@')[-1].lower()
            if any(disposable in domain for disposable in self.disposable_email_domains):
                continue
                
            # Skip common test emails
            if email.startswith(('test', 'example', 'user', 'admin', 'info@')):
                continue
                
            emails.append(email.lower())  # Convert to lowercase for consistency
        
        # Remove duplicates and return
        return list(set(emails))

    def extract_names(self, html_content, soup):
        """Extract names from HTML content"""
        names = []
        
        # Method 1: Using regex for common name patterns
        name_matches = re.findall(self.name_pattern, html_content)
        names.extend([name.strip() for name in name_matches if 8 <= len(name) <= 40])
        
        # Method 2: Look for common elements that might contain names
        for tag in soup.select('h1, h2, h3, h4, h5'):
            text = tag.text.strip()
            # Check if it looks like a name (2-3 words, proper case)
            words = text.split()
            if 2 <= len(words) <= 5 and all(word[0].isupper() for word in words if word):
                if 8 <= len(text) <= 40:  # Reasonable name length
                    names.append(text)
        
        # Method 3: Look for doctor-specific patterns if profession is doctor
        if self.profession.lower() == "doctor":
            dr_name_pattern = r"Dr\.?\s+([A-Z][a-z]+(\s+[A-Z][a-z]+){1,3})"
            dr_matches = re.findall(dr_name_pattern, html_content)
            if dr_matches:
                for match in dr_matches:
                    if isinstance(match, tuple) and match:
                        names.append(f"Dr. {match[0]}")
                    elif isinstance(match, str):
                        names.append(f"Dr. {match}")
        
        # Remove duplicates and return
        return list(set(names))

    def extract_doctor_info(self, html_content, soup):
        """Extract doctor-specific information from HTML content"""
        results = {
            "designation": "Not found",
            "qualification": "Not found",
            "specialization": "Not found",
            "clinic_hospital": "Not found",
            "address": "Not found",
            "experience": "Not found"
        }
        
        # Extract qualifications (MD, MBBS, etc.)
        qualification_matches = re.findall(self.qualification_pattern, html_content)
        if qualification_matches:
            results["qualification"] = ", ".join(list(set(qualification_matches)))
        
        # Extract specialization
        specialization_matches = re.findall(self.specialization_pattern, html_content)
        if specialization_matches:
            results["specialization"] = specialization_matches[0].strip()
        
        # Extract designation
        designation_matches = re.findall(self.designation_pattern, html_content)
        if designation_matches:
            results["designation"] = designation_matches[0].strip()
        
        # Extract experience
        exp_pattern = r"([0-9]+)\+?\s+years\s+(?:of\s+)?experience"
        exp_matches = re.findall(exp_pattern, html_content, re.IGNORECASE)
        if exp_matches:
            results["experience"] = f"{exp_matches[0]} years"
        
        # Look for address and clinic information
        address_pattern = r"(?:Address|Location|Clinic)[\s\:]+([A-Za-z0-9\s\,\-\#\.\(\)]+)(?:[\n\.\,]|Phone)"
        addr_matches = re.findall(address_pattern, html_content, re.IGNORECASE)
        if addr_matches:
            results["address"] = addr_matches[0].strip()
            
            # If address is found, try to extract clinic/hospital name
            lines = html_content.split('\n')
            for i, line in enumerate(lines):
                if addr_matches[0] in line and i > 0:
                    potential_clinic = lines[i-1].strip()
                    if 3 <= len(potential_clinic) <= 50:  # Reasonable clinic name length
                        results["clinic_hospital"] = potential_clinic
                        break
        
        return results

    def create_contact_records(self, domain, url, names, emails, phones, 
                              linkedin_profiles, instagram_profiles, twitter_profiles, doctor_info=None):
        """Create contact records by combining the extracted information"""
        
        # If we have more of one type than others, we'll create multiple records
        max_items = max(
            len(names), 
            len(emails), 
            len(phones), 
            len(linkedin_profiles), 
            len(instagram_profiles), 
            len(twitter_profiles)
        )
        
        # If we didn't find any contact info at all, don't create a record
        if max_items == 0:
            return
        
        # Start with one default record
        if max_items == 0:
            max_items = 1
        
        for i in range(min(max_items, 5)):  # Limit to 5 records per page to avoid noise
            record = {
                "name": names[i] if i < len(names) else "Not found",
                "email": emails[i] if i < len(emails) else "Not found",
                "phone": phones[i] if i < len(phones) else "Not found",
                "linkedin": linkedin_profiles[i] if i < len(linkedin_profiles) else "Not found",
                "instagram": instagram_profiles[i] if i < len(instagram_profiles) else "Not found",
                "twitter": twitter_profiles[i] if i < len(twitter_profiles) else "Not found",
                "profession": self.profession,
                "city": self.city,
                "state": self.state,
                "domain": domain,
                "source_url": url
            }
            
            # Add doctor-specific info if available
            if doctor_info and self.profession.lower() == "doctor":
                for key, value in doctor_info.items():
                    record[key] = value
            
            # Add the record only if it has at least a name, email or phone
            if (record["name"] != "Not found" or 
                record["email"] != "Not found" or 
                record["phone"] != "Not found"):
                self.contacts.append(record)
                
                # Debug info
                if self.debug:
                    print(f"Created record: {record['name']}, {record['email']}, {record['phone']}")

    def extract_social_media(self, html_content, pattern):
        """Extract social media profile links from HTML content"""
        profiles = []
        
        # Find all profile URLs
        matches = re.findall(pattern, html_content)
        
        # Clean and deduplicate
        for match in matches:
            # Make sure we have a full URL
            if not match.startswith('http'):
                if 'linkedin.com' in match:
                    match = f"https://{match}"
                elif 'instagram.com' in match:
                    match = f"https://{match}"
                elif 'twitter.com' in match or 'x.com' in match:
                    match = f"https://{match}"
            
            profiles.append(match)
        
        # Remove duplicates and return
        return list(set(profiles))

    def extract_phone_numbers(self, html_content):
        """Extract phone numbers from HTML content"""
        phones = []
        
        # Improved phone number patterns
        patterns = [
            r"(?:\+?91[-\s]*)?(?:[0]?)?[6-9][0-9\s\-]{8,11}",  # Basic Indian pattern
            r"(?:[\+]?91)?[-\s]*[6-9][0-9]{9}",                # Strict 10-digit format
            r"[0-9]{3}[-\s][0-9]{3}[-\s][0-9]{4}",             # XXX-XXX-XXXX format
            r"[0-9]{5}[-\s][0-9]{5}"                          # XXXXX-XXXXX format
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html_content)
            for match in matches:
                # Clean up the phone number
                phone = match.strip()
                phone = re.sub(r'\s+', '', phone)  # Remove spaces
                phone = re.sub(r'^0+', '', phone)  # Remove leading zeros
                
                # Format for consistency
                if len(phone) >= 10:
                    if not phone.startswith('+'):
                        # If it's a 10-digit number, add +91 prefix
                        if len(phone) == 10 and phone[0] in '6789':
                            phone = f"+91{phone}"
                        # If it has 91 prefix but no +, add the +
                        elif phone.startswith('91') and len(phone) >= 12:
                            phone = f"+{phone}"
                    phones.append(phone)
        
        # Remove duplicates and return
        return list(set(phones))

    def extract_contact_info_from_page(self, url):
        """Visit a URL and extract contact information"""
        if url in self.visited_urls:
            return None
        
        self.visited_urls.add(url)
        print(f"Visiting: {url}")
        
        try:
            headers = self.get_random_headers()
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                print(f"Failed to fetch {url}, status code: {response.status_code}")
                return None
                
            html_content = response.text
            domain = get_domain_name(url)
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract all types of information
            emails = self.extract_and_filter_emails(html_content)
            phones = self.extract_phone_numbers(html_content)
            linkedin_profiles = self.extract_social_media(html_content, self.linkedin_pattern)
            instagram_profiles = self.extract_social_media(html_content, self.instagram_pattern)
            twitter_profiles = self.extract_social_media(html_content, self.twitter_pattern)
            names = self.extract_names(html_content, soup)
            
            # Extract doctor-specific info if profession is doctor
            doctor_info = {}
            if self.profession.lower() == "doctor":
                doctor_info = self.extract_doctor_info(html_content, soup)
            
            # Create contact records
            self.create_contact_records(domain, url, names, emails, phones, 
                                      linkedin_profiles, instagram_profiles, twitter_profiles, doctor_info)
            
            return {
                'emails': emails,
                'phones': phones,
                'linkedin': linkedin_profiles,
                'instagram': instagram_profiles,
                'twitter': twitter_profiles,
                'names': names,
                'doctor_info': doctor_info
            }
            
        except requests.RequestException as e:
            print(f"Request error for {url}: {e}")
        except Exception as e:
            print(f"Error processing {url}: {e}")
        
        return None

    def scrape_specific_url(self, url):
        """
        Scrape contact information directly from a specific URL
        Returns a dictionary with extraction results and the contact record
        """
        print(f"Directly scraping URL: {url}")
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Reset contacts list for this specific URL scraping
        self.contacts = []
        
        try:
            # Extract domain for record keeping
            domain = get_domain_name(url)
            
            # Extract contact information
            extraction_result = self.extract_contact_info_from_page(url)
            
            # Return the extraction results and contacts
            return {
                'success': True,
                'extraction_result': extraction_result,
                'contacts': self.contacts,
                'domain': domain,
                'url': url
            }
        except Exception as e:
            print(f"Error scraping URL {url}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'contacts': self.contacts
            }

    def scrape(self, max_pages=None):
        """Main scraping method that coordinates the entire process"""
        search_queries = self.generate_search_queries()
        
        # Initialize counters
        total_urls_found = 0
        total_pages_processed = 0
        
        # Enable debug mode to see more information
        self.debug = True
        
        for query in search_queries:
            print(f"\nProcessing search query: {query}")
            
            page = 0
            empty_pages_count = 0
            max_empty_pages = 2  # Stop after this many consecutive empty pages
            
            while (max_pages is None or page < max_pages) and empty_pages_count < max_empty_pages:
                start_index = page * 10
                
                # Fetch search results
                html = self.fetch_google_search_results(query, start=start_index)
                if not html:
                    print(f"No HTML content returned for page {page+1} of query: {query}")
                    empty_pages_count += 1
                    if empty_pages_count >= max_empty_pages:
                        print(f"Too many empty pages, moving to next query")
                        break
                    time.sleep(random.uniform(4, 7))  # Add more delay after failed attempt
                    continue
                    
                # Extract URLs from search results
                urls = self.extract_urls_from_search_results(html)
                if not urls:
                    print(f"No URLs found on page {page+1} for query: {query}")
                    empty_pages_count += 1
                    if empty_pages_count >= max_empty_pages:
                        print(f"No more URLs found, moving to next query")
                        break
                else:
                    empty_pages_count = 0  # Reset counter when we find URLs
                    total_urls_found += len(urls)
                    total_pages_processed += 1
                    
                    # Process each URL - increased limit from 5 to 10
                    url_limit = min(10, len(urls))
                    print(f"Processing {url_limit} URLs from page {page+1}")
                    
                    for url_idx, url in enumerate(urls[:url_limit]):
                        print(f"URL {url_idx+1}/{url_limit}: {url}")
                        result = self.extract_contact_info_from_page(url)
                        
                        # Print more detailed results for debugging
                        if result:
                            found_items = {k: len(v) for k, v in result.items() if isinstance(v, list)}
                            print(f"Found items: {found_items}")
                        
                        # Add random delay between requests
                        time.sleep(random.uniform(2, 4))
                
                page += 1
                print(f"Completed page {page} for query: {query}")
                # Add longer delay between pages to prevent rate limiting
                time.sleep(random.uniform(4, 7))
        
        print(f"\nScraping summary:")
        print(f"- Search attempts: {self.search_attempts}")
        print(f"- Successful searches: {self.successful_searches}")
        print(f"- Pages processed: {total_pages_processed}")
        print(f"- URLs found: {total_urls_found}")
        print(f"- Contacts extracted: {len(self.contacts)}")
                
        # Return the number of contacts found
        return len(self.contacts)

    def save_to_csv(self):
        """Save extracted contacts to CSV file"""
        if not self.contacts:
            print("No contacts were found to save.")
            # Create an empty file with headers to prevent file not found errors
            try:
                # Base fieldnames
                fieldnames = ['name', 'email', 'phone', 'linkedin', 'instagram', 'twitter',
                             'profession', 'city', 'state', 'domain', 'source_url']
                
                # Add doctor-specific fields if profession is doctor
                if self.profession.lower() == "doctor":
                    fieldnames.extend(self.additional_fields)
                
                # Ensure the output directory exists
                output_dir = os.path.dirname(self.output_file)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                with open(self.output_file, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                
                print(f"Created empty CSV file with headers: {self.output_file}")
                return True
            except Exception as e:
                print(f"Error creating empty CSV file: {e}")
                return False
            
        try:
            # Base fieldnames
            fieldnames = ['name', 'email', 'phone', 'linkedin', 'instagram', 'twitter',
                         'profession', 'city', 'state', 'domain', 'source_url']
            
            # Add doctor-specific fields if profession is doctor
            if self.profession.lower() == "doctor":
                fieldnames.extend(self.additional_fields)
            
            # Ensure the output directory exists
            output_dir = os.path.dirname(self.output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            with open(self.output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for contact in self.contacts:
                    # Ensure phone is stored as a properly formatted string
                    if contact['phone'] != 'Not found':
                        # Make sure it's a string to prevent scientific notation
                        if isinstance(contact['phone'], (int, float)):
                            contact['phone'] = f"+{int(contact['phone'])}"
                        else:
                            contact['phone'] = str(contact['phone'])
                    
                    # Write only the fields in fieldnames
                    row_data = {field: contact.get(field, 'Not found') for field in fieldnames}
                    writer.writerow(row_data)
                    
            print(f"Successfully saved {len(self.contacts)} contacts to {self.output_file}")
            return True
        except Exception as e:
            print(f"Error saving to CSV: {e}")
            # Try a fallback approach with a different filename
            try:
                fallback_file = f"{self.output_file}.fallback.csv"
                with open(fallback_file, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    for contact in self.contacts:
                        row_data = {field: str(contact.get(field, 'Not found')) for field in fieldnames}
                        writer.writerow(row_data)
                print(f"Fallback save successful: {fallback_file}")
                return True
            except Exception as e2:
                print(f"Fallback save also failed: {e2}")
                return False


def get_domain_name(url):
    """Extract domain name from URL"""
    parsed_url = urlparse(url)
    return parsed_url.netloc
