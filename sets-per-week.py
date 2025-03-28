import re
import pandas as pd
import matplotlib.pyplot as plt

# Function to parse the workout entries
def parse_workout_entries(readme_content):
    workout_entries = []
    in_2024_or_2025 = False
    year = None
    
    for line in readme_content.split('\n'):
        # Check for year header to know we're in 2024 or 2025 section
        if '## 2024' in line or '## 2025' in line:
            in_2024_or_2025 = True
            year = int(line.strip('#').strip())
            continue
        elif '## 2023' in line:  # Stop when we hit 2023
            break
            
        if not in_2024_or_2025:
            continue
        
        # Check for total number of sets
        match_total_sets = re.match(r'.*Total number of sets:\s*(\d+)', line)
        if match_total_sets and year:
            total_sets = int(match_total_sets.group(1))
            week = len(workout_entries) + 1  # Incremental week number as per order in the log
            workout_entries.append({'year': year, 'week': week, 'sets': total_sets})
    
    return workout_entries

# Extract workout entries from README.md content
with open('README.md', 'r') as file:
    readme_content = file.read()

workout_entries = parse_workout_entries(readme_content)

# Create a DataFrame from the parsed workout entries
df = pd.DataFrame(workout_entries)

# Filter data for the years 2024 and 2025
df = df[(df['year'] == 2024) | (df['year'] == 2025)]

# Create the time series graph
plt.figure(figsize=(12, 6))
for year in [2024, 2025]:
    yearly_data = df[df['year'] == year]
    plt.plot(yearly_data['week'], yearly_data['sets'], label=f'{year}')

plt.xlabel('Week')
plt.ylabel('Number of Sets')
plt.title('Number of Sets per Week (2024 & 2025)')
plt.legend()
plt.grid(True)
plt.show()