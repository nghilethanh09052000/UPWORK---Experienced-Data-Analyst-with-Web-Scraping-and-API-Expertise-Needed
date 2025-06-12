import os
import sys
import json
from datetime import datetime

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.collectors.companies_house_crawler import CompaniesHouseCrawler
from src.collectors.data_collector import DataCollector

def test_companies_house_crawler():
    """Test the Companies House crawler functionality"""
    # Test data
    test_cases = [
        {
            'name': 'SOUTHAMPTON ENGINEERING TRAINING ASSOCIATION LIMITED',
            'address': 'Tremona Road, Southampton, SO16 6YD'
        },
        {
            'name': 'TRAINING 2000 LIMITED',
            'address': 'Shadsworth Business Park, Blackburn, BB1 2PR'
        }
    ]
    
    # Initialize crawler
    crawler = CompaniesHouseCrawler()
    
    # Test each case
    results = []
    for case in test_cases:
        print(f"\nTesting company: {case['name']}")
        print(f"Address: {case['address']}")
        
        # Get company data
        company_data = crawler.search_company(case['name'], case['address'])
        
        if company_data:
            print("\nCompany Details:")
            print(f"Company Number: {company_data['company_number']}")
            print(f"Company Name: {company_data['company_name']}")
            print(f"Status: {company_data['company_status']}")
            print(f"Incorporation Date: {company_data['incorporation_date']}")
            
            print("\nRegistered Office:")
            for key, value in company_data['registered_office'].items():
                print(f"{key}: {value}")
            
            print("\nOfficers:")
            for officer in company_data['officers']:
                print(f"Name: {officer['name']}")
                print(f"Role: {officer['role']}")
                print(f"Appointed: {officer['appointed']}")
                if officer['resigned']:
                    print(f"Resigned: {officer['resigned']}")
                print("---")
            
            print("\nFinancial Data:")
            print(f"Latest Accounts: {company_data['latest_accounts']}")
            print(f"Turnover: {company_data['turnover']}")
            print(f"Net Profit: {company_data['net_profit']}")
        else:
            print("No company data found")
        
        results.append({
            'test_case': case,
            'result': company_data
        })
    
    # Save results to JSON file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'test_data/companies_house_test_results_{timestamp}.json'
    os.makedirs('test_data', exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nTest results saved to: {output_file}")

def test_data_collector():
    """Test the DataCollector with Companies House integration"""
    collector = DataCollector()
    
    # Test data
    test_cases = [
        {
            'name': 'SOUTHAMPTON ENGINEERING TRAINING ASSOCIATION LIMITED',
            'address': 'Tremona Road, Southampton, SO16 6YD'
        },
        {
            'name': 'TRAINING 2000 LIMITED',
            'address': 'Shadsworth Business Park, Blackburn, BB1 2PR'
        }
    ]
    
    results = []
    for case in test_cases:
        print(f"\nTesting DataCollector for: {case['name']}")
        
        # Get Ofsted data (which includes address)
        ofsted_data = collector.get_ofsted_data(case['name'])
        print("\nOfsted Data:")
        print(f"Rating: {ofsted_data['rating']}")
        print(f"Inspection Date: {ofsted_data['inspection_date']}")
        print(f"Address: {ofsted_data['address']}")
        
        # Get Companies House data using the address from Ofsted
        companies_house_data = collector.get_companies_house_data(
            case['name'],
            ofsted_data['address']
        )
        
        results.append({
            'test_case': case,
            'ofsted_data': ofsted_data,
            'companies_house_data': companies_house_data
        })
    
    # Save results to JSON file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'test_data/data_collector_test_results_{timestamp}.json'
    os.makedirs('test_data', exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nTest results saved to: {output_file}")

if __name__ == '__main__':
    print("Testing Companies House Crawler...")
    test_companies_house_crawler()
    
    print("\nTesting Data Collector...")
    test_data_collector() 