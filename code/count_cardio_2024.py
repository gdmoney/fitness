import re

def count_cardio_days(filename, year):
    with open(filename, 'r') as f:
        content = f.read()
        
    # Find the 2024 section
    pattern = r'## ' + str(year) + r'(.*?)(?=## \d{4}|\Z)'
    year_section = re.search(pattern, content, re.DOTALL)
    
    if year_section:
        # Count occurrences of '***`Cardio`***' in the 2024 section
        cardio_pattern = r'\*\*\*`Cardio`\*\*\*'
        cardio_count = len(re.findall(cardio_pattern, year_section.group(1)))
        return cardio_count
    return 0

# Test the function
cardio_days = count_cardio_days('README.md', 2024)
print(f"Number of Cardio only days in 2024: {cardio_days}")