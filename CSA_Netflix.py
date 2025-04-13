# %% [markdown]
# # Content Statergy Analysis (NETFLIX)

# %%
# Requirements
import pandas as pd
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
import os

# createing a results directory if it doesn't exist to save the plots
os.makedirs("results", exist_ok=True)

# Set the default template for all plots
pio.templates.default = "plotly_white"

# %% [markdown]
# # Data Loading

# %%


# Load the dataset
data = pd.read_csv('data/netflix_content_2023.csv')
# Count the number of records in the dataset
record_count = len(data)
print(f"Total number of records in the dataset: {record_count}")
# Display the first few rows of the dataset
data.head()

# %% [markdown]
# # Data Cleaning

# %%
# Remove commas from Hours_Viewed and convert to float
data['Hours_Viewed'] = data['Hours_Viewed'].replace(',', '', regex=True).astype(float)

# Drop rows with NaN values in 'Hours_Viewed'
data = data.dropna(subset=['Hours_Viewed'])

# Drop rows where 'Hours_Viewed' is less than or equal to 0
data = data[data['Hours_Viewed'] > 0]

# Drop null values in 'Title' column
data = data.dropna(subset=['Title'])

# Ensure 'Title' is treated as a string
data['Title'] = data['Title'].astype(str)

# Check for duplicates in 'Title' column & keep the one with highest Hours_Viewed
data = data.sort_values(by='Hours_Viewed', ascending=False).drop_duplicates(subset=['Title'], keep='first')

# Count the number of records after cleaning
record_count = len(data)
print(f"Number of records after cleaning: {record_count}")

# Display the first few rows of the cleaned dataset
data.head()

# %% [markdown]
# # Exploratory Data Analysis (EDA) - Aggregations and Bar Charts

# %%
# Aggregate total hours viewed by Content_Type and sort by Hours_Viewed
content_type_agg = data.groupby('Content_Type')['Hours_Viewed'].sum().reset_index()
content_type_agg = content_type_agg.sort_values(by='Hours_Viewed', ascending=False)
# Format Hours_Viewed for bar labels (converting to billions with "B") 
content_type_agg['Hours_Viewed_Text'] = (content_type_agg['Hours_Viewed'] / 1e9).round(2).astype(str) + 'B'

# Aggregate total hours viewed by Language_Indicator and sort by Hours_Viewed
language_agg = data.groupby('Language_Indicator')['Hours_Viewed'].sum().reset_index()
language_agg = language_agg.sort_values(by='Hours_Viewed', ascending=False)
# Format Hours_Viewed for bar labels
language_agg['Hours_Viewed_Text'] = (language_agg['Hours_Viewed'] / 1e9).round(2).astype(str) + 'B'

# Aggregate by both Content_Type and Language_Indicator and sort by Hours_Viewed
content_language_agg = data.groupby(['Content_Type', 'Language_Indicator'])['Hours_Viewed'].sum().reset_index()
content_language_agg = content_language_agg.sort_values(by='Hours_Viewed', ascending=False)
# Format Hours_Viewed for bar labels
content_language_agg['Hours_Viewed_Text'] = (content_language_agg['Hours_Viewed'] / 1e9).round(2).astype(str) + 'B'

# Bar chart for Hours Viewed by Content Type
fig1 = px.bar(content_type_agg, x='Content_Type', y='Hours_Viewed', 
              title='Total Hours Viewed by Content Type', text='Hours_Viewed_Text')  
fig1.update_traces(textposition='auto')
fig1.show()
#fig1.write_image("results/fig1.png")

# Bar chart for Hours Viewed by Language
fig2 = px.bar(language_agg, x='Language_Indicator', y='Hours_Viewed', 
              title='Total Hours Viewed by Language', text='Hours_Viewed_Text')
fig2.update_traces(textposition='auto')
fig2.show()
#fig2.write_image("results/fig2.png")

# Bar chart for Hours Viewed by Content Type and Language
fig3 = px.bar(content_language_agg, x='Content_Type', y='Hours_Viewed', color='Language_Indicator',
              title='Hours Viewed by Content Type and Language', barmode='group', text='Hours_Viewed_Text')
fig3.update_traces(textposition='auto')
fig3.show()
#fig3.write_image("results/fig4.png")

# %% [markdown]
# # Growth Rate Analysis - Data Preparation

# %%
# Convert Release_Date to datetime
data['Release_Date'] = pd.to_datetime(data['Release_Date'], format='%d-%m-%Y')

# Sort by Release_Date
data_sorted = data.sort_values('Release_Date')

# Extract year from Release_Date
data_sorted['Year'] = data_sorted['Release_Date'].dt.year

# Aggregate by Year and Content_Type
year_content_agg = data_sorted.groupby(['Year', 'Content_Type'])['Hours_Viewed'].sum().reset_index()

# Aggregate by Year and Language_Indicator
year_language_agg = data_sorted.groupby(['Year', 'Language_Indicator'])['Hours_Viewed'].sum().reset_index()

# %% [markdown]
# # Growth Rate Analysis - Calculations

