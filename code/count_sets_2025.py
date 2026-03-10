# counts the total number of sets in 2025 by adding the weekly totals

import re
from datetime import datetime

def extract_weekly_sets(lines):
    total_sets = 0
    in_2025 = False
    
    for line in lines:
        # Check for year header to know we're in 2025 section
        if '## 2025' in line:
            in_2025 = True
        elif '## 2024' in line:  # Stop when we hit 2024
            break
            
        if not in_2025:
            continue
            
        # Look for "Total number of sets: N" pattern
        match = re.search(r'Total number of sets:\s*(\d+)', line)
        if match:
            sets = int(match.group(1))
            total_sets += sets
            
    return total_sets

if __name__ == "__main__":
    file_path = 'README.md'  # Adjust path if necessary
    
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    total = extract_weekly_sets(lines)
    print(f"Total number of sets in 2024: {total}")