"""
Step 2: DuckDB Database - Create Tables and Run SQL Queries
DuckDB is space-efficient and perfect for large data analysis
"""

import duckdb
import pandas as pd
import os
import json
from datetime import datetime

# Setting my project base directory
BASE_DIR = r"D:\patent_data_pipeline"
CLEANED_DATA_DIR = os.path.join(BASE_DIR, "data", "cleaned")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
DATABASE_DIR = os.path.join(BASE_DIR, "database")

# Creating directories if they don't exist
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(DATABASE_DIR, exist_ok=True)

# Database file path
DB_PATH = os.path.join(DATABASE_DIR, "patent_data.duckdb")

print("=" * 70)
print("STEP 2: DUCKDB DATABASE - CREATING TABLES AND RUNNING QUERIES")
print("=" * 70)
print(f"\nProject Directory: {BASE_DIR}")
print(f"Database Location: {DB_PATH}")
print(f"Reports Location: {REPORTS_DIR}")

# Connecting to DuckDB database
print("\n[1/7] Connecting to DuckDB database...")
conn = duckdb.connect(DB_PATH)

# -----------------------------------------------------------------------------
# Creating tables and loading data from CSV files
# -----------------------------------------------------------------------------
print("\n[2/7] Creating tables and loading data...")
print("      This may take a few minutes...")

# Defining CSV file paths
patents_csv = os.path.join(CLEANED_DATA_DIR, "clean_patents.csv")
inventors_csv = os.path.join(CLEANED_DATA_DIR, "clean_inventors.csv")
companies_csv = os.path.join(CLEANED_DATA_DIR, "clean_companies.csv")
relationships_csv = os.path.join(CLEANED_DATA_DIR, "relationships.csv")

# Checking if files exist
for file_path in [patents_csv, inventors_csv, companies_csv, relationships_csv]:
    if not os.path.exists(file_path):
        print(f"      ERROR: File not found - {file_path}")
        exit(1)

# Creating patents table with explicit VARCHAR for patent_id
print("      Loading patents...")
conn.execute(f"""
CREATE OR REPLACE TABLE patents AS 
SELECT 
    patent_id::VARCHAR as patent_id,
    title::VARCHAR as title,
    abstract::VARCHAR as abstract,
    filing_date::DATE as filing_date,
    year::INTEGER as year
FROM read_csv_auto(
    '{patents_csv}',
    header=True,
    ALL_VARCHAR=True
)
""")
patent_count = conn.execute("SELECT COUNT(*) FROM patents").fetchone()[0]
print(f"      ✓ Patents loaded: {patent_count:,}")

# Create inventors table
print("      Loading inventors...")
conn.execute(f"""
CREATE OR REPLACE TABLE inventors AS 
SELECT 
    inventor_id::VARCHAR as inventor_id,
    name::VARCHAR as name,
    country::VARCHAR as country
FROM read_csv_auto(
    '{inventors_csv}',
    header=True,
    ALL_VARCHAR=True
)
""")
inventor_count = conn.execute("SELECT COUNT(*) FROM inventors").fetchone()[0]
print(f"       Inventors loaded: {inventor_count:,}")

# Create companies table
print("      Loading companies...")
conn.execute(f"""
CREATE OR REPLACE TABLE companies AS 
SELECT 
    company_id::VARCHAR as company_id,
    name::VARCHAR as name,
    country::VARCHAR as country
FROM read_csv_auto(
    '{companies_csv}',
    header=True,
    ALL_VARCHAR=True
)
""")
company_count = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
print(f"       Companies loaded: {company_count:,}")

# Create relationships table
print("      Loading relationships...")
conn.execute(f"""
CREATE OR REPLACE TABLE relationships AS 
SELECT 
    relationship_id::INTEGER as relationship_id,
    patent_id::VARCHAR as patent_id,
    inventor_id::VARCHAR as inventor_id,
    company_id::VARCHAR as company_id
FROM read_csv_auto(
    '{relationships_csv}',
    header=True,
    ALL_VARCHAR=True
)
""")
rel_count = conn.execute("SELECT COUNT(*) FROM relationships").fetchone()[0]
print(f"       Relationships loaded: {rel_count:,}")

print("\n       All tables created successfully!")

# -----------------------------------------------------------------------------
# Creating indexes for better performance
# -----------------------------------------------------------------------------
print("\n[3/7] Creating indexes...")
conn.execute("CREATE INDEX IF NOT EXISTS idx_patents_year ON patents(year)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_relationships_patent ON relationships(patent_id)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_relationships_inventor ON relationships(inventor_id)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_relationships_company ON relationships(company_id)")
print("       Indexes created")

