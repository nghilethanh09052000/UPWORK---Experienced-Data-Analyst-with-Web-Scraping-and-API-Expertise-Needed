import requests
import time
import random
import logging
import json
import pandas as pd
from urllib.parse import quote
from datetime import datetime

class LinkedInCrawler:
    def __init__(self):
        self.headers = {
            'accept': 'application/vnd.linkedin.normalized+json+2.1',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US,en;q=0.9',
            'cookie': 'bcookie="v=2&247fb8e3-2d97-4cbf-85b0-364a704711b0"; bscookie="v=1&202503191245500d2f9d12-65e5-4cc8-8de3-b2a03821879cAQH02nke8uBHbvTS85YfDBX0cb1OgpDv"; li_rm=AQEdHjWoFqssEQAAAZWucYPGexOYMtQUUb73Qqw3A_x3l8q1Ff7oEnEV2EAZnPIR4H1_n_oqTlChkVJXpfj4PMkLDEkrZKXSpsK2s_R08F4sYZyz7gL2Ot9j; g_state={"i_l":0}; li_theme=light; li_theme_set=app; li_sugr=d7be2f64-bfd3-452a-9b44-538817e05074; _guid=0f0794ff-c00f-4ffc-ab5f-3c5af4a1b519; dfpfpt=2696e41c85b9496abdeaa1c66f9b5e28; visit=v=1&M; liap=true; JSESSIONID="ajax:5695997962284638174"; li_at=AQEDAVizm2kAIwMcAAABlbCRZoAAAAGXUnkSO1YAnCUf5kLGE04E4Zs4Y46mxFQSga9xQUKo8iCSsjjmwbR231hqoMyUOc2UWkrEPekWoCglP-_kAS5KyyMSJNnTdXvKDc9KxVSp1EIdMeYjvtr27YaG; timezone=Asia/Saigon; sdui_ver=sdui-flagship:0.1.5106+sdui-flagship.production; AnalyticsSyncHistory=AQLud-l78nrU7wAAAZdLDfBNL9r0f6Hb230rHCoEPu3M5Z2kb6mI5ESSEGJ6n9wiTVq3nMaTbTgFvHxHGucVuQ; lms_ads=AQHiQjycnq8WhgAAAZdLDfGzTbDHWVHa3c6ZPSSBYXO6KWNhF6CH9tAVX7yU3U-YbSWGd4eRx_rbREnH67a3csxwT0QiCpq7; lms_analytics=AQHiQjycnq8WhgAAAZdLDfGzTbDHWVHa3c6ZPSSBYXO6KWNhF6CH9tAVX7yU3U-YbSWGd4eRx_rbREnH67a3csxwT0QiCpq7; aam_uuid=88106608129888270480981408920743877337; __cf_bm=IjpTLQ_jEBDEgEpp_5IGJ7V3icvyNhKyCIdz5bG8_dE-1749311019-1.0.1.1-gowM4J2DJSg2v4Uxgny6pcREfOk47O6FEO_3a.Vxj_3t87GpYVd1K2JTm9xDCWHBEjJvmCFgHVLMghpuSfskDqjwLvMv7O6rdUer36akfWA; lang=v=2&lang=en-us; li_mc=MTswOzE3NDkzMTI0NTE7MTswMjEEfzg2cj+h00lpA6+I2t1cbtunSw9yDLrmEWiadNbxZw==; AMCVS_14215E3D5995C57C0A495C55%40AdobeOrg=1; AMCV_14215E3D5995C57C0A495C55%40AdobeOrg=-637568504%7CMCIDTS%7C20247%7CMCMID%7C88301321526479232990959694473747786002%7CMCAAMLH-1749917254%7C3%7CMCAAMB-1749917254%7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y%7CMCOPTOUT-1749319654s%7CNONE%7CvVersion%7C5.1.1%7CMCCIDH%7C1293343068; fptctx2=taBcrIH61PuCVH7eNCyH0MJojnuUODHcZ6x9WoxhgClWbqUNstdGzdX%252fSgkmg2kmn%252fE%252bQXe0kx1tm1mVGtrSrUIkuEpk6KTCOPLHcrCQoLIuSMxMYnjYlacZKKK%252bch9B4kfo88BACQDMI3nVEvi9BqcninntPuZVW8Dox91oCabq1j6wAaWlkOgy%252bexui9%252bpvSpOGU5wfQKurDO28iZA3wlKoOFGQbCow1ptIWG3ZxFAJ940JwxQDBxEOUw1aMTYW8W6xPBBb%252fQ%252bKs8L1c%252fRZUQcwjmU%252fL0Lx56Zw%252fy3uvMfGMv07gB17RozYaoORH94EICjvDKjEQkLZlM4kFm30qgyQrNHvdCFSzJq6SerAqc%253d; _gcl_au=1.1.1609383261.1742388432.1308413919.1749310937.1749312464; UserMatchHistory=AQJOrxxc--dY6wAAAZdLJ5C5rJgWZr8LNJPaN8M_-IpyLQHBiC7Kkt_-W3L-XPRvhGTsU45T_O6LMKhcSMia60wOyw5yeXQOZpERGbqnMphjFJY3FFsH8mw0pzd9gXWNxhcif4Gl863X2PECzOFZRlXU-TZiCuZK0UXhCSLeuSsLwzLcPgnsC0mJimxXMc1sIUp9NBxgfwBnlLZ3HDI-JGNtU-eoDBEOtP0IwlKcbTIkxKA6eCP9D0WNyhWNQsVLVVgqOezdKH9j9QdWqlab3z9dA3c9TzBcpY_fKmvs4ytE_U4u2eIBB849E7gbtYsxdy4TjvTNcDThAJGbYruci2TTdRmhsHSq6pVU12rmldwAD570qA; lidc="b=OB37:s=O:r=O:a=O:p=O:g=4850:u=8:x=1:i=1749312574:t=1749397291:v=2:sig=AQEvWKveZQFeAAcfGA8mMa-7KaKMAJMl"',
            'csrf-token': 'ajax:5695997962284638174',
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

    def search_company(self, company_name):
        """Search for a company on LinkedIn using the search box API"""
        try:
            # First request - Get company ID from search box
            search_url = f"https://www.linkedin.com/voyager/api/graphql?variables=(keywords:{quote(company_name)},query:(),type:COMPANY)&queryId=voyagerSearchDashReusableTypeahead.35c83322e303eeb7ced9eb48e83a165c"
            
            print(f"Searching LinkedIn for: {company_name}")
            response = requests.get(search_url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
               
                if 'data' in data and 'data' in data['data'] and 'searchDashReusableTypeaheadByType' in data['data']['data']:
                    elements = data['data']['data']['searchDashReusableTypeaheadByType'].get('elements', [])
                    company_matches = []
                    
                    for element in elements:
                        # Check if this is a company result
                        if 'title' in element and 'text' in element['title']:
                            result_name = element['title']['text']
                            tracking_urn = element.get('trackingUrn', '')
                            if tracking_urn:
                                company_id = tracking_urn.split(':')[-1]
                                company_matches.append({
                                    'name': result_name,
                                    'id': company_id
                                })
                                print(f"Found potential match: {result_name} (ID: {company_id})")
                    
                    if company_matches:
                        print(f"Found {len(company_matches)} potential company matches")
                        return company_matches
                    else:
                        print("No company matches found")
                        return None
                else:
                    print("No search results found")
                    return None
            else:
                print(f"LinkedIn API request failed with status code: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error searching LinkedIn for {company_name}: {str(e)}")
            return None

    def search_people(self, company_id, person_name):
        """Search for people associated with a company"""
        try:
            # Construct the search URL
            search_url = f"https://www.linkedin.com/voyager/api/graphql?variables=(start:0,origin:FACETED_SEARCH,query:(keywords:{quote(person_name)},flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:currentCompany,value:List({company_id})),(key:resultType,value:List(PEOPLE))),includeFiltersInResponse:false))&queryId=voyagerSearchDashClusters.52fec77d08aa4598c8a056ca6bce6c11"
            
            print(f"Searching for people at company {company_id} with name: {person_name}")
            response = requests.get(search_url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if there are any results
                if not data.get('included'):
                    print(f"No results found for {person_name}")
                    return None
                
                # Extract people data
                people_data = []
                for item in data['included']:
                    # Check for UNIVERSAL template
                    if item.get('template') == 'UNIVERSAL':
                        # Get the title text
                        title_text = item.get('title', {}).get('text', '')
                        
                        # Check if name matches
                        if title_text.lower() == person_name.lower():
                            # Get navigation URL
                            navigation_url = item.get('navigationUrl', '')
                            if navigation_url:
                                people_data.append({
                                    'profile_url': navigation_url
                                })
                
                return people_data
            else:
                print(f"LinkedIn API request failed with status code: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error searching for people: {str(e)}")
            return None 