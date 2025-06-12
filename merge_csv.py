import pandas as pd

# Read the CSV files
df1 = pd.read_csv('/Users/nghilethanh/Project/UPWORK - Experienced Data Analyst with Web Scraping and API Expertise Needed /output/processed_data_20250601_185002.csv')
df2 = pd.read_csv('/Users/nghilethanh/Project/UPWORK - Experienced Data Analyst with Web Scraping and API Expertise Needed /output/processed_data_20250602_174839.csv')

# Get the position of address column in df1
address_position = df1.columns.get_loc('address') if 'address' in df1.columns else None

# First, drop the address column from df1 if it exists
if 'address' in df1.columns:
    df1 = df1.drop('address', axis=1)

# Select only ukprn and address columns from df2
df2_subset = df2[['ukprn', 'address']]

# Perform left join on ukprn
merged_df = df1.merge(df2_subset, on='ukprn', how='left')

# Remove the region column if it exists
if 'region' in merged_df.columns:
    merged_df = merged_df.drop('region', axis=1)

# Reorder columns to put address back in its original position
if address_position is not None:
    cols = merged_df.columns.tolist()
    cols.remove('address')
    cols.insert(address_position, 'address')
    merged_df = merged_df[cols]

# Save the merged result
output_path = '/Users/nghilethanh/Project/UPWORK - Experienced Data Analyst with Web Scraping and API Expertise Needed /output/merged_data.csv'
merged_df.to_csv(output_path, index=False)

print(f"Files merged successfully. Result saved to: {output_path}")
print(f"Number of rows in merged file: {len(merged_df)}")
print("\nColumns in merged file:")
print(merged_df.columns.tolist()) 