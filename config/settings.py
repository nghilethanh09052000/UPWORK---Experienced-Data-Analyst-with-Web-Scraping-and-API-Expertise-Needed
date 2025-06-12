import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
LINKEDIN_API_KEY = os.getenv('LINKEDIN_API_KEY', '')
COMPANIES_HOUSE_API_KEY = os.getenv('COMPANIES_HOUSE_API_KEY', '')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')

# File paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APAR_CSV_PATH = os.path.join(BASE_DIR, 'data', 'raw', 'apar-2025-05-23-10-47-10.csv')
OUTPUT_CSV_PATH = os.path.join(BASE_DIR, 'data', 'output', 'processed_data.csv')

# API URLs
COMPANIES_HOUSE_API_URL = 'https://api.company-information.service.gov.uk'
OFSTED_API_URL = 'https://reports.ofsted.gov.uk/api/v1'

# Profit bands for categorization
PROFIT_BANDS = [
    (float('-inf'), 0, 'Loss'),
    (0, 100000, '0-100k'),
    (100000, 500000, '100k-500k'),
    (500000, 1000000, '500k-1M'),
    (1000000, float('inf'), '1M+')
]

# Logging Configuration
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = os.path.join(BASE_DIR, 'logs', 'app.log') 