import requests
import subprocess
import os
import pandas as pd
import re
from Levenshtein import distance
from datetime import datetime

def check_rate_limit(username, token):
    session = requests.Session()
    session.auth = (username, token)

    response = session.get('https://api.github.com/rate_limit')

    rate_limit_info = response.json()
    print(rate_limit_info)


def get_git_shortlog(repoName, repoPath):
    command = 'git shortlog --until="2015-08-25" -sne --all --format="%aN <%aE>" --no-merges'
    dir = repoPath + repoName
    os.chdir(dir)
    try:
        # Run the command and capture the output
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        output_lines = result.stdout.split('\n')

        # Remove any empty lines from the output
        output_lines = [line.strip() for line in output_lines if line.strip()]

        return output_lines
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        return None


def findInString(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]


def mapInitials(string1, string2): # function to check if one username is the initials of another, so it maps them toe ach other
    if (len(string1) <= 3):
        initials_string = string1
        full_string = string2
    elif (len(string2) <= 3):
        initials_string = string2
        full_string = string1
    else:
        return False
    while len(full_string) > 0 and len(initials_string) > 0\
        and (full_string[-1] == '_' or full_string[-1] == '.' or initials_string[-1] == '.' or initials_string[-1] == '.'):
        if (full_string[-1] == '.' or full_string[-1] == '_'):  # ensuring name does not end by separator ('.' or '_')
            full_string = full_string[:-1]
        if (initials_string[-1] == '.' or initials_string[-1] == '_'):
            initials_string = initials_string[:-1]

    separator_indexes = findInString(full_string, ' ')
    if not separator_indexes:
        separator_indexes = findInString(full_string, '.')
        if not separator_indexes:
            separator_indexes = findInString(full_string, '_')
            if not separator_indexes:
                    return False
    if len(initials_string) == len(separator_indexes) + 1 and initials_string[0] == full_string[0]:
        separator_ii = 0
        for initial in initials_string[1:]:
            if initial != full_string[separator_indexes[separator_ii] + 1]:
                return False
            separator_ii += 1
        return True
    return False


def get_duplicates():
    lines = get_git_shortlog(repo_name, repoPath=reposPath)
    authorList = []
    commitList = []
    emailList = []
    duplicates = {}
    for line in lines:
        line.strip()
        commitList.append(int(line.split('\t')[0].strip()))
        authorMail = line.split('\t')[1].strip()
        authorList.append(authorMail.split('<')[0].strip())
        emailList.append(authorMail.split('<')[1].strip()[:-1])
    k = 0
    l = 1
    size = len(authorList)
    for k in range(len(authorList)):
        if (k == size - 1):
            break

        for l in reversed(range(k + 1, len(authorList))):

            string1 = authorList[k].replace(' ', '').lower()
            string2 = authorList[l].replace(' ', '').lower()
            initials_match = mapInitials(string1, string2)

            string1 = re.sub("[\(\[].*?[\)\]]", "", string1)
            string2 = re.sub("[\(\[].*?[\)\]]", "", string2)
            email_initials_match = False
            email1 = emailList[k]  # .split('@')[0]
            email2 = emailList[l]  # .split('@')[0]
            #   email_initials_match = mapInitials(email1, email2)

            if ((distance(string1, string2) < 2 and len(string1) > 3 and len(string2) > 3) or
                    (string1 == string2) or
                    (email1 == email2) or
                    initials_match or
                    email_initials_match):
                # print('Duplicates: ' + string1 + ' at ' + str(k) + ' - ' + string2 + ' at ' + str(l))
                if duplicates.get(authorList[k]) is not None:
                    duplicates.get(authorList[k]).append(authorList[l])
                else:
                    duplicates[authorList[k]] = [authorList[l]]
                commitList[k] = commitList[k] + commitList[l]
                authorList.pop(l)
                commitList.pop(l)
                emailList.pop(l)
                size -= 1
    return duplicates


