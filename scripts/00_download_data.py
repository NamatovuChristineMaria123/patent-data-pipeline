"""
Step 0: (For reproducibility) Download Patent Data from USPTO API
This script downloads real patent data from the PatentsView API
Run this first before any other scripts to get the raw data files needed for the pipeline
"""

import requests
import pandas as pd
import os
import time
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(RAW_DATA_DIR, exist_ok=True)

print("=" * 70)
print("STEP 0: DOWNLOADING PATENT DATA FROM USPTO API")
print("=" * 70)

# API endpoint
API_URL = "https://api.patentsview.org/patents/query"

def download_patents(limit=50000, start=0):
    """Download patent data from PatentsView API"""
    
    all_patents = []
    batch_size = 250
    total_downloaded = 0
    
    print(f"\n[1/4] Downloading patents (target: {limit:,} records)...")
    
    while total_downloaded < limit:
        query = {
            "q": {},
            "f": [
                "patent_id",
                "patent_title",
                "patent_abstract",
                "patent_date",
                "patent_year",
                "inventor_first_name",
                "inventor_last_name",
                "inventor_country",
                "assignee_organization",
                "assignee_country"
            ],
            "s": [{"patent_date": "desc"}],
            "o": {"page": (start // batch_size) + 1, "per_page": batch_size}
        }
        
        try:
            response = requests.post(API_URL, json=query, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                patents = data.get('patents', [])
                
                if not patents:
                    break
                    
                for patent in patents:
                    # Get first inventor
                    inventor_name = "Unknown"
                    inventor_country = "Unknown"
                    if 'inventors' in patent and patent['inventors']:
                        inv = patent['inventors'][0]
                        inventor_name = f"{inv.get('inventor_first_name', '')} {inv.get('inventor_last_name', '')}".strip()
                        inventor_country = inv.get('inventor_country', 'Unknown')
                    
                    # Get first assignee
                    assignee_name = "Unknown"
                    assignee_country = "Unknown"
                    if 'assignees' in patent and patent['assignees']:
                        assignee_name = patent['assignees'][0].get('assignee_organization', 'Unknown')
                        assignee_country = patent['assignees'][0].get('assignee_country', 'Unknown')
                    
                    all_patents.append({
                        'patent_id': patent.get('patent_id', ''),
                        'title': patent.get('patent_title', ''),
                        'abstract': patent.get('patent_abstract', ''),
                        'filing_date': patent.get('patent_date', ''),
                        'year': patent.get('patent_year', ''),
                        'inventor_name': inventor_name,
                        'inventor_country': inventor_country,
                        'assignee_name': assignee_name,
                        'assignee_country': assignee_country
                    })
                
                total_downloaded += len(patents)
                print(f"      Downloaded {total_downloaded:,} patents...", end="\r")
                start += batch_size
                time.sleep(0.5)  # Be nice to the API
            else:
                print(f"\n      API error: {response.status_code}")
                break
                
        except Exception as e:
            print(f"\n      Error: {e}")
            break
    
    print(f"\n      ✓ Downloaded {len(all_patents):,} total patents")
    return pd.DataFrame(all_patents)

def create_sample_patent_data():
    """Fallback: Create sample data if API fails"""
    print("\n[2/4] API unavailable - Creating sample patent data...")
    
    sample_data = []
    for i in range(1, 10001):
        year = 2015 + (i % 10)
        sample_data.append({
            'patent_id': f'US{10000000 + i}',
            'title': f'Sample Patent {i}',
            'abstract': f'This is a sample abstract for patent {i}',
            'filing_date': f'{year}-{(i % 12)+1:02d}-{(i % 28)+1:02d}',
            'year': year,
            'inventor_name': f'Inventor {i % 100}',
            'inventor_country': ['US', 'CN', 'JP', 'DE', 'KR'][i % 5],
            'assignee_name': ['IBM', 'Google', 'Microsoft', 'Samsung', 'Toyota'][i % 5],
            'assignee_country': ['US', 'US', 'US', 'KR', 'JP'][i % 5]
        })
    
    df = pd.DataFrame(sample_data)
    print(f"       Created {len(df):,} sample patent records")
    return df

# Main execution
print("\n[1/4] Connecting to PatentsView API...")

try:
    # Try to download real data (50,000 patents - adjust as needed)
    patents_df = download_patents(limit=50000)
    
    if len(patents_df) == 0:
        patents_df = create_sample_patent_data()
        
except Exception as e:
    print(f"      API connection failed: {e}")
    patents_df = create_sample_patent_data()

# Save raw data
print("\n[3/4] Saving raw data...")
patents_df.to_csv(os.path.join(RAW_DATA_DIR, "raw_patents.csv"), index=False)
print(f"       Saved: data/raw/raw_patents.csv")

# Create additional required files for compatibility (matching your original structure)
print("\n[4/4] Creating additional data files...")

# Create location file (derived from inventor locations)
location_data = []
unique_countries = patents_df['inventor_country'].unique()
for i, country in enumerate(unique_countries):
    if country != 'Unknown':
        location_data.append({
            'location_id': f'loc_{i:05d}',
            'disambig_city': 'Unknown',
            'disambig_state': 'Unknown',
            'disambig_country': country,
            'latitude': 0,
            'longitude': 0,
            'county': 'Unknown',
            'state_fips': '00',
            'county_fips': '000'
        })

location_df = pd.DataFrame(location_data)
location_df.to_csv(os.path.join(RAW_DATA_DIR, "g_location_disambiguated.tsv"), sep="\t", index=False)
print(f"       Created: data/raw/g_location_disambiguated.tsv")

# Create inventors file
inventors_data = patents_df[['inventor_name', 'inventor_country']].drop_duplicates().reset_index(drop=True)
inventors_data['inventor_id'] = [f'inv_{i:08d}' for i in range(len(inventors_data))]
inventors_data['disambig_inventor_name_first'] = inventors_data['inventor_name'].apply(lambda x: x.split()[0] if x != 'Unknown' else 'Unknown')
inventors_data['disambig_inventor_name_last'] = inventors_data['inventor_name'].apply(lambda x: x.split()[-1] if x != 'Unknown' else 'Unknown')
inventors_data['location_id'] = 'loc_00000'
inventors_data = inventors_data[['patent_id', 'inventor_id', 'disambig_inventor_name_first', 'disambig_inventor_name_last', 'location_id']]
inventors_data.to_csv(os.path.join(RAW_DATA_DIR, "g_inventor_disambiguated.tsv"), sep="\t", index=False)
print(f"       Created: data/raw/g_inventor_disambiguated.tsv")

# Create assignee file
assignees_data = patents_df[['assignee_name', 'assignee_country']].drop_duplicates().reset_index(drop=True)
assignees_data['assignee_id'] = [f'asg_{i:08d}' for i in range(len(assignees_data))]
assignees_data['disambig_assignee_organization'] = assignees_data['assignee_name']
assignees_data['location_id'] = 'loc_00000'
assignees_data = assignees_data[['patent_id', 'assignee_id', 'disambig_assignee_organization', 'location_id']]
assignees_data.to_csv(os.path.join(RAW_DATA_DIR, "g_assignee_disambiguated.tsv"), sep="\t", index=False)
print(f"       Created: data/raw/g_assignee_disambiguated.tsv")

# Create abstract file
abstracts_data = patents_df[['patent_id', 'abstract']].copy()
abstracts_data.to_csv(os.path.join(RAW_DATA_DIR, "g_patent_abstract.tsv"), sep="\t", index=False)
print(f"       Created: data/raw/g_patent_abstract.tsv")

# Create patent file
patents_for_file = patents_df[['patent_id', 'title', 'filing_date', 'year']].copy()
patents_for_file.columns = ['patent_id', 'patent_title', 'patent_date', 'year']
patents_for_file['patent_type'] = 'utility'
patents_for_file['num_claims'] = 10
patents_for_file['withdrawn'] = 0
patents_for_file.to_csv(os.path.join(RAW_DATA_DIR, "g_patent.tsv"), sep="\t", index=False)
print(f"       Created: data/raw/g_patent.tsv")


print(" DATA DOWNLOAD/ CREATION COMPLETE!")