# -----------------------------------------------------------------------------
# RUNNING ALL 7 SQL QUERIES
# -----------------------------------------------------------------------------
print("\n[4/7] Running SQL queries...")

# Q1: Top Inventors
print("\n" + "-" * 50)
print("Q1: TOP INVENTORS (Most Patents)")
print("-" * 50)
q1 = """
SELECT 
    i.name,
    COUNT(DISTINCT r.patent_id) as patent_count
FROM inventors i
JOIN relationships r ON i.inventor_id = r.inventor_id
GROUP BY i.inventor_id, i.name
ORDER BY patent_count DESC
LIMIT 10
"""
top_inventors = conn.execute(q1).fetchdf()
print(top_inventors.to_string(index=False))
top_inventors.to_csv(os.path.join(REPORTS_DIR, "top_inventors.csv"), index=False)
print(f"\n Saved: reports/top_inventors.csv")

# Q2: Top Companies
print("\n" + "-" * 50)
print("Q2: TOP COMPANIES (Most Patents)")
print("-" * 50)
q2 = """
SELECT 
    c.name,
    COUNT(DISTINCT r.patent_id) as patent_count
FROM companies c
JOIN relationships r ON c.company_id = r.company_id
GROUP BY c.company_id, c.name
ORDER BY patent_count DESC
LIMIT 10
"""
top_companies = conn.execute(q2).fetchdf()
print(top_companies.to_string(index=False))
top_companies.to_csv(os.path.join(REPORTS_DIR, "top_companies.csv"), index=False)
print(f"\n Saved: reports/top_companies.csv")

# Q3: Top Countries
print("\n" + "-" * 50)
print("Q3: TOP COUNTRIES (Most Patents by Inventor Country)")
print("-" * 50)
q3 = """
SELECT 
    i.country,
    COUNT(DISTINCT r.patent_id) as patent_count
FROM inventors i
JOIN relationships r ON i.inventor_id = r.inventor_id
WHERE i.country != 'Unknown' AND i.country IS NOT NULL
GROUP BY i.country
ORDER BY patent_count DESC
LIMIT 10
"""
top_countries = conn.execute(q3).fetchdf()
print(top_countries.to_string(index=False))
top_countries.to_csv(os.path.join(REPORTS_DIR, "country_trends.csv"), index=False)
print(f"\n Saved: reports/country_trends.csv")

# Q4: Trends Over Time
print("\n" + "-" * 50)
print("Q4: PATENT TRENDS OVER TIME")
print("-" * 50)
q4 = """
SELECT 
    year,
    COUNT(*) as patent_count
FROM patents
WHERE year > 0 AND year IS NOT NULL
GROUP BY year
ORDER BY year
"""
trends = conn.execute(q4).fetchdf()
print(trends.to_string(index=False))

# Q5: JOIN Query
print("\n" + "-" * 50)
print("Q5: JOIN QUERY (Patents with Inventors and Companies)")
print("-" * 50)
q5 = """
SELECT 
    p.patent_id,
    SUBSTRING(p.title, 1, 60) as title_preview,
    i.name as inventor_name,
    c.name as company_name,
    p.year
FROM patents p
JOIN relationships r ON p.patent_id = r.patent_id
JOIN inventors i ON r.inventor_id = i.inventor_id
JOIN companies c ON r.company_id = c.company_id
LIMIT 20
"""
join_sample = conn.execute(q5).fetchdf()
print(join_sample.to_string(index=False))

# Q6: CTE Query (WITH statement)
print("\n" + "-" * 50)
print("Q6: CTE QUERY (Top Inventor Each Year)")
print("-" * 50)
q6 = """
WITH inventor_patents AS (
    SELECT 
        i.name,
        p.year,
        COUNT(*) as patents_per_year
    FROM inventors i
    JOIN relationships r ON i.inventor_id = r.inventor_id
    JOIN patents p ON r.patent_id = p.patent_id
    WHERE p.year IS NOT NULL AND p.year > 0
    GROUP BY i.name, p.year
),
ranked_inventors AS (
    SELECT 
        name,
        year,
        patents_per_year,
        ROW_NUMBER() OVER (PARTITION BY year ORDER BY patents_per_year DESC) as rank
    FROM inventor_patents
)
SELECT name, year, patents_per_year
FROM ranked_inventors
WHERE rank = 1
ORDER BY year DESC
LIMIT 10
"""
cte_results = conn.execute(q6).fetchdf()
print(cte_results.to_string(index=False))

