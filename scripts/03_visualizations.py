"""
Creating Visualizations for Patent Data Analysis
Installed matplotlib and seaborn
Used the command: pip install matplotlib seaborn
"""

import duckdb
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

# Set style for better-looking charts
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Set your project base directory
BASE_DIR = r"D:\patent_data_pipeline"
DB_PATH = os.path.join(BASE_DIR, "database", "patent_data.duckdb")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
VISUALS_DIR = os.path.join(REPORTS_DIR, "visuals")

# Create visuals directory
os.makedirs(VISUALS_DIR, exist_ok=True)


print(" CREATING DATA VISUALIZATIONS")


# Connect to DuckDB
print("\n[1/6] Connecting to database...")
conn = duckdb.connect(DB_PATH)


# Visualization 1: Top 10 Inventors (Bar Chart)
print("\n[2/6] Creating Top 10 Inventors chart...")

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

plt.figure(figsize=(12, 6))
bars = plt.barh(range(len(top_inventors)), top_inventors['patent_count'], color='steelblue')
plt.yticks(range(len(top_inventors)), top_inventors['name'])
plt.xlabel('Number of Patents', fontsize=12)
plt.title('Top 10 Inventors by Patent Count', fontsize=14, fontweight='bold')
plt.gca().invert_yaxis()

# Add value labels on bars
for i, v in enumerate(top_inventors['patent_count']):
    plt.text(v + 100, i, f'{v:,}', va='center', fontsize=10)

plt.tight_layout()
plt.savefig(os.path.join(VISUALS_DIR, 'top_inventors.png'), dpi=150, bbox_inches='tight')
plt.close()
print(f"      Saved: visuals/top_inventors.png")


# Visualization 2: Top 10 Companies (Bar Chart)
print("\n[3/6] Creating Top 10 Companies chart...")

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

plt.figure(figsize=(12, 6))
bars = plt.barh(range(len(top_companies)), top_companies['patent_count'], color='coral')
plt.yticks(range(len(top_companies)), top_companies['name'])
plt.xlabel('Number of Patents', fontsize=12)
plt.title('Top 10 Companies by Patent Count', fontsize=14, fontweight='bold')
plt.gca().invert_yaxis()

# Add value labels
for i, v in enumerate(top_companies['patent_count']):
    plt.text(v + 1000, i, f'{v:,}', va='center', fontsize=9)

plt.tight_layout()
plt.savefig(os.path.join(VISUALS_DIR, 'top_companies.png'), dpi=150, bbox_inches='tight')
plt.close()
print(f"      Saved: visuals/top_companies.png")


# Visualization 3: Top 10 Countries (Bar Chart)
print("\n[4/6] Creating Top 10 Countries chart...")

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

plt.figure(figsize=(10, 6))
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
          '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
plt.bar(range(len(top_countries)), top_countries['patent_count'], color=colors)
plt.xticks(range(len(top_countries)), top_countries['country'])
plt.ylabel('Number of Patents', fontsize=12)
plt.title('Top 10 Countries by Patent Count', fontsize=14, fontweight='bold')

# Add value labels on top of bars
for i, v in enumerate(top_countries['patent_count']):
    plt.text(i, v + 50000, f'{v:,}', ha='center', fontsize=9)

plt.tight_layout()
plt.savefig(os.path.join(VISUALS_DIR, 'top_countries.png'), dpi=150, bbox_inches='tight')
plt.close()
print(f"      Saved: visuals/top_countries.png")


# Visualization 4: Patent Trends Over Time (Line Chart)
print("\n[5/6] Creating Patent Trends chart...")

q4 = """
SELECT 
    year,
    COUNT(*) as patent_count
FROM patents
WHERE year > 1975 AND year <= 2025
GROUP BY year
ORDER BY year
"""
trends = conn.execute(q4).fetchdf()

