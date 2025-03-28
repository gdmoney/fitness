import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import re
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_weekly_sets(text: str) -> pd.DataFrame:
    """Extracts weekly sets data from the given text."""
    paragraphs = text.split('\n\n')
    weekly_data = []

    for para in paragraphs:
        try:
            sets = extract_sets_from_paragraph(para)
            date = extract_date_from_paragraph(para)
            if date and date.year in [2024, 2025]:
                weekly_data.append({'Date': date, 'Sets': sets})
        except ValueError as e:
            logging.warning(f"Skipping paragraph due to error: {e}")

    df = pd.DataFrame(weekly_data).sort_values('Date')
    return df

def extract_sets_from_paragraph(para: str) -> int:
    """Extracts the number of sets from a paragraph."""
    set_match = re.search(r'Total number of sets: (\d+)', para)
    if set_match:
        return int(set_match.group(1))
    raise ValueError("Sets not found in paragraph")

def extract_date_from_paragraph(para: str) -> datetime:
    """Extracts the date from the 7th line of a paragraph."""
    lines = para.split('\n')
    if len(lines) >= 7:
        date_match = re.search(r'(\d{4})[.-](\d{2})[.-](\d{2})', lines[6])
        if date_match:
            return datetime.strptime(date_match.group(0), '%Y.%m.%d')
    raise ValueError("Date not found in paragraph")

def plot_weekly_sets(df: pd.DataFrame) -> None:
    """Plots the weekly sets data."""
    plt.figure(figsize=(15, 8))
    plt.plot(df['Date'], df['Sets'], marker='o', linestyle='-', linewidth=2)
    plt.title('Sets per Week (2024-2025)', fontsize=14, pad=20)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Number of Sets', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(df['Date'], df['Date'].dt.strftime('%Y.%m.%d'), rotation=45)
    plt.tight_layout()
    plt.show()

def main() -> None:
    """Main function to read data, extract weekly sets, and plot them."""
    try:
        with open('README.md', 'r') as file:
            content = file.read()
        df = extract_weekly_sets(content)
        plot_weekly_sets(df)
    except FileNotFoundError:
        logging.error("README.md file not found.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()