# Q7: Ranking Query (Window Functions)
print("\n" + "-" * 50)
print("Q7: RANKING QUERY (Rank Inventors by Patent Count)")
print("-" * 50)
q7 = """
SELECT 
    i.name,
    COUNT(DISTINCT r.patent_id) as patent_count,
    RANK() OVER (ORDER BY COUNT(DISTINCT r.patent_id) DESC) as rank
FROM inventors i
JOIN relationships r ON i.inventor_id = r.inventor_id
GROUP BY i.inventor_id, i.name
ORDER BY patent_count DESC
LIMIT 20
"""
ranking_results = conn.execute(q7).fetchdf()
print(ranking_results.to_string(index=False))

# -----------------------------------------------------------------------------
# CREATING REPORTS
# -----------------------------------------------------------------------------
print("\n[5/7] Creating reports...")

# Get total patents
total_patents = conn.execute("SELECT COUNT(*) as total FROM patents").fetchdf()['total'][0]

# JSON Report
json_report = {
    "total_patents": int(total_patents),
    "top_inventors": top_inventors.head(5).to_dict('records'),
    "top_companies": top_companies.head(5).to_dict('records'),
    "top_countries": top_countries.head(5).to_dict('records'),
    "generated_at": datetime.now().isoformat()
}

with open(os.path.join(REPORTS_DIR, "report.json"), "w") as f:
    json.dump(json_report, f, indent=2)
print("✓ Saved: reports/report.json")

# Console Report
console_output = f"""
{'='*70}
PATENT DATA REPORT
{'='*70}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

TOTAL PATENTS: {total_patents:,}

{'='*70}
TOP 10 INVENTORS
{'='*70}
{top_inventors.to_string(index=False)}

{'='*70}
TOP 10 COMPANIES
{'='*70}
{top_companies.to_string(index=False)}

{'='*70}
TOP 10 COUNTRIES
{'='*70}
{top_countries.to_string(index=False)}

{'='*70}
PATENT TRENDS (All Years)
{'='*70}
{trends.to_string(index=False)}

{'='*70}
SAMPLE JOIN QUERY (20 rows)
{'='*70}
{join_sample.to_string(index=False)}

{'='*70}
CTE QUERY - Top Inventor Each Year
{'='*70}
{cte_results.to_string(index=False)}

{'='*70}
RANKING QUERY - Top 20 Inventors
{'='*70}
{ranking_results.to_string(index=False)}
"""

with open(os.path.join(REPORTS_DIR, "console_output.txt"), "w") as f:
    f.write(console_output)
print(" Saved: reports/console_output.txt")

# Also print summary to terminal
print("\n" + "=" * 70)
print("CONSOLE REPORT SUMMARY")
print("=" * 70)
print(f"Total Patents: {total_patents:,}")
if len(top_inventors) > 0:
    print(f"\nTop Inventor: {top_inventors.iloc[0]['name']} - {top_inventors.iloc[0]['patent_count']:,} patents")
if len(top_companies) > 0:
    print(f"Top Company: {top_companies.iloc[0]['name']} - {top_companies.iloc[0]['patent_count']:,} patents")
if len(top_countries) > 0:
    print(f"Top Country: {top_countries.iloc[0]['country']} - {top_countries.iloc[0]['patent_count']:,} patents")

# -----------------------------------------------------------------------------
# CREATING schema.sql FILE WITH TABLE DEFINITIONS AND QUERIES
# -----------------------------------------------------------------------------
print("\n[6/7] Creating schema.sql...")

schema_sql = """-- Patent Data Pipeline Database Schema
-- Generated for the Patent Data Analysis Project
-- Database: DuckDB
-- Generated on: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """

-- =====================================================
-- TABLE STRUCTURES
-- =====================================================

-- patents table
CREATE TABLE patents (
    patent_id VARCHAR PRIMARY KEY,
    title VARCHAR,
    abstract VARCHAR,
    filing_date DATE,
    year INTEGER
);

-- inventors table
CREATE TABLE inventors (
    inventor_id VARCHAR PRIMARY KEY,
    name VARCHAR,
    country VARCHAR
);

-- companies table
CREATE TABLE companies (
    company_id VARCHAR PRIMARY KEY,
    name VARCHAR,
    country VARCHAR
);