plt.figure(figsize=(14, 7))
plt.plot(trends['year'], trends['patent_count'], marker='o', linewidth=2, markersize=4, color='steelblue')
plt.xlabel('Year', fontsize=12)
plt.ylabel('Number of Patents', fontsize=12)
plt.title('Patent Trends Over Time (1976-2025)', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.axvline(x=2000, color='red', linestyle='--', alpha=0.5, label='Year 2000')
plt.legend()

# Highlight the peak year
peak_year = trends.loc[trends['patent_count'].idxmax(), 'year']
peak_count = trends['patent_count'].max()
plt.annotate(f'Peak: {peak_count:,} patents\n({peak_year})', 
             xy=(peak_year, peak_count), 
             xytext=(peak_year-8, peak_count+20000),
             arrowprops=dict(arrowstyle='->', color='red'),
             fontsize=10)

plt.tight_layout()
plt.savefig(os.path.join(VISUALS_DIR, 'patent_trends.png'), dpi=150, bbox_inches='tight')
plt.close()
print(f"      Saved: visuals/patent_trends.png")


# Visualization 5: Top Countries Pie Chart
print("\n[6/6] Creating Top Countries Pie Chart...")

# Get top 8 countries, group others as "Other"
top8 = top_countries.head(8)
other_sum = top_countries.iloc[8:]['patent_count'].sum() if len(top_countries) > 8 else 0

if other_sum > 0:
    pie_data = pd.concat([top8, pd.DataFrame({'country': ['Other'], 'patent_count': [other_sum]})])
else:
    pie_data = top8

plt.figure(figsize=(10, 8))
colors = plt.cm.Set3(range(len(pie_data)))
plt.pie(pie_data['patent_count'], labels=pie_data['country'], autopct='%1.1f%%', 
        colors=colors, startangle=90, explode=[0.05] * len(pie_data))
plt.title('Patent Distribution by Country', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(VISUALS_DIR, 'countries_pie.png'), dpi=150, bbox_inches='tight')
plt.close()
print(f"      Saved: visuals/countries_pie.png")


#  Combined Dashboard (Multiple charts in one figure)
print("\n Creating Combined Dashboard...")

fig, axes = plt.subplots(2, 2, figsize=(14, 12))
fig.suptitle('Patent Data Dashboard', fontsize=16, fontweight='bold')

# Subplot 1: Top Inventors (Top 5)
ax1 = axes[0, 0]
top5_inventors = top_inventors.head(5)
ax1.barh(range(len(top5_inventors)), top5_inventors['patent_count'], color='steelblue')
ax1.set_yticks(range(len(top5_inventors)))
ax1.set_yticklabels(top5_inventors['name'])
ax1.set_xlabel('Patents')
ax1.set_title('Top 5 Inventors')
ax1.invert_yaxis()

# Subplot 2: Top Companies (Top 5)
ax2 = axes[0, 1]
top5_companies = top_companies.head(5)
ax2.barh(range(len(top5_companies)), top5_companies['patent_count'], color='coral')
ax2.set_yticks(range(len(top5_companies)))
ax2.set_yticklabels(top5_companies['name'])
ax2.set_xlabel('Patents')
ax2.set_title('Top 5 Companies')
ax2.invert_yaxis()

# Subplot 3: Patent Trends (Last 10 years)
ax3 = axes[1, 0]
recent_trends = trends.tail(10)
ax3.plot(recent_trends['year'], recent_trends['patent_count'], marker='o', linewidth=2, color='green')
ax3.set_xlabel('Year')
ax3.set_ylabel('Patents')
ax3.set_title('Patent Trends (Last 10 Years)')
ax3.grid(True, alpha=0.3)

# Subplot 4: Top Countries (Top 5)
ax4 = axes[1, 1]
top5_countries = top_countries.head(5)
ax4.bar(top5_countries['country'], top5_countries['patent_count'], color='purple')
ax4.set_xlabel('Country')
ax4.set_ylabel('Patents')
ax4.set_title('Top 5 Countries')
ax4.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig(os.path.join(VISUALS_DIR, 'dashboard.png'), dpi=150, bbox_inches='tight')
plt.close()
print(f"      Saved: visuals/dashboard.png")

# Close connection
conn.close()


print(" ALL VISUALIZATIONS CREATED SUCCESSFULLY!")
print("\n Visualizations saved in: reports/visuals/")

