# 1. Import necessary libraries

import pandas as pd

# 2. Loading the dataset

df = pd.read_csv("tuition_fees_50_countries.csv")

# 3. Preview the dataset

print(df.head()) # Show the first 5 rows
print(df.info()) # Shows column types, nulls
print(df.describe()) #Shows summary statistics
print(df.isnull().sum()) # Shows me where the missing values are

import matplotlib.pyplot as plt
import seaborn as sns

# Distribution of tuition fees

sns.histplot(df['Average Tuition Fee (USD)'], bins=50)
plt.title("Distribution of Tuition Fees")
plt.xlabel("tuition_usd")
plt.ylabel("Count")
plt.show()

# Tuition fee by degree level

sns.boxplot(x = 'Degree_level', y = 'Average Tuition Fee (USD)', data=df)
plt.title("Tuition Fees by Degree Level")
plt.xticks(rotation = 45)
plt.show()

# Tuition by Country

top_countries = df['Country'].value_counts().head(10).index
sns.boxplot(x = 'Country', y = 'tuition_usd', data = df [df['Country'].isin(topcountries)])
plt.xticks(rotation = 45)
plt.title("Tuition Fees by Top 10 Countries")
plt.show()

# Tuition by Private vs Public

sns.boxplot(x = 'Public or Private', y = 'tuition_usd', data = df)
plt.title("Tuition: Public vs Private Universities")
plt.show()