# %%
# Growth rate for Content Type
year_content_pivot = year_content_agg.pivot(index='Year', columns='Content_Type', values='Hours_Viewed').fillna(0)
year_content_pivot['Total'] = year_content_pivot.sum(axis=1)
year_content_pivot['Show_Growth_Rate'] = year_content_pivot['Show'].pct_change() * 100
year_content_pivot['Movie_Growth_Rate'] = year_content_pivot['Movie'].pct_change() * 100
year_content_pivot['Total_Growth_Rate'] = year_content_pivot['Total'].pct_change() * 100

# Growth rate for Language
year_language_pivot = year_language_agg.pivot(index='Year', columns='Language_Indicator', values='Hours_Viewed').fillna(0)
year_language_pivot['Total'] = year_language_pivot.sum(axis=1)
year_language_pivot['English_Growth_Rate'] = year_language_pivot['English'].pct_change() * 100
year_language_pivot['Korean_Growth_Rate'] = year_language_pivot['Korean'].pct_change() * 100

# %% [markdown]
# # Growth Rate Analysis - Visualizations

# %%
# Line plot for Hours Viewed by Year and Content Type
fig4 = px.line(year_content_agg, x='Year', y='Hours_Viewed', color='Content_Type',
               title='Hours Viewed by Year and Content Type', markers=True)
fig4.show()
#fig4.write_image("results/fig4.png")

# Line plot for Hours Viewed by Year and Language
fig5 = px.line(year_language_agg, x='Year', y='Hours_Viewed', color='Language_Indicator',
               title='Hours Viewed by Year and Language', markers=True)
fig5.show()
#fig5.write_image("results/fig5.png")

# %% [markdown]
# # Seasonal Viewership Analysis

# %%
# Define a function to assign seasons based on month
def get_season(month):
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    elif month in [9, 10, 11]:
        return 'Fall'

# Extract month from Release_Date and assign season
data_sorted['Month'] = data_sorted['Release_Date'].dt.month
data_sorted['Season'] = data_sorted['Month'].apply(get_season)

# Aggregate by Season and sort by Hours_Viewed
season_agg = data_sorted.groupby('Season')['Hours_Viewed'].sum().reset_index()
season_agg = season_agg.sort_values(by='Hours_Viewed', ascending=False)
# Format Hours_Viewed for bar labels
season_agg['Hours_Viewed_Text'] = (season_agg['Hours_Viewed'] / 1e9).round(2).astype(str) + 'B'

# Bar chart for Seasonal Viewership
fig6 = px.bar(season_agg, x='Season', y='Hours_Viewed', 
                    title='Total Hours Viewed by Season', text='Hours_Viewed_Text')
fig6.update_traces(textposition='auto')
fig6.show()
#fig6.write_image("results/fig6.png")

# %% [markdown]
# # Monthly Viewership Analysis

# %%
# Extract month from Release_Date
data_sorted['Month'] = data_sorted['Release_Date'].dt.month

# Aggregate by Month and sort by Hours_Viewed
month_agg = data_sorted.groupby('Month')['Hours_Viewed'].sum().reset_index()
month_agg = month_agg.sort_values(by='Hours_Viewed', ascending=False)
# Format Hours_Viewed for bar labels
month_agg['Hours_Viewed_Text'] = (month_agg['Hours_Viewed'] / 1e9).round(2).astype(str) + 'B'

# Map month numbers to names for better readability
month_names = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
               7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}
month_agg['Month_Name'] = month_agg['Month'].map(month_names)

# Bar chart for Monthly Viewership
fig7 = px.bar(month_agg, x='Month_Name', y='Hours_Viewed', 
                   title='Total Hours Viewed by Month', text='Hours_Viewed_Text')
fig7.update_traces(textposition='auto')
fig7.update_layout(xaxis_title='Month')
fig7.show()
#fig7.write_image("results/fig7.png")

# %% [markdown]
# # Weekly Viewership Analysis

# %%
# Extract day of week from Release_Date (0 = Monday, 6 = Sunday)
data_sorted['Day_of_Week'] = data_sorted['Release_Date'].dt.dayofweek

# Aggregate by Day of Week and sort by Hours_Viewed
week_agg = data_sorted.groupby('Day_of_Week')['Hours_Viewed'].sum().reset_index()
week_agg = week_agg.sort_values(by='Hours_Viewed', ascending=False)
# Format Hours_Viewed for bar labels
week_agg['Hours_Viewed_Text'] = (week_agg['Hours_Viewed'] / 1e9).round(2).astype(str) + 'B'

# Map day numbers to names
day_names = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 
             4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
week_agg['Day_Name'] = week_agg['Day_of_Week'].map(day_names)

# Bar chart for Weekly Viewership
fig8 = px.bar(week_agg, x='Day_Name', y='Hours_Viewed', 
                  title='Total Hours Viewed by Day of Week', text='Hours_Viewed_Text')
fig8.update_traces(textposition='auto')
fig8.update_layout(xaxis_title='Day of Week')
fig8.show()
#fig8.write_image("results/fig8.png")


