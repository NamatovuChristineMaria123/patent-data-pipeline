-- Patent Data Pipeline Database Schema
-- Generated for the Patent Data Analysis Project
-- Database: DuckDB
-- Generated on: 2026-04-20 22:17:26

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
