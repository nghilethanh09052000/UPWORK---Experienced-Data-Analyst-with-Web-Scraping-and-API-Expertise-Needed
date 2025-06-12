import pandas as pd
import json
import sys
import os

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from config.settings import PROFIT_BANDS

class DataProcessor:
    def __init__(self, data):
        self.data = data

    def get_profit_band(self, turnover):
        """Determine the profit band based on turnover"""
        if pd.isna(turnover) or turnover == '':
            return ''
        
        try:
            turnover = float(turnover)
            for min_val, max_val, band in PROFIT_BANDS:
                if min_val <= turnover < max_val:
                    return band
        except (ValueError, TypeError):
            return ''
        
        return ''

    def get_region(self, address):
        """Extract region from address"""
        if pd.isna(address) or address == '':
            return ''
        
        # Common UK regions
        regions = {
            'London': ['London', 'Greater London'],
            'South East': ['South East', 'Berkshire', 'Buckinghamshire', 'East Sussex', 'Hampshire', 'Isle of Wight', 'Kent', 'Oxfordshire', 'Surrey', 'West Sussex'],
            'South West': ['South West', 'Bristol', 'Cornwall', 'Devon', 'Dorset', 'Gloucestershire', 'Somerset', 'Wiltshire'],
            'East of England': ['East of England', 'Bedfordshire', 'Cambridgeshire', 'Essex', 'Hertfordshire', 'Norfolk', 'Suffolk'],
            'West Midlands': ['West Midlands', 'Birmingham', 'Coventry', 'Herefordshire', 'Shropshire', 'Staffordshire', 'Warwickshire', 'Worcestershire'],
            'East Midlands': ['East Midlands', 'Derbyshire', 'Leicestershire', 'Lincolnshire', 'Northamptonshire', 'Nottinghamshire', 'Rutland'],
            'North West': ['North West', 'Cheshire', 'Cumbria', 'Greater Manchester', 'Lancashire', 'Merseyside'],
            'North East': ['North East', 'Durham', 'Northumberland', 'Tyne and Wear'],
            'Yorkshire and the Humber': ['Yorkshire and the Humber', 'East Riding of Yorkshire', 'North Yorkshire', 'South Yorkshire', 'West Yorkshire'],
            'Wales': ['Wales'],
            'Scotland': ['Scotland'],
            'Northern Ireland': ['Northern Ireland']
        }
        
        address_str = str(address).lower()
        for region, keywords in regions.items():
            if any(keyword.lower() in address_str for keyword in keywords):
                return region
        
        return ''

    def clean_json_value(self, value):
        """Clean JSON values into readable strings"""
        if isinstance(value, dict):
            # Handle date format
            if all(k in value for k in ['year', 'month', 'day']):
                year = value.get('year', '')
                month = value.get('month', '')
                day = value.get('day', '')
                return f"{year}-{month if month else '01'}-{day if day else '01'}" if year else ''
            
            # Handle phone number format
            if 'number' in value:
                phone_number = value.get('number', '')
                extension = value.get('extension', '')
                return f"{phone_number} ext. {extension}" if extension else phone_number
            
            # For other dictionaries, convert to string
            return str(value)
        return value

    def process_data(self, data=None):
        """Process and enrich the data"""
        # Use provided data or self.data
        if data is not None:
            processed_data = data.copy()
        elif self.data is not None:
            processed_data = self.data.copy()
        else:
            return None

        # Process Companies House data
        if 'accounts' in processed_data.columns:
            processed_data['turnover'] = processed_data['accounts'].apply(
                lambda x: x.get('turnover', '') if isinstance(x, dict) else ''
            )
            processed_data['net_profit'] = processed_data['accounts'].apply(
                lambda x: x.get('net_profit', '') if isinstance(x, dict) else ''
            )
        else:
            # If no accounts column, check for direct turnover and net_profit columns
            if 'turnover' not in processed_data.columns:
                processed_data['turnover'] = ''
            if 'net_profit' not in processed_data.columns:
                processed_data['net_profit'] = ''


        # Clean up the data
        columns_to_keep = [
            'ukprn',
            'name',
            'application_type',
            'start_date',
            'status',
            'rating',
            'inspection_date',
            'company_number',
            'address',
            'turnover',
            'net_profit',
            'operating_profit',
            'financial_year',
            'company_status',
            'incorporation_date',
            'latest_accounts',
            'persons_with_significant_control'
        ]

        # Keep only the columns we want and reorder them
        processed_data = processed_data[columns_to_keep]

        # Clean any JSON values
        for col in processed_data.columns:
            processed_data[col] = processed_data[col].apply(self.clean_json_value)

        # Clean up any NaN values
        processed_data = processed_data.fillna('')

        return processed_data

    def format_address(self, address_dict):
        """Format address dictionary into a readable string"""
        if not isinstance(address_dict, dict):
            return ''
            
        address_parts = []
        
        # Add address lines
        if address_dict.get('address_line_1'):
            address_parts.append(address_dict['address_line_1'])
        if address_dict.get('address_line_2'):
            address_parts.append(address_dict['address_line_2'])
            
        # Add locality
        if address_dict.get('locality'):
            address_parts.append(address_dict['locality'])
            
        # Add postal code
        if address_dict.get('postal_code'):
            address_parts.append(address_dict['postal_code'])
            
        # Add country
        if address_dict.get('country'):
            address_parts.append(address_dict['country'])
            
        return ', '.join(address_parts) 