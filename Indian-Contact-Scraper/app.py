import streamlit as st
import pandas as pd
import os
import time
import base64
from indian_contact_scraper import IndianContactScraper

# Set page config
st.set_page_config(
    page_title="Indian Contact Scraper",
    page_icon="📞",
    layout="wide"
)

def get_download_link(file_path, file_name):
    """Generate a download link for a file"""
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{file_name}" class="download-button">Download {file_name}</a>'
        return href
    except Exception as e:
        st.error(f"Error generating download link: {str(e)}")
        return None

def list_csv_files(directory="output"):
    """List all CSV files in the output directory"""
    if not os.path.exists(directory):
        return []
    
    return [f for f in os.listdir(directory) if f.endswith('.csv')]

def sanitize_filename_part(text):
    """Sanitize text for use in filenames by limiting length and removing invalid characters"""
    if not text:
        return "undefined"
    
    # Remove characters that are problematic in filenames
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        text = text.replace(char, '')
    
    # Limit length to prevent extremely long filenames
    max_length = 30
    if len(text) > max_length:
        text = text[:max_length]
    
    return text.strip().replace(' ', '_')

def main():
    # App header
    st.title("Indian Professional Contact Scraper")
    st.write("Extract contact information of Indian professionals by location and profession")
    
    # Create tabs for different modes
    tab1, tab2 = st.tabs(["Search-based Scraping", "Direct URL Scraping"])
    
    # Sidebar with information
    with st.sidebar:
        st.header("About")
        st.info(
            "This tool extracts publicly available contact information "
            "of professionals based on state, city, and profession. "
            "Please use responsibly and ethically."
        )
        st.header("Instructions")
        st.write("1. Enter the state, city and profession")
        st.write("2. Select the number of pages to scrape")
        st.write("3. Click 'Start Scraping'")
        st.write("4. View results and download CSV")
        
        # Add option to view existing files
        st.header("Existing Files")
        csv_files = list_csv_files()
        if csv_files:
            selected_file = st.selectbox("Select a file to view/download:", [""] + csv_files)
            if selected_file:
                file_path = os.path.join("output", selected_file)
                try:
                    df = pd.read_csv(file_path)
                    st.write(f"File contains {len(df)} records")
                    if len(df) > 0:
                        st.markdown(get_download_link(file_path, selected_file), unsafe_allow_html=True)
                        if st.button("View Selected File Contents"):
                            st.session_state['view_file'] = selected_file
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
        else:
            st.info("No CSV files found in the output directory")

    # Check if we should display a file from sidebar
    if 'view_file' in st.session_state and st.session_state['view_file']:
        st.header(f"Contents of {st.session_state['view_file']}")
        file_path = os.path.join("output", st.session_state['view_file'])
        try:
            df = pd.read_csv(file_path)
            st.dataframe(df)
            st.markdown(get_download_link(file_path, st.session_state['view_file']), unsafe_allow_html=True)
            if st.button("Clear View"):
                del st.session_state['view_file']
                st.experimental_rerun()
        except Exception as e:
            st.error(f"Error displaying file: {str(e)}")
        
        # Return to prevent showing the main interface when viewing a file
        return
    
    # Tab 1: Search-based Scraping
    with tab1:
        # Create two columns for input
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Search Parameters")
            
            # Create form for inputs
            with st.form("scraper_form"):
                # Common Indian states for dropdown
                indian_states = [
                    "Select a state", "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", 
                    "Chhattisgarh", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", 
                    "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", 
                    "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", 
                    "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", 
                    "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"
                ]
                
                # Common professions for dropdown
                professions = [
                    "Select a profession", "Doctor", "Lawyer", "Teacher", "Engineer", "Architect",
                    "Accountant", "Dentist", "Chef", "Journalist", "Musician",
                    "Photographer", "Designer", "Professor", "Consultant", "Others"
                ]
                
                # Form inputs
                state = st.selectbox("State", indian_states)
                city = st.text_input("City (e.g., Mumbai, Bangalore, Chennai)", "")
                profession = st.selectbox("Profession", professions)
                
                # If "Others" is selected, allow custom profession input
                if profession == "Others":
                    profession = st.text_input("Enter custom profession")
                
                max_pages = st.number_input(
                    "Maximum search pages to process (0 for unlimited)", 
                    min_value=0, 
                    value=3, 
                    help="Higher values will find more results. Use 0 for unlimited pages (capped at 10)."
                )
                
                # Add advanced options
                advanced_options = st.expander("Advanced Options")
                with advanced_options:
                    enable_debug = st.checkbox("Enable debug mode", False, 
                                              help="Show detailed logs during scraping")
                    scrape_timeout = st.slider("Scraping timeout (seconds)", 
                                               min_value=30, max_value=300, value=120,
                                               help="Maximum time to run the scraper")
                
                submitted = st.form_submit_button("Start Scraping")
        
        # When form is submitted
        if submitted:
            if state == "Select a state" or not city or profession == "Select a profession" or profession == "":
                st.error("Please fill in all fields (state, city, and profession)")
            else:
                with col2:
                    st.subheader("Scraping Progress")
                    
                    # Create output directory
                    output_dir = "output"
                    if not os.path.exists(output_dir):
                        os.makedirs(output_dir)
                    
                    # Sanitize inputs for filename 
                    safe_state = sanitize_filename_part(state)
                    safe_city = sanitize_filename_part(city)
                    safe_profession = sanitize_filename_part(profession)
                    
                    # Generate output filename
                    output_file = os.path.join(output_dir, f"{safe_state}_{safe_city}_{safe_profession}_contacts.csv")
                    
                    # Create and run scraper
                    progress_text = st.empty()
                    progress_text.info(f"Starting scraping for {profession}s in {city}, {state}...")
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    debug_info = st.empty()
                    
                    scraper = IndianContactScraper(
                        state=state,
                        city=city,
                        profession=profession,
                        output_file=output_file
                    )
                    
                    # Enable debug mode if requested
                    if enable_debug:
                        scraper.debug = True
                        debug_info.info("Debug mode enabled: You'll see more detailed information")
                    
                    try:
                        # Track start time
                        start_time = time.time()
                        
                        # Custom scraping with progress updates
                        search_queries = scraper.generate_search_queries()
                        
                        # Calculate total queries based on max_pages setting
                        if max_pages > 0:
                            total_queries = len(search_queries) * max_pages
                        else:
                            # For unlimited mode, set an initial estimate that will be updated
                            total_queries = len(search_queries) * 10
                            
                        processed = 0
                        
                        for i, query in enumerate(search_queries):
                            status_text.text(f"Processing search query ({i+1}/{len(search_queries)}): {query}")
                            
                            page = 0
                            continue_scraping = True
                            
                            while continue_scraping:
                                # Stop if we reached max_pages (if not unlimited)
                                if max_pages > 0 and page >= max_pages:
                                    break
                                    
                                status_text.text(f"Processing page {page+1} for query: {query}")
                                start_index = page * 10
                                
                                # Fetch search results
                                html = scraper.fetch_google_search_results(query, start=start_index)
                                if not html:
                                    debug_info.warning(f"No results returned for page {page+1}. This might be due to rate limiting or network issues.")
                                    time.sleep(3)  # Wait before continuing
                                    break
                                    
                                # Extract URLs from search results
                                urls = scraper.extract_urls_from_search_results(html)
                                if not urls:
                                    debug_info.warning(f"No URLs found on page {page+1}. Moving to next query.")
                                    break
                                    
                                # Update debug info
                                debug_info.info(f"Found {len(urls)} URLs on page {page+1}")
                                
                                # Process each URL
                                url_limit = min(5, len(urls))  # Process at most 5 URLs
                                for url_idx, url in enumerate(urls[:url_limit]):
                                    status_text.text(f"Analyzing URL {url_idx+1}/{url_limit}: {url[:50]}...")
                                    scraper.extract_contact_info_from_page(url)
                                    time.sleep(0.5)  # Reduced delay for better user experience
                                
                                processed += 1
                                
                                # For unlimited mode, update the total estimate as we go
                                if max_pages == 0:
                                    total_queries = max(total_queries, processed + len(search_queries))
                                    
                                # Update progress
                                progress = min(processed / total_queries, 1.0) if total_queries > 0 else 0
                                progress_bar.progress(progress)
                                
                                # Show current contact count
                                if hasattr(scraper, 'contacts'):
                                    debug_info.success(f"Found {len(scraper.contacts)} contacts so far")
                                
                                page += 1
                                # Add delay between pages to avoid rate limiting
                                time.sleep(2)
                        
                        # Save results
                        scraper.save_to_csv()
                        elapsed_time = time.time() - start_time
                        
                        # Clear progress indicators
                        status_text.empty()
                        debug_info.empty()
                        progress_text.success(f"✅ Scraping completed in {elapsed_time:.2f} seconds.")
                        
                        # Display results
                        if os.path.exists(output_file):
                            try:
                                df = pd.read_csv(output_file)
                                
                                if len(df) > 0:
                                    st.subheader(f"Found {len(df)} contacts")
                                    st.dataframe(df)
                                    
                                    # Add multiple download options
                                    st.subheader("Download Options")
                                    
                                    # Option 1: Direct download link
                                    download_link = get_download_link(output_file, 
                                                   f"{safe_state}_{safe_city}_{safe_profession}_contacts.csv")
                                    if download_link:
                                        st.markdown(download_link, unsafe_allow_html=True)
                                    
                                    # Option 2: Download with pandas
                                    csv_data = df.to_csv(index=False)
                                    b64 = base64.b64encode(csv_data.encode()).decode()
                                    st.markdown(
                                        f'<a href="data:file/csv;base64,{b64}" download="{safe_state}_{safe_city}_{safe_profession}_contacts.csv">Alternative Download Link</a>',
                                        unsafe_allow_html=True
                                    )
                                    
                                    # Option 3: Show file location
                                    st.info(f"File saved at: {os.path.abspath(output_file)}")
                                else:
                                    st.warning("No contacts found in the output file. Try different search parameters or increase the number of pages.")
                                    # Show search diagnostic info
                                    st.info(f"Diagnostic information:\n"
                                           f"- Search attempts: {scraper.search_attempts}\n"
                                           f"- Successful searches: {scraper.successful_searches}\n")
                            except Exception as e:
                                st.error(f"Error reading output file: {str(e)}")
                        else:
                            st.error(f"Output file not created: {output_file}")
                            
                    except Exception as e:
                        st.error(f"Error during scraping: {str(e)}")
                        # Try to save partial results
                        if hasattr(scraper, 'contacts'):
                            contact_count = len(scraper.contacts)
                            if contact_count > 0:
                                scraper.save_to_csv()
                                st.info(f"Saved {contact_count} contacts found before the error occurred.")
                            else:
                                st.warning("No contacts were found before the error occurred.")
    
    # Tab 2: Direct URL Scraping
    with tab2:
        st.subheader("Direct URL Scraping")
        st.write("Extract contact information directly from a specific website URL")
        
        url_col1, url_col2 = st.columns(2)
        
        with url_col1:
            with st.form("url_scraper_form"):
                direct_url = st.text_input(
                    "Website URL", 
                    placeholder="e.g., example.com or https://example.com",
                    help="Enter the website URL you want to scrape for contact information"
                )
                
                profession_for_url = st.selectbox(
                    "Profession (for categorization)", 
                    [
                        "Select a profession", "Doctor", "Lawyer", "Teacher", "Engineer", "Architect",
                        "Accountant", "Dentist", "Chef", "Journalist", "Musician",
                        "Photographer", "Designer", "Professor", "Consultant", "Others"
                    ]
                )
                
                # If "Others" is selected, allow custom profession input
                if profession_for_url == "Others":
                    profession_for_url = st.text_input("Enter custom profession")
                
                location_details = st.expander("Location Details (Optional)")
                with location_details:
                    # Common Indian states for dropdown
                    indian_states = [
                        "Select a state", "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", 
                        "Chhattisgarh", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", 
                        "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", 
                        "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", 
                        "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", 
                        "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"
                    ]
                    state_for_url = st.selectbox("State (Optional)", indian_states)
                    city_for_url = st.text_input("City (Optional)", "")
                
                url_submitted = st.form_submit_button("Extract Contact Information")
        
        # Process URL scraping when form is submitted
        if url_submitted:
            if not direct_url:
                st.error("Please enter a URL to scrape")
            elif profession_for_url == "Select a profession" or profession_for_url == "":
                st.error("Please select a profession for categorization")
            else:
                with url_col2:
                    st.subheader("Extraction Progress")
                    
                    # Create output directory if it doesn't exist
                    output_dir = "output"
                    if not os.path.exists(output_dir):
                        os.makedirs(output_dir)
                    
                    # Sanitize parts for filename
                    safe_url = sanitize_filename_part(direct_url.replace('https://', '').replace('http://', '').split('/')[0])
                    safe_profession = sanitize_filename_part(profession_for_url)
                    
                    # Generate output filename
                    state_part = sanitize_filename_part(state_for_url) if state_for_url != "Select a state" else "Unknown"
                    city_part = sanitize_filename_part(city_for_url) if city_for_url else "Unknown"
                    output_file = os.path.join(output_dir, f"direct_{safe_url}_{safe_profession}_contacts.csv")
                    
                    # Create progress indicators
                    progress_text = st.empty()
                    progress_text.info(f"Starting extraction from {direct_url}...")
                    
                    status_text = st.empty()
                    status_text.text("Initializing...")
                    
                    debug_info = st.empty()
                    
                    # Create and run scraper
                    scraper = IndianContactScraper(
                        state=state_for_url if state_for_url != "Select a state" else "Unknown",
                        city=city_for_url if city_for_url else "Unknown",
                        profession=profession_for_url,
                        output_file=output_file
                    )
                    
                    try:
                        # Track start time
                        start_time = time.time()
                        
                        # Scrape the specific URL
                        status_text.text(f"Extracting data from {direct_url}...")
                        result = scraper.scrape_specific_url(direct_url)
                        
                        if not result['success']:
                            debug_info.error(f"Error during extraction: {result.get('error', 'Unknown error')}")
                        else:
                            elapsed_time = time.time() - start_time
                            
                            # Save results
                            scraper.save_to_csv()
                            
                            # Clear progress indicators
                            status_text.empty()
                            progress_text.success(f"✅ Extraction completed in {elapsed_time:.2f} seconds.")
                            
                            # Display results
                            contact_count = len(scraper.contacts)
                            if contact_count > 0:
                                debug_info.success(f"Found {contact_count} contacts")
                            else:
                                debug_info.warning("No contacts found on this URL. The site might be using JavaScript to load content or has anti-scraping measures.")
                            
                            if os.path.exists(output_file):
                                try:
                                    df = pd.read_csv(output_file)
                                    
                                    if len(df) > 0:
                                        st.subheader(f"Found {len(df)} contacts")
                                        st.dataframe(df)
                                        
                                        # Add download options
                                        st.subheader("Download Options")
                                        download_link = get_download_link(output_file, 
                                                      f"direct_{safe_url}_{safe_profession}_contacts.csv")
                                        if download_link:
                                            st.markdown(download_link, unsafe_allow_html=True)
                                    else:
                                        st.warning("No contacts found in the output file.")
                                except Exception as e:
                                    st.error(f"Error reading output file: {str(e)}")
                            else:
                                st.error(f"Output file was not created.")
                                
                    except Exception as e:
                        st.error(f"Error during extraction: {str(e)}")
                        # Try to save partial results
                        if hasattr(scraper, 'contacts'):
                            contact_count = len(scraper.contacts)
                            if contact_count > 0:
                                scraper.save_to_csv()
                                st.info(f"Saved {contact_count} contacts found before the error occurred.")

if __name__ == "__main__":
    main()
