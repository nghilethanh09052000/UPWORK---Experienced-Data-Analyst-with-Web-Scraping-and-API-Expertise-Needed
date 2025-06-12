import pandas as pd
import ast
from src.collectors.linkedin_crawler import LinkedInCrawler
import time
import random
from datetime import datetime
import os
import json

def process_psc_to_linkedin(csv_path: str):
    """Process PSC data and find LinkedIn profiles"""
    try:
        # Initialize LinkedIn crawler
        crawler = LinkedInCrawler()
        
        # Read the CSV file
        print(f"Reading CSV file: {csv_path}")
        df = pd.read_csv(csv_path)
        
        # Initialize lists to store results
        results = []
        
        # Create linkedin folder for storing data
        linkedin_dir = os.path.join(os.path.dirname(__file__), 'linkedin_data')
        os.makedirs(linkedin_dir, exist_ok=True)
        
        # Process each row
        for idx, row in df.iterrows():
            company_name = row['name']
            company_number = row['company_number']
            psc_data = row['persons_with_significant_control']
            
            print(f"\nProcessing company {idx + 1}/{len(df)}: {company_name}")
            
            # Skip if no PSC data
            if pd.isna(psc_data) or psc_data == '[]':
                print(f"No PSC data for {company_name}")
                continue
            
            try:
                # Parse PSC data from string to list
                psc_list = ast.literal_eval(psc_data)
                
                # Process each person
                for person in psc_list:
                    name = person.get('name', '')
                    if not name:
                        continue
                        
                    print(f"\nSearching for: {name} at {company_name}")
                    
                    # Search for company first
                    company_matches = crawler.search_company(company_name)
                    if not company_matches:
                        print(f"No LinkedIn company matches found for {company_name}")
                        continue
                        
                    # Get company ID
                    company_id = company_matches[0]['id']
                    
                    # Search for person at company
                    people_data = crawler.search_people(company_id, name)
                    
                    if people_data:
                        for person_data in people_data:
                            result = {
                                'company_name': company_name,
                                'company_number': company_number,
                                'psc_name': name,
                                'profile_url': person_data['profile_url']
                            }
                            results.append(result)
                            print(f"Found match: {name} - {person_data['profile_url']}")
                            
                            # Save individual result to JSON
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            result_file = os.path.join(linkedin_dir, f"{company_number}_{name.replace(' ', '_')}_{timestamp}.json")
                            with open(result_file, 'w') as f:
                                json.dump(result, f, indent=2)
                            print(f"Saved result to: {result_file}")
                    else:
                        print(f"No LinkedIn matches found for {name}")
                    
                    # Add delay to avoid rate limiting
                    # delay = random.uniform(2, 4)
                    # print(f"Waiting {delay:.1f} seconds...")
                    # time.sleep(delay)
            
            except Exception as e:
                print(f"Error processing PSC data for {company_name}: {str(e)}")
                continue
        
        # Create DataFrame from results
        if results:
            results_df = pd.DataFrame(results)
            
            # Save results to CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(linkedin_dir, f'linkedin_psc_matches_{timestamp}.csv')
            results_df.to_csv(output_file, index=False)
            print(f"\nSaved LinkedIn matches to: {output_file}")
            
            return results_df
        else:
            print("\nNo LinkedIn matches found")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Error processing PSC data: {str(e)}")
        return pd.DataFrame()

if __name__ == "__main__":
    # Path to the processed data CSV
    csv_path = "output/processed_data_20250606_185009.csv"
    
    # Process PSC data and find LinkedIn profiles
    results = process_psc_to_linkedin(csv_path) 