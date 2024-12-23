import re

def read_readme(file_path):
    with open(file_path, 'r') as file:
        return file.readlines()

def extract_set_totals(lines):
    pattern = re.compile(r"Total number of sets:\s*(\d+)")
    totals = []
    for line in lines:
        match = pattern.search(line)
        if match:
            totals.append(int(match.group(1)))
    return totals

def calculate_total_sets(totals):
    return sum(totals)

if __name__ == "__main__":
    file_path = '/Users/gdavitiani/Documents/GitHub/fitness/README.md'  # Adjust the path if necessary
    lines = read_readme(file_path)
    totals = extract_set_totals(lines)
    total_sets = calculate_total_sets(totals)
    
    print(f"The total number of sets is: {total_sets}")