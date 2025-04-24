import streamlit as st
import os
import pandas as pd
import base64
import time
from csv_manager import CSVManager

st.set_page_config(
    page_title="CSV File Manager",
    page_icon="📊",
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

def main():
    st.title("CSV File Manager")
    st.write("Manage your extracted contact CSV files")
    
    # Initialize CSV manager
    csv_manager = CSVManager("output")
    
    # Refresh file list
    if 'refresh' not in st.session_state:
        st.session_state['refresh'] = 0
    
    # Layout with sidebar
    with st.sidebar:
        st.header("Actions")
        
        # Refresh button
        if st.button("🔄 Refresh File List"):
            st.session_state['refresh'] += 1
            st.success("File list refreshed")
            time.sleep(0.5)
        
        # Fix all files option
        if st.button("🔧 Fix Phone Numbers in All Files"):
            files = csv_manager.list_csv_files()
            if files:
                fixed_counts = {}
                for file in files:
                    fixed = csv_manager.fix_phone_numbers(file)
                    if fixed:
                        fixed_counts[file] = fixed
                
                if fixed_counts:
                    st.success("Fixed phone numbers in the following files:")
                    for file, count in fixed_counts.items():
                        st.write(f"- {file}: {count} numbers fixed")
                else:
                    st.info("No phone numbers needed fixing")
            else:
                st.warning("No CSV files found")
    
    # Main content area
    files = csv_manager.list_csv_files()
    
    if not files:
        st.warning("No CSV files found in the output directory.")
        st.info("Run the scraper first to generate some CSV files.")
        return
    
    # File selector
    selected_file = st.selectbox("Select a file to manage:", files)
    
    if not selected_file:
        return
    
    # Get file path
    file_path = csv_manager.get_file_path(selected_file)
    
    # Get file statistics
    stats = csv_manager.get_stats(selected_file)
    
    if not stats:
        st.error(f"Could not read file: {selected_file}")
        return
    
    # Display file info
    st.subheader("File Information")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**Rows:** {stats['rows']}")
    with col2:
        st.write(f"**Columns:** {stats['columns']}")
    with col3:
        st.write(f"**Size:** {stats['size_bytes'] / 1024:.2f} KB")
    
    # File actions
    st.subheader("Actions")
    action_col1, action_col2, action_col3 = st.columns(3)
    
    with action_col1:
        # Download button
        st.markdown(get_download_link(file_path, selected_file), unsafe_allow_html=True)
    
    with action_col2:
        # Fix phone numbers button
        if st.button("Fix Phone Numbers"):
            fixed = csv_manager.fix_phone_numbers(selected_file)
            if isinstance(fixed, int):
                if fixed > 0:
                    st.success(f"Fixed {fixed} phone numbers in scientific notation")
                else:
                    st.info("No phone numbers needed fixing")
            else:
                st.error("Failed to fix phone numbers")
    
    with action_col3:
        # Delete button with confirmation
        if st.button("Delete File"):
            st.session_state['confirm_delete'] = True
    
    # Handle delete confirmation
    if st.session_state.get('confirm_delete', False):
        st.warning(f"Are you sure you want to delete {selected_file}?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, Delete"):
                if csv_manager.delete_csv(selected_file):
                    st.success(f"Deleted {selected_file}")
                    st.session_state['confirm_delete'] = False
                    st.session_state['refresh'] += 1
                    time.sleep(1)
                    st.experimental_rerun()
                else:
                    st.error(f"Failed to delete {selected_file}")
        with col2:
            if st.button("Cancel"):
                st.session_state['confirm_delete'] = False
                st.experimental_rerun()
    
    # Display file contents
    st.subheader("File Contents")
    try:
        df = pd.read_csv(file_path)
        st.dataframe(df)
        
        # Column-specific statistics
        st.subheader("Column Analysis")
        
        # Phone numbers
        if 'phone' in df.columns:
            st.write("**Phone Number Statistics:**")
            phone_counts = df['phone'].value_counts()
            phone_not_found = (df['phone'] == 'Not found').sum()
            phone_found = len(df) - phone_not_found
            st.write(f"- Records with phone numbers: {phone_found}")
            st.write(f"- Records without phone numbers: {phone_not_found}")
        
        # Emails
        if 'email' in df.columns:
            st.write("**Email Statistics:**")
            email_counts = df['email'].value_counts()
            email_not_found = (df['email'] == 'Not found').sum()
            email_found = len(df) - email_not_found
            st.write(f"- Records with emails: {email_found}")
            st.write(f"- Records without emails: {email_not_found}")
        
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")

if __name__ == "__main__":
    main()
