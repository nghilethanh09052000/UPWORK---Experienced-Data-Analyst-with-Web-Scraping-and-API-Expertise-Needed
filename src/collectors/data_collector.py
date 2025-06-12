import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import json
import urllib.parse
import os
import sys

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from config.settings import (
    APAR_CSV_PATH,
    COMPANIES_HOUSE_API_URL,
    COMPANIES_HOUSE_API_KEY
)

class DataCollector:
    def __init__(self):
        self.apar_data = None

    def load_apar_data(self):
        """Load the APAR CSV data"""
        try:
            self.apar_data = pd.read_csv(APAR_CSV_PATH)
            return True
        except Exception as e:
            print(f"Error loading APAR data: {str(e)}")
            return False

    def get_ofsted_data(self, provider_name):
        """Get Ofsted inspection data for a provider"""
        try:
            # Encode the provider name for URL
            encoded_name = urllib.parse.quote(provider_name)
            search_url = f"https://reports.ofsted.gov.uk/search?q={encoded_name}&location=&radius=&latest_report_date_start=&latest_report_date_end=&status%5B%5D=1"
            
            print(f"Searching Ofsted for provider: {provider_name}")
            response = requests.get(search_url)
            
            if response.status_code != 200:
                print(f"Failed to get search results for {provider_name}")
                return {
                    'rating': '',
                    'inspection_date': '',
                    'address': ''
                }
            
            # Parse the search results
            soup = BeautifulSoup(response.text, 'html.parser')
            results_list = soup.find('ul', class_='results-list')
            
            if not results_list:
                print(f"No search results found for {provider_name}")
                return {
                    'rating': '',
                    'inspection_date': '',
                    'address': ''
                }
            
            # Find the exact match for the provider name
            provider_link = None
            provider_address = None
            for result in results_list.find_all('li', class_='search-result'):
                result_name = result.find('h3', class_='search-result__title').find('a').text.strip()
                if result_name.lower() == provider_name.lower():
                    provider_link = result.find('h3', class_='search-result__title').find('a')['href']
                    # Get the address
                    address_elem = result.find('address', class_='search-result__address')
                    if address_elem:
                        provider_address = address_elem.text.strip()
                    break
            
            if not provider_link:
                print(f"No exact match found for {provider_name}")
                return {
                    'rating': '',
                    'inspection_date': '',
                    'address': ''
                }
            
            # Get the provider details page
            provider_url = f"https://reports.ofsted.gov.uk{provider_link}"
            provider_response = requests.get(provider_url)
            
            if provider_response.status_code != 200:
                print(f"Failed to get provider details for {provider_name}")
                return {
                    'rating': '',
                    'inspection_date': '',
                    'address': provider_address or ''
                }
            
            # Parse the provider details page
            provider_soup = BeautifulSoup(provider_response.text, 'html.parser')
            
            # Get the overall rating
            rating_div = provider_soup.find('div', class_='subjudgements__overall')
            if not rating_div:
                print(f"No rating information found for {provider_name}")
                return {
                    'rating': '',
                    'inspection_date': '',
                    'address': provider_address or ''
                }
            
            # Extract rating and date
            rating = rating_div.find('strong').text.strip()
            date_text = rating_div.find('p').text.strip()
            # Clean up the date by removing "was:" and any extra whitespace
            inspection_date = date_text.split('on ')[-1].replace('was:', '').strip()
            
            print(f"Ofsted data for {provider_name}: Rating - {rating}, Inspection Date - {inspection_date}, Address - {provider_address}")
            
            return {
                'rating': rating,
                'inspection_date': inspection_date,
                'address': provider_address or ''
            }
            
        except Exception as e:
            print(f"Error getting Ofsted data for {provider_name}: {str(e)}")
            return {
                'rating': '',
                'inspection_date': '',
                'address': ''
            }

    def get_companies_house_data(self, company_name, address=None):
        """Get Companies House data for a company including financial information"""
        try:
            from collectors.companies_house_crawler import CompaniesHouseCrawler
            crawler = CompaniesHouseCrawler()
            company_data = crawler.search_company(company_name, address)
            
            if company_data:
                return company_data
            
            return {
                'company_number': '',
                'company_name': '',
                'registered_office': {},
                'company_status': '',
                'incorporation_date': '',
                'latest_accounts': '',
                'turnover': '',
                'net_profit': '',
                'operating_profit': '',
                'financial_year': '',
                'persons_with_significant_control': []
            }
            
        except Exception as e:
            print(f"Error getting Companies House data for {company_name}: {str(e)}")
            return {
                'company_number': '',
                'company_name': '',
                'registered_office': {},
                'company_status': '',
                'incorporation_date': '',
                'latest_accounts': '',
                'turnover': '',
                'net_profit': '',
                'operating_profit': '',
                'financial_year': '',
                'persons_with_significant_control': []
            }

    def collect_all_data(self):
        """Collect all data for each provider"""
        if not self.load_apar_data():
            return None

        enriched_data = []
        
        for _, row in self.apar_data.iterrows():
            provider_data = {
                'ukprn': row['Ukprn'],
                'name': row['Name'],
                'application_type': row['ApplicationType'],
                'start_date': row['StartDate'],
                'status': row['Status']
            }
            
            # Get Ofsted data
            ofsted_data = self.get_ofsted_data(row['Name'])
            if ofsted_data:
                provider_data.update(ofsted_data)
            
            # Get Companies House data using the address from Ofsted
            companies_house_data = self.get_companies_house_data(
                row['Name'],
                ofsted_data.get('address', '')  # Pass the address from Ofsted
            )
            if companies_house_data:
                provider_data.update({
                    'company_number': companies_house_data.get('company_number', ''),
                    'company_address': ofsted_data.get('address', '') ,
                    'company_name': companies_house_data.get('company_name', ''),
                    'registered_office': str(companies_house_data.get('registered_office', {})),
                    'company_status': companies_house_data.get('company_status', ''),
                    'incorporation_date': companies_house_data.get('incorporation_date', ''),
                    'persons_with_significant_control': companies_house_data.get('persons_with_significant_control', []),
                    'latest_accounts': companies_house_data.get('latest_accounts', ''),
                    'turnover': companies_house_data.get('turnover', ''),
                    'operating_profit': companies_house_data.get('operating_profit', ''),
                    'net_profit': companies_house_data.get('net_profit', ''),
                    'financial_year': companies_house_data.get('financial_year', '')
                })
            
            enriched_data.append(provider_data)
        
        # Create DataFrame
        df = pd.DataFrame(enriched_data)
        
        # Convert array fields to proper format
        if 'persons_with_significant_control' in df.columns:
            df['persons_with_significant_control'] = df['persons_with_significant_control'].apply(
                lambda x: x if isinstance(x, list) else []
            )
        
        return df 