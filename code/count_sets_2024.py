import re
from datetime import datetime

def parse_sets(exercise_text):
    # Split exercises by bullet points
    exercises = exercise_text.split('•')
    total_sets = 0
    
    for exercise in exercises:
        # Look for patterns like "x10x4", "x15x3", etc.
        match = re.search(r'x\d+x(\d+)', exercise)
        if match:
            total_sets += int(match.group(1))
            continue
            
        # Look for patterns like "10x3", "15x4", etc.
        match = re.search(r'\b\d+x(\d+)', exercise)
        if match:
            total_sets += int(match.group(1))
            
    return total_sets

def is_2024_entry(date_str):
    try:
        date = datetime.strptime(date_str, '%Y.%m.%d')
        return date.year == 2024
    except ValueError:
        return False

def count_daily_sets(workout_line):
    # Skip rest days or empty entries
    if '***`      `***' in workout_line:
        return 0
        
    # Split the line after the date and workout type
    parts = workout_line.split('***')
    if len(parts) < 3:
        return 0
        
    exercises = parts[2]  # Get the exercise portion
    return parse_sets(exercises)

def count_total_sets(lines):
    total_sets = 0
    for line in lines:
        # Look for date at start of line (YYYY.MM.DD)
        date_match = re.match(r'(\d{4}\.\d{2}\.\d{2})', line)
        if date_match:
            date = date_match.group(1)
            if is_2024_entry(date):
                sets = count_daily_sets(line)
                total_sets += sets
    return total_sets

if __name__ == "__main__":
    file_path = 'README.md'  # Adjust path if necessary
    
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    total = count_total_sets(lines)
    print(f"Total number of sets in 2024: {total}")