-- relationships table (links patents to inventors and companies)
CREATE TABLE relationships (
    relationship_id INTEGER PRIMARY KEY,
    patent_id VARCHAR,
    inventor_id VARCHAR,
    company_id VARCHAR
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

CREATE INDEX idx_patents_year ON patents(year);
CREATE INDEX idx_relationships_patent ON relationships(patent_id);
CREATE INDEX idx_relationships_inventor ON relationships(inventor_id);
CREATE INDEX idx_relationships_company ON relationships(company_id);

-- =====================================================
-- ANALYTICAL QUERIES
-- =====================================================

-- Q1: Top Inventors (Who has the most patents?)
SELECT 
    i.name,
    COUNT(DISTINCT r.patent_id) as patent_count
FROM inventors i
JOIN relationships r ON i.inventor_id = r.inventor_id
GROUP BY i.inventor_id, i.name
ORDER BY patent_count DESC
LIMIT 10;

-- Q2: Top Companies (Which companies own the most patents?)
SELECT 
    c.name,
    COUNT(DISTINCT r.patent_id) as patent_count
FROM companies c
JOIN relationships r ON c.company_id = r.company_id
GROUP BY c.company_id, c.name
ORDER BY patent_count DESC
LIMIT 10;

-- Q3: Top Countries (Which countries produce the most patents?)
SELECT 
    i.country,
    COUNT(DISTINCT r.patent_id) as patent_count
FROM inventors i
JOIN relationships r ON i.inventor_id = r.inventor_id
WHERE i.country != 'Unknown'
GROUP BY i.country
ORDER BY patent_count DESC
LIMIT 10;

-- Q4: Trends Over Time (How many patents per year?)
SELECT 
    year,
    COUNT(*) as patent_count
FROM patents
WHERE year > 0
GROUP BY year
ORDER BY year;

-- Q5: JOIN Query (Combine patents with inventors and companies)
SELECT 
    p.patent_id,
    p.title,
    i.name as inventor_name,
    c.name as company_name,
    p.year
FROM patents p
JOIN relationships r ON p.patent_id = r.patent_id
JOIN inventors i ON r.inventor_id = i.inventor_id
JOIN companies c ON r.company_id = c.company_id
LIMIT 20;

-- Q6: CTE Query (Top inventor per year)
WITH inventor_patents AS (
    SELECT 
        i.name,
        p.year,
        COUNT(*) as patents_per_year
    FROM inventors i
    JOIN relationships r ON i.inventor_id = r.inventor_id
    JOIN patents p ON r.patent_id = p.patent_id
    WHERE p.year IS NOT NULL
    GROUP BY i.name, p.year
),
ranked_inventors AS (
    SELECT 
        name,
        year,
        patents_per_year,
        ROW_NUMBER() OVER (PARTITION BY year ORDER BY patents_per_year DESC) as rank
    FROM inventor_patents
)
SELECT name, year, patents_per_year
FROM ranked_inventors
WHERE rank = 1
ORDER BY year DESC
LIMIT 10;

-- Q7: Ranking Query (Rank inventors)
SELECT 
    i.name,
    COUNT(DISTINCT r.patent_id) as patent_count,
    RANK() OVER (ORDER BY COUNT(DISTINCT r.patent_id) DESC) as rank
FROM inventors i
JOIN relationships r ON i.inventor_id = r.inventor_id
GROUP BY i.inventor_id, i.name
ORDER BY patent_count DESC
LIMIT 20;
"""

with open(os.path.join(DATABASE_DIR, "schema.sql"), "w") as f:
    f.write(schema_sql)
print(" Saved: database/schema.sql")

# -----------------------------------------------------------------------------
# DATABASE SIZE INFO
# -----------------------------------------------------------------------------
print("\n[7/7] Getting database information...")

# Get database file size
if os.path.exists(DB_PATH):
    db_size = os.path.getsize(DB_PATH) / (1024 * 1024 * 1024)  # Size in GB
    print(f"      Database size: {db_size:.2f} GB")

# Close connection
conn.close()


print(" ALL TASKS COMPLETED SUCCESSFULLY!")

print("\n Reports saved in: reports/")
print("   top_inventors.csv")
print("   top_companies.csv")
print("   country_trends.csv")
print("   report.json")
print("   console_output.txt")
print("\n Database saved in: database/patent_data.duckdb")
print(" Schema saved in: database/schema.sql")
