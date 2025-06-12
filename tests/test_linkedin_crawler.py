import json
import os
import sys
from datetime import datetime

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from collectors.linkedin_crawler import LinkedInCrawler

def test_linkedin_api():
    """Test the LinkedIn API response structure"""
    # Create test data directory if it doesn't exist
    os.makedirs('tests/test_data', exist_ok=True)

    # Test company name
    company_name = "YOUNG GLOUCESTERSHIRE LIMITED"
    print(f"\nSearching for company: {company_name}")
    
    # Initialize LinkedIn crawler
    crawler = LinkedInCrawler()
    
    try:
        # Search for company and get details
        company_data = crawler.search_company(company_name)
        
        if company_data:
            print("\nFound company data:")
            for key, value in company_data.items():
                print(f"{key}: {value}")
            
            # Save the data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            data_file = f'tests/test_data/linkedin_company_data_{timestamp}.json'
            
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(company_data, f, indent=2)
            
            print(f"\nCompany data saved to: {data_file}")
            return company_data
        else:
            print(f"\nNo data found for company: {company_name}")
            return None
            
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return None

if __name__ == '__main__':
    test_linkedin_api() 