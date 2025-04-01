# pip install pandas matplotlib

import pandas as pd
import matplotlib.pyplot as plt
import re

# Read the data from the file
with open('README.md', 'r') as file:
    data = file.readlines()

# Extract weekly recap data
weekly_data = []
for line in data:
    match = re.match(r'\*\*Recap\*\* - .* Total number of sets: (\d+)', line)
    if match:
        sets = int(match.group(1))
        weekly_data.append(sets)

# Create a DataFrame
df = pd.DataFrame(weekly_data, columns=['Total Sets'])

# Generate a date range for the weeks
df['Week'] = pd.date_range(start='2025-01-01', periods=len(df), freq='W')

# Plot the data
plt.figure(figsize=(10, 6))
plt.plot(df['Week'], df['Total Sets'], marker='o')
plt.title('Total Number of Sets per Week')
plt.xlabel('Week')
plt.ylabel('Total Sets')
plt.grid(True)
plt.show()