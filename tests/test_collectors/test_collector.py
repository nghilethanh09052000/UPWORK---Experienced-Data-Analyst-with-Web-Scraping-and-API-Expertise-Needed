from data_collector import DataCollector
import pandas as pd

def test_functions():
    # Initialize the collector
    collector = DataCollector()
    
    # Test 1: Load APAR data
    print("\n=== Testing load_apar_data ===")
    success = collector.load_apar_data()
    if success:
        print("Successfully loaded APAR data")
        print("First few rows:")
        print(collector.apar_data.head())
    else:
        print("Failed to load APAR data")
    
    # Test 2: Get Ofsted data for a specific provider
    print("\n=== Testing get_ofsted_data ===")
    test_provider = "UNIVERSITY HOSPITAL SOUTHAMPTON NHS FOUNDATION TRUST"
    ofsted_data = collector.get_ofsted_data(test_provider)
    print(f"Ofsted data for {test_provider}:")
    print(ofsted_data)
    
    # Test 3: Get Companies House data
    print("\n=== Testing get_companies_house_data ===")
    companies_house_data = collector.get_companies_house_data(test_provider)
    print(f"Companies House data for {test_provider}:")
    print(companies_house_data)
    
    # Test 4: Try with a different provider
    print("\n=== Testing with another provider ===")
    test_provider2 = "MARY HARE T/A Mary Hare School"
    print(f"\nTesting Ofsted data for {test_provider2}")
    ofsted_data2 = collector.get_ofsted_data(test_provider2)
    print(ofsted_data2)
    
    print(f"\nTesting Companies House data for {test_provider2}")
    companies_house_data2 = collector.get_companies_house_data(test_provider2)
    print(companies_house_data2)

if __name__ == "__main__":
    test_functions() 