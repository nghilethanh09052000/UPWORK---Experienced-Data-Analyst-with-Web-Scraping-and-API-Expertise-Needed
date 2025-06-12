import json
import os
import sys
import pandas as pd
import requests
from datetime import datetime
import time

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from config.settings import APAR_CSV_PATH

class LinkedInBatchTester:
    def __init__(self):
        self.headers = {
            'accept': 'application/vnd.linkedin.normalized+json+2.1',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US,en;q=0.9',
            'cookie': 'bcookie="v=2&b581617b-4845-46dc-88cb-fa89eaf2cfbf"; li_sugr=665ddb33-8c4d-4a35-8f74-f68edc700039; bscookie="v=1&2025022609095191d436e3-f794-42f2-81f1-2c9326080accAQEnwbyGJlzsiwEKaAMjAtKPUiCEUjsZ"; li_gc=MTswOzE3NDA4MjM2Njc7MjswMjHiMK4lo/LXWj+J3JFYqwPACJq7BiIWycJciDEcnu+U+Q==; g_state={"i_l":0}; timezone=Asia/Saigon; li_theme=light; li_theme_set=app; _guid=5f862a6c-3ee9-4a45-9e33-37c1148b825e; dfpfpt=97c85285a9e34a6da06525361e9f1e49; li_rm=AQGRgX3vL2pfXgAAAZWXW-s-3JuhnfD__qN47IfajslmdvfijmooNWV76_ngjvkjt_MV88I3tE3hVGxPhI0hWDc9xb0yXKmP2PiHRRCGOEzCdaaVNJjCmqNr; visit=v=1&M; liap=true; JSESSIONID="ajax:4103262043015182436"; lang=v=2&lang=en-us; PLAY_SESSION=eyJhbGciOiJIUzI1NiJ9.eyJkYXRhIjp7ImZsb3dUcmFja2luZ0lkIjoidm9UN3haRkpReFc5YTVGdERZZ08xUT09In0sIm5iZiI6MTc0NzE1MTI3OSwiaWF0IjoxNzQ3MTUxMjc5fQ.Bd73RRuJ9KDJ-NWzgy9oAI94xYhwvPPVIiuxs6FaXwA; fid=AQHlWoTrJ9NrPQAAAZb_v5qz5_HQJpYAEVpBjkxDdPA9dI0tm_T7y0pu7c0GL0wr7IH9Onpg5Dx6Pg; li_at=AQEDAUSBj58ASDWwAAABliib0QAAAAGXJWcl11YApMZI3d-JeD6Fj35RmJcCXiSpCMYm1YJWS0tl2UilPsIipB1N1Ap6bL2XRL1CeSTn_rDhC_xrZCEHfjSfQEaFNC6nV6WWSshws7AMf2Z08-CAedyS; AnalyticsSyncHistory=AQJUJqY1vigPFwAAAZcW19ha3Yil4I15bupBRzmHPu7s6xQBGbv0yr6h6nyMLGC90s4xH7OYsLed5BAfLgHgyA; __cf_bm=A1Q3Jwvwc4mz4r3a3ZpOEhc1bWZWDFinhn7NQQbjqrY-1748588296-1.0.1.1-6B4LHmWMbLZAjScIhvEbvXPzfswKQHaMa2Y4yJqsXOmWwJVYHuMvV5WownfNVGWlkIvJiSNP2LaZAkWW9TdepYMit074KcAF20KYCfWvF9I; sdui_ver=sdui-flagship:0.1.4947+sdui-flagship.production; fptctx2=taBcrIH61PuCVH7eNCyH0J9Fjk1kZEyRnBbpUW3FKs%252f1fBo4Xe1rmWxLZzA6LC0b02cGxePlPwCrm%252fOgYDbmEetjb1htMyqJw9HTDsiiY3NLd9sAjJ%252fEStYprhvhcAOLA%252banyVtKlEI1CavzfKaQ77gWATDrNiU8MYOvraLErcX3%252b2vRDeS%252bw%252bY7e%252fKJnRTRGaBZabmcEuN3e87h8wFxN5QyAa2USeYT2MQM7Lr%252bh%252f6%252fKfE4aeON%252bvkU%252bmt0t2a9VWwaOY%252fNxn9qAm0BkEpgL4T45nJJaQjp%252bEgrYhkXzvkqURDB9qpwHIbUUB6xpypwBxW0ksn3swmIZM5tK%252fwrigqHmZcoYRZCFj7Ibk3cqWw%253d; UserMatchHistory=AQLrWnyvHLYDRgAAAZcgCOd7UGSWAcafvp8v-uYoQq2JqWxfwJXOFUcypDFdK9D62iXyRiZgU5kBug; lms_ads=AQFqWO7HpQ7QEwAAAZcgCOi5SdpncHN-DinudbOP3xuq7HuSFPebaj2ABU_iH3B7rBZWa78jbYbkIawlALi37-_6rPFj0Aeu; lms_analytics=AQFqWO7HpQ7QEwAAAZcgCOi5SdpncHN-DinudbOP3xuq7HuSFPebaj2ABU_iH3B7rBZWa78jbYbkIawlALi37-_6rPFj0Aeu; lidc="b=OB99:s=O:r=O:a=O:p=O:g=1118:u=332:x=1:i=1748589144:t=1748671941:v=2:sig=AQGABwNMXEInYmHLW_J6X6Y4xoUs6A8O"',
            'csrf-token': 'ajax:4103262043015182436',
            'priority': 'u=1, i',
            'referer': 'https://www.linkedin.com/search/results/all/',
            'sec-ch-prefers-color-scheme': 'dark',
            'sec-ch-ua': '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0',
            'x-li-lang': 'en_US',
            'x-li-page-instance': 'urn:li:page:d_flagship3_search_srp_companies;mHZvCAPTREqD2r95FslMCA==',
            'x-li-pem-metadata': 'Voyager - Companies SRP=search-results',
            'x-li-track': '{"clientVersion":"1.13.35839","mpVersion":"1.13.35839","osName":"web","timezoneOffset":7,"timezone":"Asia/Saigon","deviceFormFactor":"DESKTOP","mpName":"voyager-web","displayDensity":2,"displayWidth":3024,"displayHeight":1964}',
            'x-restli-protocol-version': '2.0.0'
        }
        
        # Create test data directory if it doesn't exist
        os.makedirs('tests/test_data', exist_ok=True)
        
        # Load APAR data
        self.apar_data = pd.read_csv(APAR_CSV_PATH).head(10)  # Test with first 10 companies

    def search_company(self, company_name):
        """Search for a company on LinkedIn"""
        try:
            # Construct the API URL
            api_url = f"https://www.linkedin.com/voyager/api/graphql?variables=(start:0,origin:SWITCH_SEARCH_VERTICAL,query:(keywords:{company_name.replace(' ', '%20')},flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:resultType,value:List(COMPANIES))),includeFiltersInResponse:false))&queryId=voyagerSearchDashClusters.52fec77d08aa4598c8a056ca6bce6c11"
            
            # Make the request
            response = requests.get(api_url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error searching for {company_name}: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Exception searching for {company_name}: {str(e)}")
            return None

    def run_batch_test(self):
        """Run the LinkedIn crawler test on multiple companies"""
        results = []
        
        for _, row in self.apar_data.iterrows():
            company_name = row['Name']
            print(f"\nSearching for: {company_name}")
            
            # Search for company
            response_data = self.search_company(company_name)
            
            if response_data:
                # Save raw response
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                response_file = f'tests/test_data/linkedin_response_{company_name.replace(" ", "_")}_{timestamp}.json'
                
                with open(response_file, 'w', encoding='utf-8') as f:
                    json.dump(response_data, f, indent=2)
                
                # Extract relevant data (to be implemented based on response structure)
                company_data = {
                    'company_name': company_name,
                    'raw_response': response_file,
                    'parsed_data': None  # Will be implemented after analyzing response structure
                }
                
                results.append(company_data)
            
            # Add delay to avoid rate limiting
            time.sleep(2)
        
        # Save all results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f'tests/test_data/linkedin_batch_results_{timestamp}.json'
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nBatch test completed. Results saved to {results_file}")
        return results

if __name__ == '__main__':
    tester = LinkedInBatchTester()
    tester.run_batch_test() 