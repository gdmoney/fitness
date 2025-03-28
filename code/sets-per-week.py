import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import re
from datetime import datetime

def extract_weekly_sets(text):
    # Split text into paragraphs (weekly blocks)
    paragraphs = text.split('\n\n')
    
    weekly_data = []
    
    for para in paragraphs:
        # Look for "Total number of sets:" in the paragraph
        set_match = re.search(r'Total number of sets: (\d+)', para)
        if set_match:
            sets = int(set_match.group(1))
            
            # Get the first date from the 7th line (Monday)
            lines = para.split('\n')
            if len(lines) >= 7:  # Ensure there are enough lines
                date_match = re.search(r'(\d{4})[.-](\d{2})[.-](\d{2})', lines[6])
                if date_match:
                    date_text = date_match.group(0)
                    date = datetime.strptime(date_text, '%Y.%m.%d')
                    
                    # Only include 2024 and 2025 data
                    if date.year in [2024, 2025]:
                        weekly_data.append({'Date': date, 'Sets': sets})
    
    # Convert to DataFrame
    df = pd.DataFrame(weekly_data)
    df = df.sort_values('Date')
    
    return df

def plot_weekly_sets(df):
    plt.figure(figsize=(15, 8))
    plt.plot(df['Date'], df['Sets'], marker='o', linestyle='-', linewidth=2)
    
    plt.title('Sets per Week (2024-2025)', fontsize=14, pad=20)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Number of Sets', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Format x-axis with YYYY.MM.DD
    ax = plt.gca()
    
    # Use the actual dates from the data for x-axis ticks
    plt.xticks(df['Date'], df['Date'].dt.strftime('%Y.%m.%d'), rotation=45)
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    plt.show()

def main():
    # Read file content
    with open('README.md', 'r') as file:
        content = file.read()
    
    # Extract and plot data
    df = extract_weekly_sets(content)
    plot_weekly_sets(df)

if __name__ == "__main__":
    main()