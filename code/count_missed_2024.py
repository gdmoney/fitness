# counts the total number of missed workouts in 2024 by adding the monthly totals

import re
from datetime import datetime

def extract_missed_workouts(lines):
    total_missed = 0
    in_2024 = False
    
    for line in lines:
        # Check for year header to know we're in 2024 section
        if '## 2024' in line:
            in_2024 = True
        elif '## 2023' in line:  # Stop when we hit 2023
            break
            
        if not in_2024:
            continue
            
        # Look for "missed workouts: N" pattern
        match = re.search(r'(\w+) missed workouts:\s*(\d+)', line)
        if match:
            missed = int(match.group(2))
            total_missed += missed
            print(f"{match.group(1)}: {missed} missed workouts")
            
    return total_missed

if __name__ == "__main__":
    file_path = 'README.md'  # Adjust path if necessary
    
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    total = extract_missed_workouts(lines)
    print(f"\nTotal number of missed workouts in 2024: {total}")
