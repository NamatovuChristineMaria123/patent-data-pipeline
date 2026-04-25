# Global Patent Intelligence Data Pipeline

## Project Overview

This project builds a complete data pipeline that collects, cleans, stores, and analyzes real-world patent data from the USPTO. The pipeline processes **9.4 million patents**, **4.3 million inventors**, and **25 million relationships** to answer key business questions about innovation trends.

## Data Source

- **USPTO PatentsView**: Granted Patent Disambiguated Data
- **Link**: https://data.uspto.gov/bulkdata/datasets/pvgpatdis
- **Date Range**: 1976 - 2025
- **Total Patents Analyzed**: 9,454,161

## Features

- Downloads real patent data from USPTO API
- Cleans and transforms data using pandas
- Stores data in DuckDB database (efficient columnar storage)
- Runs 7 analytical SQL queries
- Generates CSV, JSON, and console reports
- Creates 6 professional visualizations
- Interactive Streamlit dashboard with filters and heatmaps

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/NamatovuChristineMaria123/patent-data-pipeline.git
cd patent-data-pipeline
2. Install Python dependencies
bash
pip install -r requirements.txt
3. Download the data
bash
python scripts/00_download_data.py
4. Clean the data
bash
python scripts/01_load_and_clean.py
5. Create database and run SQL queries
bash
python scripts/02_duckdb_queries.py
6. Generate visualizations
bash
python scripts/03_visualizations.py
7. Launch interactive dashboard
bash
streamlit run scripts/04_streamlit_dashboard.py
Then open http://localhost:8501 in your browser.

SQL Queries Implemented
Query	Description
Q1	Top Inventors (who has the most patents)
Q2	Top Companies (which companies own the most patents)
Q3	Top Countries (which countries produce the most patents)
Q4	Trends Over Time (patents per year)
Q5	JOIN Query (combine patents with inventors and companies)
Q6	CTE Query (top inventor each year using WITH statement)
Q7	Ranking Query (rank inventors using window functions)
Key Findings
Metric	Result
Total Patents	9,454,161
Top Inventor	Shunpei Yamazaki (6,787 patents)
Top Company	SAMSUNG DISPLAY CO., LTD. (174,536 patents)
Top Country	United States (5,152,235 patents)
Reports Generated
reports/top_inventors.csv - Top 10 inventors with patent counts

reports/top_companies.csv - Top 10 companies with patent counts

reports/country_trends.csv - Patent distribution by country

reports/report.json - JSON format of key metrics

reports/console_output.txt - Complete console output

reports/visuals/ - 6 PNG visualizations

Technologies Used
Python 3.10+ - Core programming language

Pandas - Data cleaning and manipulation

DuckDB - Columnar database for analytics

Streamlit - Interactive web dashboard

Plotly - Interactive visualizations

Matplotlib/Seaborn - Static visualizations

Requests - API data fetching
```
