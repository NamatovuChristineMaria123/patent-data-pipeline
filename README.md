# Global Patent Intelligence Data Pipeline

## Project Overview

This project builds a complete data pipeline that collects, cleans, stores, and analyzes real-world patent data from the USPTO. The pipeline processes **9.4 million patents**, **4.3 million inventors**, and **25 million relationships** to answer key business questions about innovation trends.

## Links

Presented by Namatovu Christine Maria 23/U/1098
Dashboard Demo (YouTube) https://youtu.be/aRhJW2zsjyw

GitHub Repository https://github.com/NamatovuChristineMaria123/patent-data-pipeline

Data Source https://data.uspto.gov/bulkdata/datasets/pvgpatdis

---

## Installation & Setup (For reproducibility)

### 1. Clone the Repository

```bash
git clone https://github.com/NamatovuChristineMaria123/patent-data-pipeline.git
cd patent-data-pipeline
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Download Raw Data (Manual Step Required)

Download these 5 files from [USPTO PatentsView](https://data.uspto.gov/bulkdata/datasets/pvgpatdis) and place them in `data/raw/`:

- `g_patent.tsv`
- `g_patent_abstract.tsv`
- `g_inventor_disambiguated.tsv`
- `g_assignee_disambiguated.tsv`
- `g_location_disambiguated.tsv`

### 4. Run the Pipeline

```bash
python scripts/01_load_and_clean.py
python scripts/02_duckdb_queries.py
python scripts/03_visualizations.py
streamlit run scripts/04_streamlit_dashboard.py
```

---

---

## 📊 DASHBOARD (Patent trends 1976-2025)

> **Video Walkthrough:** Since the app isn't publicly deployed, I had recorded a dashboard demo and uploaded on YouTube:
> **[▶️ Watch Dashboard Demo on YouTube](https://youtu.be/aRhJW2zsjyw)**

### Dashboard Screenshot(For all countries between 1976 - 2025

> <img width="1894" height="863" alt="image" src="https://github.com/user-attachments/assets/3a0a1f58-2c0e-4ac7-9adb-3b999b164a3d" />

### Dashboard – Patent Trends View

> <img width="1887" height="860" alt="image" src="https://github.com/user-attachments/assets/d97e4f5b-df77-4fae-bf04-e87342e99f61" />

> <img width="1899" height="867" alt="image" src="https://github.com/user-attachments/assets/7d90fede-fc83-42fa-a36b-9143770ac0ad" />

> <img width="1906" height="873" alt="image" src="https://github.com/user-attachments/assets/ba43f964-4733-407b-a9fa-bfbcc931ab43" />

### DASHBOARD – FILTERS

> <img width="1857" height="867" alt="image" src="https://github.com/user-attachments/assets/1d63e42f-4b40-4d4b-af95-24474ddca691" />

### Dashboard Screenshot(For a single country (JP) in a specific year (2003)

<img width="1890" height="874" alt="image" src="https://github.com/user-attachments/assets/5f103615-0b60-472e-a55d-638adca17aa9" />

### Dashboard Screenshot(2003 Patent Trends for all countries)

<img width="1896" height="854" alt="dashboard_05_(filtered)2003_patent_trends" src="https://github.com/user-attachments/assets/2a60d8c1-5087-4740-b50b-c82cb0f3cc3a" />

### Dashboard – Heatmap(2015-2025)

> <img width="1889" height="873" alt="image" src="https://github.com/user-attachments/assets/57d57b73-6a1d-4e73-9801-ed5561899881" />

---

## 📈 VISUALIZATIONS

### 1. Top 10 Inventors by Patent Count

<img width="1324" height="651" alt="Screenshot 2026-05-09 194613" src="https://github.com/user-attachments/assets/86d6be22-1935-4a44-ba34-e5c8764e7f02" />

### 2. Top 10 Companies by Patent Count

<img width="1289" height="631" alt="Screenshot 2026-05-09 194721" src="https://github.com/user-attachments/assets/78180799-5ea9-4879-9262-ae2330b1a582" />

### 3. Top Countries by Patent Count

<img width="1061" height="627" alt="image" src="https://github.com/user-attachments/assets/6112561b-bf23-45dd-a056-b0163f86d7b3" />

### 4. Countries Distribution (Pie Chart)

<img width="607" height="629" alt="image" src="https://github.com/user-attachments/assets/7971d646-a35d-4134-83ee-8b9af697fd67" />

### 5. Patent Trends Over Time

<img width="1289" height="632" alt="image" src="https://github.com/user-attachments/assets/7f407546-15e6-42af-b610-2ff5de91a967" />

### 6. Dashboard Overview

<img width="751" height="639" alt="image" src="https://github.com/user-attachments/assets/56ff38b6-250f-4969-ae58-9f10eaab7ea7" />

---

## 🖥️ Console Report

<img width="826" height="620" alt="image" src="https://github.com/user-attachments/assets/14f89f6b-2841-42c8-8924-426a005649ed" />
<img width="1021" height="415" alt="image" src="https://github.com/user-attachments/assets/94154a39-491b-48e9-ae48-99367abbd611" />
<img width="999" height="430" alt="image" src="https://github.com/user-attachments/assets/b9cd3f01-5fab-4672-a1f1-43069132b216" />
<img width="1059" height="829" alt="image" src="https://github.com/user-attachments/assets/35ea7c55-684b-4c90-88b9-cee4648edce3" />
<img width="1065" height="736" alt="image" src="https://github.com/user-attachments/assets/f843b755-fa39-4138-ab03-1597a4b7dc87" />
<img width="1183" height="720" alt="image" src="https://github.com/user-attachments/assets/a3f6f4c9-7e42-4860-ba62-76b171674216" />
<img width="887" height="426" alt="image" src="https://github.com/user-attachments/assets/59e00c45-54b3-40c3-94e3-33474347f4b2" />
<img width="985" height="702" alt="image" src="https://github.com/user-attachments/assets/532220f2-12dd-4fb4-8f64-aafc11653e57" />

## REPORT.JSON

<img width="1028" height="742" alt="image" src="https://github.com/user-attachments/assets/9864daba-f89f-4147-a92a-26ff9d6c4117" />
<img width="1056" height="630" alt="image" src="https://github.com/user-attachments/assets/69e57435-294f-4e05-a3c9-cd71753f66e6" />
<img width="1181" height="692" alt="image" src="https://github.com/user-attachments/assets/68c2c7db-f63d-44ea-badb-7ae10d4dea0f" />

---

## 📁 Project Structure

```
patent-data-pipeline/
│
├── data/
│   ├── raw/                        # Downloaded USPTO TSV files (not committed)
│   └── clean/
│       ├── clean_patents.csv
│       ├── clean_inventors.csv
|       ├── relationships.csv
│       └── clean_companies.csv
|
│
├── scripts/
|   ├── 00_download_data            #For reproducibility incase one doesnt want to download the big datasets manually(Downloads part of the data)
│   ├── 01_load_and_clean.py        # Data ingestion & cleaning
│   ├── 02_duckdb_queries.py        # SQL analytics via DuckDB
│   ├── 03_visualizations.py        # Chart generation
│   └── 04_streamlit_dashboard.py   # Interactive dashboard
│
├── database/
|   ├── patent_data.duckdb
│   └── schema.sql                  # Database schema
│
├── reports/
│   ├── top_inventors.csv
│   ├── top_companies.csv
│   ├── country_trends.csv
│   ├── report.json
│   ├── console_output.txt
│   └── visuals/                    # 6 PNG visualizations
│
├── requirements.txt
├── gitignore
└── README.md
```

---

## 🔍 SQL Queries Implemented

| Query  | Description                                               |
| ------ | --------------------------------------------------------- |
| **Q1** | Top Inventors — who has the most patents                  |
| **Q2** | Top Companies — which companies own the most patents      |
| **Q3** | Top Countries — which countries produce the most patents  |
| **Q4** | Trends Over Time — patents granted per year               |
| **Q5** | JOIN Query — combine patents with inventors and companies |
| **Q6** | CTE Query — top inventor each year using `WITH` statement |
| **Q7** | Ranking Query — rank inventors using window functions     |

---

## 🛠️ Technologies Used

| Tool                     | Purpose                          |
| ------------------------ | -------------------------------- |
| **Python 3.10+**         | Core programming language        |
| **Pandas**               | Data cleaning and transformation |
| **DuckDB**               | Columnar database for analytics  |
| **Streamlit**            | Interactive web dashboard        |
| **Plotly**               | Interactive visualizations       |
| **Matplotlib / Seaborn** | Static visualizations            |
| **SQL**                  | Data querying and aggregation    |

---
