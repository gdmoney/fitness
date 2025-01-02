# counta the total number of missed workouts by adding the monthly totals

import re

def count_missed_workouts(file_path):
    missed_workout_count = 0
    missed_workout_pattern = re.compile(r'Missed Workouts: (\d+)')
    
    with open(file_path, 'r') as file:
        for line in file:
            match = missed_workout_pattern.search(line)
            if match:
                missed_workout_count += int(match.group(1))
    
    return missed_workout_count

file_path = 'README.md'  # Path to your README.md file
total_missed_workouts = count_missed_workouts(file_path)
print(f'Total missed workouts: {total_missed_workouts}')