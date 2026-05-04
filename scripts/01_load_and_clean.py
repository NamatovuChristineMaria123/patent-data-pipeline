"""
Data Pipeline - Loading and Cleaning Patent Data
This script loads all 5 TSV files, cleans them, and creates the 4 tables needed for the database.
"""

import pandas as pd
import os
import gc

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
CLEANED_DATA_DIR = os.path.join(BASE_DIR, "data", "cleaned")

os.makedirs(CLEANED_DATA_DIR, exist_ok=True)

# Loading location file 
print("\n[1/6] Loading location data...")
print("      File: g_location_disambiguated.tsv")

location_df = pd.read_csv(
    os.path.join(RAW_DATA_DIR, "g_location_disambiguated.tsv"),
    sep="\t",
    dtype=str
)

location_dict = dict(zip(location_df['location_id'], location_df['disambig_country']))
print(f"      Loaded {len(location_dict):,} location records")

del location_df
gc.collect()

# Loading and processing patents
print("\n[2/6] Loading patent data...")
print("      File: g_patent.tsv")

patents_df = pd.read_csv(
    os.path.join(RAW_DATA_DIR, "g_patent.tsv"),
    sep="\t",
    dtype=str
)

clean_patents = pd.DataFrame()
clean_patents['patent_id'] = patents_df['patent_id']
clean_patents['title'] = patents_df['patent_title'].fillna('Unknown Title')
clean_patents['filing_date'] = pd.to_datetime(patents_df['patent_date'], errors='coerce')
clean_patents['year'] = clean_patents['filing_date'].dt.year
clean_patents['year'] = clean_patents['year'].fillna(0).astype(int)
clean_patents['abstract'] = 'No abstract available'

clean_patents = clean_patents.drop_duplicates(subset=['patent_id'])
clean_patents = clean_patents.dropna(subset=['patent_id'])

print(f"      Patents: {len(clean_patents):,} records")

del patents_df
gc.collect()


# Loading abstracts and merge
print("\n[3/6] Loading abstract data...")
print("      File: g_patent_abstract.tsv")

abstracts_df = pd.read_csv(
    os.path.join(RAW_DATA_DIR, "g_patent_abstract.tsv"),
    sep="\t",
    dtype=str
)

abstract_dict = dict(zip(abstracts_df['patent_id'], abstracts_df['patent_abstract']))
clean_patents['abstract'] = clean_patents['patent_id'].map(abstract_dict)
clean_patents['abstract'] = clean_patents['abstract'].fillna('No abstract available')

print(f"      Merged {len(abstract_dict):,} abstracts")

del abstracts_df
del abstract_dict
gc.collect()

clean_patents.to_csv(os.path.join(CLEANED_DATA_DIR, "clean_patents.csv"), index=False)
print(f"      Saved: data/cleaned/clean_patents.csv")


# Loading and processing inventors
print("\n[4/6] Loading inventor data...")
print("      File: g_inventor_disambiguated.tsv")

inventors_df = pd.read_csv(
    os.path.join(RAW_DATA_DIR, "g_inventor_disambiguated.tsv"),
    sep="\t",
    dtype=str
)

clean_inventors = pd.DataFrame()
clean_inventors['inventor_id'] = inventors_df['inventor_id']
clean_inventors['name'] = (inventors_df['disambig_inventor_name_first'].fillna('') + ' ' + 
                            inventors_df['disambig_inventor_name_last'].fillna('')).str.strip()
clean_inventors['name'] = clean_inventors['name'].replace('', 'Unknown Inventor')
clean_inventors['country'] = inventors_df['location_id'].map(location_dict).fillna('Unknown')

patent_inventor = inventors_df[['patent_id', 'inventor_id']].drop_duplicates()
patent_inventor = patent_inventor.dropna()

clean_inventors = clean_inventors.drop_duplicates(subset=['inventor_id'])
clean_inventors = clean_inventors.dropna(subset=['inventor_id'])

print(f"      Inventors: {len(clean_inventors):,} records")
print(f"      Patent-Inventor relationships: {len(patent_inventor):,}")

del inventors_df
gc.collect()

clean_inventors.to_csv(os.path.join(CLEANED_DATA_DIR, "clean_inventors.csv"), index=False)
print(f"      Saved: data/cleaned/clean_inventors.csv")


# Loading and processing companies (assignees)
print("\n[5/6] Loading company data...")
print("      File: g_assignee_disambiguated.tsv")

companies_df = pd.read_csv(
    os.path.join(RAW_DATA_DIR, "g_assignee_disambiguated.tsv"),
    sep="\t",
    dtype=str
)

clean_companies = pd.DataFrame()
clean_companies['company_id'] = companies_df['assignee_id']
clean_companies['name'] = companies_df['disambig_assignee_organization'].fillna('Unknown Company')
clean_companies['name'] = clean_companies['name'].str.strip()
clean_companies['country'] = companies_df['location_id'].map(location_dict).fillna('Unknown')

patent_company = companies_df[['patent_id', 'assignee_id']].drop_duplicates()
patent_company = patent_company.dropna()
patent_company.columns = ['patent_id', 'company_id']

clean_companies = clean_companies.drop_duplicates(subset=['company_id'])
clean_companies = clean_companies.dropna(subset=['company_id'])

print(f"      Companies: {len(clean_companies):,} records")
print(f"      Patent-Company relationships: {len(patent_company):,}")

del companies_df
gc.collect()

clean_companies.to_csv(os.path.join(CLEANED_DATA_DIR, "clean_companies.csv"), index=False)
print(f"      Saved: data/cleaned/clean_companies.csv")


# Creating final relationships table
print("\n[6/6] Creating relationships table...")

relationships = patent_inventor.merge(patent_company, on='patent_id', how='outer')
relationships['relationship_id'] = range(1, len(relationships) + 1)
relationships = relationships[['relationship_id', 'patent_id', 'inventor_id', 'company_id']]

print(f"      Relationships: {len(relationships):,} records")

relationships.to_csv(os.path.join(CLEANED_DATA_DIR, "relationships.csv"), index=False)
print(f"      Saved: data/cleaned/relationships.csv")

del patent_inventor, patent_company, relationships, location_dict, clean_patents, clean_inventors, clean_companies
gc.collect()


# SUMMARY

print("SUCCESS! All cleanedfiles saved to: data/cleaned/")

