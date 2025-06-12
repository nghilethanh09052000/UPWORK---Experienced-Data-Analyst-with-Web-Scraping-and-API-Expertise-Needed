import sys
import os
from datetime import datetime
import logging
import json
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import queue

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.collectors.data_collector import DataCollector
from src.processors.data_processor import DataProcessor
from config.settings import OUTPUT_CSV_PATH

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Global variables for thread safety
csv_lock = Lock()
is_first_row = True
output_filename = None

def save_incremental_data(df, is_first=False):
    """Save data incrementally to CSV with thread safety"""
    global is_first_row, output_filename
    with csv_lock:
        if is_first:
            df.to_csv(output_filename, index=False, encoding='utf-8')
            is_first_row = False
        else:
            df.to_csv(output_filename, mode='a', header=False, index=False, encoding='utf-8')

def process_provider(args):
    """Process a single provider with its data"""
    index, row, collector, processor = args
    try:
        logging.info(f"Processing row {index + 1}: {row['Name']}")
        
        # Collect data for this row
        provider_data = {
            'ukprn': row['Ukprn'],
            'name': row['Name'],
            'application_type': row['ApplicationType'],
            'start_date': row['StartDate'],
            'status': row['Status']
        }
        
        # Get Ofsted data
        ofsted_data = collector.get_ofsted_data(row['Name'])
        if ofsted_data:
            provider_data.update(ofsted_data)
        
        # Get Companies House data
        companies_house_data = collector.get_companies_house_data(
            row['Name'],
            ofsted_data.get('address', '')
        )
        if companies_house_data:
            provider_data.update({
                'company_number': companies_house_data.get('company_number', ''),
                'company_name': companies_house_data.get('company_name', ''),
                'company_status': companies_house_data.get('company_status', ''),
                'incorporation_date': companies_house_data.get('incorporation_date', ''),
                'latest_accounts': companies_house_data.get('latest_accounts', ''),
                'turnover': companies_house_data.get('turnover', ''),
                'operating_profit': companies_house_data.get('operating_profit', ''),
                'net_profit': companies_house_data.get('net_profit', ''),
                'financial_year': companies_house_data.get('financial_year', ''),
                'persons_with_significant_control': companies_house_data.get('persons_with_significant_control', [])

            })
        
        # Process the data
        df_row = pd.DataFrame([provider_data])
        processed_row = processor.process_data(df_row)
        
        # Save incrementally
        save_incremental_data(processed_row, is_first=is_first_row)
        
        logging.info(f"Successfully processed and saved data for {row['Name']}")
        return True
        
    except Exception as e:
        logging.error(f"Error processing row {index + 1} ({row['Name']}): {str(e)}")
        return False

def main():
    try:
        # Initialize data collector
        logging.info("Initializing data collector...")
        collector = DataCollector()
        
        # Load APAR data first
        logging.info("Loading APAR data...")
        if not collector.load_apar_data():
            logging.error("Failed to load APAR data")
            return
            
        if collector.apar_data is None or len(collector.apar_data) == 0:
            logging.error("No APAR data loaded")
            return
            
        logging.info(f"Loaded {len(collector.apar_data)} records from APAR data")
        
        # Create output directory and filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        global output_filename
        output_filename = os.path.join('output', f"processed_data_{timestamp}.csv")
        os.makedirs(os.path.dirname(output_filename), exist_ok=True)
        
        # Initialize processor
        processor = DataProcessor(None)
        
        # Process data using thread pool
        logging.info("Starting parallel data collection and processing...")
        
        # Create a list of arguments for each provider
        args_list = [(index, row, collector, processor) 
                    for index, row in collector.apar_data.iterrows()]
        
        # Use ThreadPoolExecutor for parallel processing
        # Adjust max_workers based on your system's capabilities
        max_workers = min(5, len(args_list))  # Use up to 10 threads
        successful = 0
        failed = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_provider = {
                executor.submit(process_provider, args): args[1]['Name'] 
                for args in args_list
            }
            
            # Process results as they complete
            for future in as_completed(future_to_provider):
                provider_name = future_to_provider[future]
                try:
                    if future.result():
                        successful += 1
                    else:
                        failed += 1
                except Exception as e:
                    logging.error(f"Error processing {provider_name}: {str(e)}")
                    failed += 1
        
        logging.info(f"Data collection and processing completed:")
        logging.info(f"- Successfully processed: {successful}")
        logging.info(f"- Failed to process: {failed}")
        logging.info(f"Results saved to {output_filename}")
        
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main() 