import pdfplumber
import re
from pprint import pprint
import PyPDF2
import pytesseract
from pdf2image import convert_from_path
import io
import os
from bs4 import BeautifulSoup
import pandas as pd

def detect_file_type(file_path: str) -> str:
    """Detect the actual content type of the file"""
    try:
        # Read first few bytes of file
        with open(file_path, 'rb') as f:
            header = f.read(2048)
            
        # Check for XHTML/IXBRL content
        if b'<?xml' in header or b'<html' in header:
            return 'xhtml'
            
        # Check for PDF content
        if header.startswith(b'%PDF'):
            return 'pdf'
            
        # If we can't determine, assume it's a PDF that needs OCR
        return 'pdf_ocr'
    except Exception as e:
        print(f"Error detecting file type: {str(e)}")
        return 'pdf_ocr'

def extract_text_from_xhtml(file_path: str) -> str:
    """Extract text from XHTML/IXBRL file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Parse XHTML
        soup = BeautifulSoup(content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Get text
        text = soup.get_text(separator='\n', strip=True)
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    except Exception as e:
        print(f"Error extracting text from XHTML: {str(e)}")
        return ""

def extract_text_with_pdfplumber(pdf_path):
    """Extract text using pdfplumber"""
    print("\n=== Trying pdfplumber ===")
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for i, page in enumerate(pdf.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                    print(f"Page {i+1} text length: {len(page_text)}")
            except Exception as e:
                print(f"Error with pdfplumber on page {i+1}: {str(e)}")
        return text

def extract_text_with_pypdf2(pdf_path):
    """Extract text using PyPDF2"""
    print("\n=== Trying PyPDF2 ===")
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for i, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                    print(f"Page {i+1} text length: {len(page_text)}")
            except Exception as e:
                print(f"Error with PyPDF2 on page {i+1}: {str(e)}")
        return text

def extract_text_with_ocr(pdf_path):
    """Extract text using OCR (Tesseract)"""
    print("\n=== Trying OCR with Tesseract ===")
    try:
        # Convert PDF to images
        images = convert_from_path(pdf_path)
        text = ""
        for i, image in enumerate(images):
            try:
                # Extract text directly from image using OCR
                page_text = pytesseract.image_to_string(image)
                if page_text:
                    text += page_text + "\n"
                    print(f"Page {i+1} text length: {len(page_text)}")
            except Exception as e:
                print(f"Error with OCR on page {i+1}: {str(e)}")
        return text
    except Exception as e:
        print(f"Error converting PDF to images: {str(e)}")
        return ""

def find_financial_table(soup):
    """Find tables that likely contain financial data"""
    financial_keywords = [
        'turnover', 'revenue', 'sales', 'income',
        'operating', 'profit', 'loss',
        'net', 'total', 'balance',
        'assets', 'liabilities', 'equity'
    ]
    
    # Find all tables
    all_tables = soup.find_all('table')
    financial_tables = []
    
    for table in all_tables:
        # Get all text from the table
        table_text = table.get_text().lower()
        
        # Check if table contains financial keywords
        if any(keyword in table_text for keyword in financial_keywords):
            financial_tables.append(table)
    
    return financial_tables

def parse_table_row(row):
    """Parse a table row to extract label and values"""
    try:
        # Get all cells
        cells = row.find_all(['td', 'th'])
        if not cells:
            return None, None
            
        # Find the label cell (usually the first cell or has specific styling)
        label_cell = None
        for cell in cells:
            # Check if cell contains common financial labels
            cell_text = cell.get_text().strip().lower()
            if any(keyword in cell_text for keyword in ['turnover', 'revenue', 'sales', 'operating', 'profit', 'loss', 'net']):
                label_cell = cell
                break
        
        # If no specific label found, use first cell
        if not label_cell:
            label_cell = cells[0]
            
        label = label_cell.get_text().strip()
        
        # Find value cells (usually right-aligned or contain numbers)
        value_cells = []
        for cell in cells:
            cell_text = cell.get_text().strip()
            # Check if cell contains numbers or currency symbols
            if re.search(r'[\d£$€,.-]', cell_text):
                value_cells.append(cell_text)
        
        return label, value_cells
    except Exception as e:
        print(f"Error parsing table row: {str(e)}")
        return None, None

def extract_table_data(text):
    """Extract data from tables in the text"""
    try:
        # Parse HTML
        soup = BeautifulSoup(text, 'html.parser')
        
        # Find tables with financial data
        tables = find_financial_table(soup)
        if not tables:
            return {}
            
        financial_data = {
            'turnover': None,
            'operating_profit': None,
            'net_profit': None,
            'financial_year': None
        }
        
        # Process each table
        for table in tables:
            # Find all rows (including header rows)
            rows = table.find_all(['tr', 'thead', 'tbody'])
            
            # First try to find header row to get column indices
            header_indices = {}
            for row in rows:
                header_cells = row.find_all(['th', 'td'])
                for i, cell in enumerate(header_cells):
                    cell_text = cell.get_text().strip().lower()
                    if 'turnover' in cell_text or 'revenue' in cell_text or 'sales' in cell_text:
                        header_indices['turnover'] = i
                    elif 'operating' in cell_text:
                        header_indices['operating'] = i
                    elif 'net' in cell_text and ('profit' in cell_text or 'loss' in cell_text):
                        header_indices['net'] = i
                    elif 'year' in cell_text or 'period' in cell_text:
                        header_indices['year'] = i
            
            # Process data rows
            for row in rows:
                label, values = parse_table_row(row)
                if not label or not values:
                    continue
                    
                # Clean up label
                label = label.lower().strip()
                
                # Get the first value (most recent year)
                value = values[0] if values else None
                if not value:
                    continue
                    
                # Clean up value
                value = value.replace('(', '-').replace(')', '')
                value = re.sub(r'[^\d.-]', '', value)
                
                # Map label to financial data
                if 'turnover' in label or 'revenue' in label or 'sales' in label:
                    financial_data['turnover'] = value
                elif 'operating' in label and ('profit' in label or 'loss' in label):
                    financial_data['operating_profit'] = value
                elif 'net' in label and ('profit' in label or 'loss' in label):
                    financial_data['net_profit'] = value
                elif 'profit' in label and 'year' in label:
                    financial_data['net_profit'] = value
                    
        return financial_data
    except Exception as e:
        print(f"Error extracting table data: {str(e)}")
        return {}

def extract_financial_data(file_path: str) -> dict:
    """Extract financial data from file"""
    print(f"Opening file: {file_path}")
    
    # Detect file type
    file_type = detect_file_type(file_path)
    print(f"Detected file type: {file_type}")
    
    # Initialize financial data
    financial_data = {
        'turnover': None,
        'operating_profit': None,
        'net_profit': None,
        'financial_year': None,
        'raw_text': None
    }
    
    # Extract text based on file type
    if file_type == 'xhtml':
        text = extract_text_from_xhtml(file_path)
    else:
        # Try PDF extraction methods
        text = extract_text_with_pdfplumber(file_path)
        if not text or len(text.strip()) < 100:
            text = extract_text_with_ocr(file_path)
    
    if text:
        print(f"\nExtracted text length: {len(text)} characters")
        financial_data['raw_text'] = text[:1000]
        
        # Create text directory if it doesn't exist
        text_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'text')
        os.makedirs(text_dir, exist_ok=True)
        
        # Get company name from file path
        file_name = os.path.basename(file_path)
        company_name = file_name.split('_')[0]
        
        # Save the extracted text
        text_path = os.path.join(text_dir, f"{company_name}.txt")
        with open(text_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"\nFull extracted text saved to '{text_path}'")
        
        # Try to extract data from tables first
        table_data = extract_table_data(text)
        if any(table_data.values()):
            print("Found data in tables:")
            for key, value in table_data.items():
                if value:
                    financial_data[key] = value
                    print(f"{key}: {value}")
        
        # If we didn't get all data from tables, try regex patterns
        if not all(financial_data.values()):
            # Define regex patterns
            turnover_patterns = [
                r"(?:turnover|revenue|sales|total income)(?:\s*:)?\s*[£]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
                r"£\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:turnover|revenue|sales)",
                r"(?:turnover|revenue|sales)\s*\([^)]*\)\s*[£]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)"
            ]
            
            operating_profit_patterns = [
                r"(?:operating profit|operating surplus|operating income)(?:\s*:)?\s*[£]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
                r"£\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:operating profit|operating surplus)",
                r"(?:operating profit|operating surplus)\s*\([^)]*\)\s*[£]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
                r"(?:operating (?:profit|loss))(?:\s*:)?\s*[£]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)"
            ]
            
            net_profit_patterns = [
                r"(?:net profit|profit for the year|net income|profit after tax)(?:\s*:)?\s*[£]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
                r"£\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:net profit|profit for the year)",
                r"(?:net profit|profit for the year)\s*\([^)]*\)\s*[£]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
                r"(?:profit|income) for the (?:year|period)(?:\s*:)?\s*[£]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)"
            ]
            
            year_patterns = [
                r"(?:year|period) ended\s+(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})",
                r"(?:year|period) to\s+(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})",
                r"for the (?:year|period) ended\s+(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})",
                r"as at\s+(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})",
                r"balance sheet as at\s+(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})"
            ]
            
            # Try to find turnover if not found in tables
            if not financial_data['turnover']:
                for pattern in turnover_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        value = match.group(1).replace(',', '')
                        if not financial_data['turnover'] or float(value) > float(financial_data['turnover']):
                            financial_data['turnover'] = value
                            print(f"Found turnover: {financial_data['turnover']}")
            
            # Try to find operating profit if not found in tables
            if not financial_data['operating_profit']:
                for pattern in operating_profit_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        value = match.group(1).replace(',', '')
                        if not financial_data['operating_profit'] or float(value) > float(financial_data['operating_profit']):
                            financial_data['operating_profit'] = value
                            print(f"Found operating profit: {financial_data['operating_profit']}")
            
            # Try to find net profit if not found in tables
            if not financial_data['net_profit']:
                for pattern in net_profit_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        value = match.group(1).replace(',', '')
                        if not financial_data['net_profit'] or float(value) > float(financial_data['net_profit']):
                            financial_data['net_profit'] = value
                            print(f"Found net profit: {financial_data['net_profit']}")
            
            # Try to find financial year if not found in tables
            if not financial_data['financial_year']:
                for pattern in year_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        financial_data['financial_year'] = match.group(1)
                        print(f"Found financial year: {financial_data['financial_year']}")
                        break
    else:
        print("No text could be extracted from the file")
    
    return financial_data

if __name__ == "__main__":
    pdf_path = "document.pdf"
    result = extract_financial_data(pdf_path)
    print("\nExtracted financial data:")
    print(f"Turnover: {result['turnover']}")
    print(f"Operating Profit: {result['operating_profit']}")
    print(f"Net Profit: {result['net_profit']}")
    print(f"Financial Year: {result['financial_year']}") 