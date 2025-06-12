import requests
from requests.auth import HTTPBasicAuth
import json
import os
import sys
from typing import Dict, List, Optional, Union, Any

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from config.settings import COMPANIES_HOUSE_API_URL, COMPANIES_HOUSE_API_KEY
from utils.parse_financials import extract_financial_data

class CompaniesHouseCrawler:
    
    def __init__(self) -> None:
        self.api_url: str = COMPANIES_HOUSE_API_URL
        self.api_key: str = COMPANIES_HOUSE_API_KEY
        self.auth: HTTPBasicAuth = HTTPBasicAuth(self.api_key, '')

    def search_company(self, company_name: str, address: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Search for a company by name"""
        try:
            # Search for company
            search_url = f"{self.api_url}/search/companies"
            params = {'q': company_name}
            
            print(f"Searching Companies House for: {company_name}")
            response = requests.get(
                search_url,
                auth=self.auth,
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('items'):
                    for item in data['items']:
                        if item.get('title', '').lower().strip() == company_name.lower().strip():
                            # Found exact name match
                            print(f"Found exact name match: {item['title']}")
                            company_number = item.get('links', {}).get('self', '').split('/')[-1]
                            if company_number:
                                return self.get_company_details(company_number)
                            else:
                                print("Error: Could not extract company number from response")
                                return None
            
            print(f"No exact match found for: {company_name}")
            return None
            
        except Exception as e:
            print(f"Error searching company: {str(e)}")
            return None

    def _download_pdf(self, url: str, company_number: str, company_name: str) -> Optional[str]:
        """Download PDF from Companies House"""
        try:
            # Create documents directory if it doesn't exist
            documents_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'documents')
            os.makedirs(documents_dir, exist_ok=True)
            
            # Clean company name for filename
            safe_company_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_company_name = safe_company_name.replace(' ', '_')
            
            # Check if file already exists
            pdf_path = os.path.join(documents_dir, f"{safe_company_name}_{company_number}_accounts.pdf")
            if os.path.exists(pdf_path):
                print(f"PDF already exists at: {pdf_path}")
                return pdf_path
            
            print(f"Downloading PDF from: {url}")
            # First get the document metadata
            metadata_response = requests.get(url, auth=self.auth)
            
            if metadata_response.status_code == 200:
                metadata = metadata_response.json()
                # Get the actual document URL from metadata
                if metadata.get('links', {}).get('document'):
                    doc_url = metadata['links']['document']
                    if not doc_url.startswith('http'):
                        doc_url = f"https://document-api.company-information.service.gov.uk{doc_url}"
                    
                    print(f"Getting actual document from: {doc_url}")
                    doc_response = requests.get(doc_url, auth=self.auth)
                    
                    if doc_response.status_code == 200:
                        # Save the PDF with company name
                        with open(pdf_path, 'wb') as f:
                            f.write(doc_response.content)
                        print(f"PDF saved to: {pdf_path}")
                        return pdf_path
                    else:
                        print(f"Failed to download document: {doc_response.status_code}")
                else:
                    print("No document URL found in metadata")
            else:
                print(f"Failed to get document metadata: {metadata_response.status_code}")
            return None
                
        except Exception as e:
            print(f"Error downloading PDF: {str(e)}")
            return None

    def _get_company_basic_info(self, company_number: str) -> Optional[Dict[str, Any]]:
        """Get basic company information"""
        try:
            company_url = f"{self.api_url}/company/{company_number}"
            print(f"Getting company details from: {company_url}")
            response = requests.get(company_url, auth=self.auth)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get company details: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error getting company details: {str(e)}")
            return None

    def _get_persons_with_significant_control(self, company_number: str) -> List[Dict[str, Any]]:
        """Get persons with significant control with specific fields"""
        try:
            psc_url = f"{self.api_url}/company/{company_number}/persons-with-significant-control"
            print(f"Getting persons with significant control from: {psc_url}")
            response = requests.get(psc_url, auth=self.auth)
            
            if response.status_code == 200:
                psc_data = response.json().get('items', [])
                formatted_psc = []
                
                for psc in psc_data:
                    if not psc.get('ceased'):
                        # Format address as string
                        address_parts = []
                        address = psc.get('address', {})
                        if address.get('premises'):
                            address_parts.append(address['premises'])
                        if address.get('address_line_1'):
                            address_parts.append(address['address_line_1'])
                        if address.get('locality'):
                            address_parts.append(address['locality'])
                        if address.get('postal_code'):
                            address_parts.append(address['postal_code'])
                        if address.get('country'):
                            address_parts.append(address['country'])
                        formatted_address = ', '.join(address_parts)

                        # Format name - remove titles
                        full_name = psc.get('name', '')
                        # Remove common titles
                        titles = ['Mr ', 'Mrs ', 'Miss ', 'Ms ', 'Dr ', 'Prof ', 'Sir ', 'Lady ']
                        for title in titles:
                            full_name = full_name.replace(title, '')
                        # Remove any extra spaces
                        full_name = ' '.join(full_name.split())

                        # Extract only required fields
                        formatted_psc.append({
                            'name': full_name,
                            'date_of_birth': f"{psc.get('date_of_birth', {}).get('month', '')}/{psc.get('date_of_birth', {}).get('year', '')}",
                            'country_of_residence': psc.get('country_of_residence', ''),
                            'nationality': psc.get('nationality', ''),
                            'address': formatted_address
                        })
                
                print(f"Found {len(formatted_psc)} persons with significant control")
                return formatted_psc
            else:
                print(f"Could not get persons with significant control: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error getting PSC data: {str(e)}")
            return []

    def _get_filing_history(self, company_number: str) -> Optional[Dict[str, Any]]:
        """Get company filing history"""
        try:
            filing_url = f"{self.api_url}/company/{company_number}/filing-history"
            print(f"Getting filing history from: {filing_url}")
            response = requests.get(filing_url, auth=self.auth)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get filing history: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error getting filing history: {str(e)}")
            return None

    def _extract_financial_data(self, filing_data: Dict[str, Any], company_number: str, company_name: str) -> Dict[str, str]:
        """Extract financial data from filing history"""
        financial_data: Dict[str, str] = {
            'latest_accounts': '',
            'turnover': '',
            'operating_profit': '',
            'net_profit': '',
            'financial_year': ''
        }
        
        try:
            for filing in filing_data.get('items', []):
                if filing.get('type') == 'AA':  # AA is the code for full accounts
                    financial_data['latest_accounts'] = filing.get('date', '')
                    
                    # Get the document URL
                    if filing.get('links', {}).get('document_metadata'):
                        doc_url = filing['links']['document_metadata']
                        if not doc_url.startswith('http'):
                            doc_url = f"https://document-api.company-information.service.gov.uk{doc_url}"
                        
                        # Download and parse the PDF
                        pdf_path = self._download_pdf(doc_url, company_number, company_name)
                        if pdf_path:
                            try:
                                # Use parse_financials to extract data
                                extracted_data = extract_financial_data(pdf_path)
                                financial_data['turnover'] = extracted_data.get('turnover', '')
                                financial_data['operating_profit'] = extracted_data.get('operating_profit', '')
                                financial_data['net_profit'] = extracted_data.get('net_profit', '')
                                financial_data['financial_year'] = extracted_data.get('financial_year', '')
                            except Exception as e:
                                print(f"Error parsing financial data: {str(e)}")
                    break
                    
        except Exception as e:
            print(f"Error extracting financial data: {str(e)}")
            
        return financial_data

    def get_company_details(self, company_number: str) -> Optional[Dict[str, Any]]:
        """Get detailed company information including officers and financial data"""
        try:
            # Get basic company information
            company_data = self._get_company_basic_info(company_number)
            if not company_data:
                return None
                
            company_name = company_data.get('company_name', '')
            
            # Get persons with significant control
            psc_data = self._get_persons_with_significant_control(company_number)
            
            # Get filing history and extract financial data
            filing_data = self._get_filing_history(company_number)
            financial_data = self._extract_financial_data(filing_data, company_number, company_name) if filing_data else {
                'latest_accounts': '',
                'turnover': '',
                'operating_profit': '',
                'net_profit': '',
                'financial_year': ''
            }
            
            # financial_data = {
            #     'latest_accounts': '',
            #     'turnover': '',
            #     'operating_profit': '',
            #     'net_profit': '',
            #     'financial_year': ''
            # }
        
            
            
            return {
                'company_number': company_number,
                'company_name': company_name,
                'registered_office': company_data.get('registered_office_address', {}),
                'company_status': company_data.get('company_status', ''),
                'incorporation_date': company_data.get('date_of_creation', ''),
                'persons_with_significant_control': psc_data,
                **financial_data
            }
            
        except Exception as e:
            print(f"Error getting company details: {str(e)}")
            return None

    def _format_address(self, address_dict: Dict[str, str]) -> str:
        """Format address dictionary into a readable string"""
        if not isinstance(address_dict, dict):
            return ''
            
        address_parts = []
        
        # Add premises if available
        if address_dict.get('premises'):
            address_parts.append(address_dict['premises'])
            
        # Add address lines
        if address_dict.get('address_line_1'):
            address_parts.append(address_dict['address_line_1'])
        if address_dict.get('address_line_2'):
            address_parts.append(address_dict['address_line_2'])
            
        # Add locality
        if address_dict.get('locality'):
            address_parts.append(address_dict['locality'])
            
        # Add region
        if address_dict.get('region'):
            address_parts.append(address_dict['region'])
            
        # Add postal code
        if address_dict.get('postal_code'):
            address_parts.append(address_dict['postal_code'])
            
        # Add country
        if address_dict.get('country'):
            address_parts.append(address_dict['country'])
            
        return ', '.join(address_parts) 