def get_all_issues_before_date(repo_owner, repo_name, token, before_date):
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/issues'
    issues = []

    page = 1
    while True:
        params = {'page': page, 'per_page': 100, 'state': 'all'}  # Include both open and closed issues
        response = requests.get(url, params=params, auth=(repo_owner, token))

        if response.status_code == 200:
            current_issues = response.json()
            if not current_issues:
                break

            # Include issues created before the specified date
            issues.extend(issue for issue in current_issues if issue['created_at'] < before_date)

            page += 1
        else:
            print(f"Failed to retrieve issues. Status code: {response.status_code}")
            return None

    return issues

def count_issues_per_assignee(issues, token):
    assignee_counts = {}
    assignee_info = {}

    for issue in issues:
        assignees = issue.get('assignees', [])
        for assignee in assignees:
            login = assignee.get('login')
            if login:
                assignee_counts[login] = assignee_counts.get(login, 0) + 1

    # Fetch and print names of assignees
    for assignee, count in assignee_counts.items():
        user_info = get_user_details(assignee, token)
        name = user_info.get('name', 'N/A')
        assignee_info[assignee] = (name, count, 0)
        print(f"{assignee} ({name}): {count} issues")

    return assignee_info

def get_user_details(username, token):
    url = f'https://api.github.com/users/{username}'
    response = requests.get(url, auth=(username, token))

    if response.status_code == 200:
        user_details = response.json()
        return user_details
    else:
        print(f"Failed to retrieve user details for {username}. Status code: {response.status_code}")
        return None

def print_issue_info(issue):
    print(f"Issue #{issue['number']}: {issue['title']}")
    print(f"Status: {issue['state']}")
    if issue['assignees']:
        assignees = [assignee['login'] for assignee in issue['assignees']]
        print(f"Assignees: {', '.join(assignees)}")
    else:
        print("No assignees")

username = "AshPlusPlus"
repo_owner = 'Leaflet'
repo_name = 'Leaflet'
token = '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'
before_date = '2015-08-25T00:00:00Z'  # Replace with your desired date
reposPath = 'C:/Users/ahmed/Documents/GitHub/Thesis/'
targetPath = reposPath + 'XXrepostatsXX/'
df = pd.read_excel('C:/Users/ahmed/Desktop/Thesis Prog/dataset.xlsx')
df = df.reset_index()


check_rate_limit(username, token)
current_time = datetime.now().strftime("%H:%M")
print(f"\nCurrent Time: {current_time}")

all_issues_before_date = get_all_issues_before_date(repo_owner, repo_name, token, before_date)

current_time = datetime.now().strftime("%H:%M")
print(f"\nCurrent Time: {current_time}")

if all_issues_before_date:
    # print(f"Issues in {repo_owner}/{repo_name} before {before_date}:")
    # for issue in all_issues_before_date:
    #     print_issue_info(issue)
    #     print()

    # Count the number of issues per assignee and fetch their names
    assignee_info = count_issues_per_assignee(all_issues_before_date, token)


    duplicates = get_duplicates()
    commitsFile = open(targetPath + repo_name + '/commits.txt', "r", encoding='utf-8', errors='ignore')
    lines = commitsFile.readlines()
    issues = []

    current_time = datetime.now().strftime("%H:%M")
    print(f"\nCurrent Time: {current_time}")

    for line in lines:
        author = line.split('\t')[1].strip()
        found = False
        for assignee, info in assignee_info.items():
            if (author.lower() == info[0].lower() or author.lower() == assignee.lower()) and info[2] == 0:
                temp = assignee_info[assignee]
                assignee_info[assignee] = (temp[0], temp[1], 1)
                found = True
            else:
                if author in duplicates.keys():
                    for duplicate in duplicates[author]:
                        if (duplicate.lower() == assignee.lower() or duplicate.lower() == info[0].lower()) and info[2] == 0:
                            temp = assignee_info[assignee]
                            assignee_info[assignee] = (temp[0], temp[1], 1)
                            found = True
                            print(f'found in duplicates, match: {duplicate} and {assignee} or {info[0]}')
                            break

            if found:
                    issues.append(info[1])
                    break
        if not found:
                issues.append(0)

    issuesFile = open('issues.txt', "w", encoding='utf-8', errors='ignore')
    for issue in issues:
        issuesFile.write(f'{issue}\n')





else:
    print("No issues found.")

check_rate_limit(username,token)
current_time = datetime.now().strftime("%H:%M")
print(f"\nCurrent Time: {current_time}")
