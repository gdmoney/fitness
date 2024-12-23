import requests

def get_readme_content(repo_owner, repo_name):
    url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/main/README.md"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Error fetching README.md: {response.status_code}")
        return None

def count_phrase_in_readme(phrase, readme_content):
    return readme_content.count(phrase)

if __name__ == "__main__":
    repo_owner = "gdmoney"
    repo_name = "fitness"
    phrase = "Total number of sets"

    readme_content = get_readme_content(repo_owner, repo_name)
    if readme_content:
        count = count_phrase_in_readme(phrase, readme_content)
        print(f"The phrase '{phrase}' appears {count} times in the README.md file.")