import pandas as pd

# Load the Excel file
file_path = 'functionalDataBase.xlsx'
df = pd.read_excel(file_path, engine='openpyxl')

# Remove hyperlinks but keep the text
for col in df.columns:
    if df[col].dtype == 'object':
        df[col] = df[col].str.replace(r'=HYPERLINK\("(.*?)"\)', r'\1', regex=True)

# Save the cleaned data to a CSV file
output_file_path = 'functionalDataBase_cleaned.csv'
df.to_csv(output_file_path, index=False)

print(f"Cleaned CSV file saved to {output_file_path}")
