import subprocess
import os
import pandas as pd
import re
from Levenshtein import distance
import datetime

def get_commit_dates(repo_pathm, avl):
    os.chdir(repo_path)
    if avl == 1:
        cmd = 'git log --all --format="%an;;;%aE:::%ad" --date=short --until="2015-08-25"'
    else:
        cmd = 'git log --all --format="%an;;;%aE:::%ad" --date=short --until="2016-09-25"'
    try:
        #output = subprocess.check_output(cmd, cwd=repo_path, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
        git_log_output_bytes = subprocess.check_output(cmd, shell=True)
        git_log_output = git_log_output_bytes.decode("utf-8", errors='ignore')
        return git_log_output.splitlines()
    except subprocess.CalledProcessError as e:
        print("Error executing Git command:", e.output)
        return []

def count_unique_days(commit_dates):
    developer_days = {}
    for line in commit_dates:
        parts = line.split(':::')
        if len(parts) == 2:
            author_name, date_str = parts
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            unique_days = developer_days.get(author_name, set())
            unique_days.add(date.date())
            developer_days[author_name] = unique_days
    return developer_days

if __name__ == "__main__":

    df = pd.read_excel('C:/Users/ahmed/Desktop/Thesis Prog/dataset.xlsx')
    df = df.reset_index()
    reposPath = 'C:/Users/ahmed/Documents/GitHub/Thesis/'
    targetPath = reposPath + 'XXrepostatsXX/'

    for index, row in df.iterrows():

        #   print(row['AVL'])
        repoName = row['Repository']
        print("Working in " + repoName + "...")
        repo_path = reposPath + repoName
        # repo_path = "C:/Users/ahmed/Documents/GitHub/Thesis/androidannotations"
        print('\tGenerating files...')
        commit_dates = get_commit_dates(repo_path, row['AVL'])
        authorList = []
        emailList = []
        daysList = []
        if commit_dates:
            developer_days_worked = count_unique_days(commit_dates)
            for author_email, days in developer_days_worked.items():
                authorList.append(author_email.split(";;;")[0])
                emailList.append(author_email.split(";;;")[1])
                daysList.append(len(days))
                #num_days = len(days)
        else:
            print(f"Error! No commit dates found for {repoName}.")
            continue

        duplicates = {}
        size = len(authorList)
        print('\tEliminating duplicates...')
        for k in range(len(authorList)):
            if (k == size - 1):
                break
            for l in reversed(range(k + 1, len(authorList))):
                if k == l:
                    print('here')
                string1 = authorList[k].replace(' ', '').lower()
                string2 = authorList[l].replace(' ', '').lower()
                initials_match = False
                # if (len(string1) > 0 and len(string2) > 0):
                #    initials_match = mapInitials(string1, string2)

                string1 = re.sub("[\(\[].*?[\)\]]", "", string1)
                string2 = re.sub("[\(\[].*?[\)\]]", "", string2)
                email1 = emailList[k]  # .split('@')[0]
                email2 = emailList[l]  # .split('@')[0]
                email_initials_match = False
                # if (len(email1) > 0 and len(email2) > 0):
                #    email_initials_match = mapInitials(email1, email2)

                if ((distance(string1, string2) < 2 and len(string1) > 3 and len(string2) > 3) or
                        (string1 == string2) or
                        (email1 == email2) or
                        initials_match or
                        email_initials_match):
                    #   print('Duplicates: ' + string1 + ' at ' + str(k) + ' - ' + string2 + ' at ' + str(l))
                    if duplicates.get(authorList[k]) is not None:
                        duplicates.get(authorList[k]).append(authorList[l])
                    else:
                        duplicates[authorList[k]] = [authorList[l]]
                    daysList[k] = daysList[k] + daysList[l]
                    authorList.pop(l)
                    daysList.pop(l)
                    emailList.pop(l)
                    size -= 1

        commitsFile = open(targetPath + repoName + '/commits.txt', "r", encoding='utf-8', errors='ignore')
        lines = commitsFile.readlines()
        newAuthorsList = []
        newDaysList = []

        for line in lines:
            author = line.split('\t')[1].strip()
            if author in authorList:
                newAuthorsList.append(author)
                newDaysList.append(daysList[authorList.index(author)])
            else:
                for authorItem in duplicates.keys():
                    if author in duplicates[authorItem]:
                        newAuthorsList.append(author)
                        newDaysList.append(daysList[authorList.index(authorItem)])
                        break
        daysFile = open(targetPath + repoName + '/daysWorked.txt', "w", encoding='utf-8', errors='ignore')
        i = 0
        for line in lines:
            author = line.split('\t')[1].strip()
            if author not in newAuthorsList:
                daysFile.write('\n')
            else:
                daysFile.write(str(newDaysList[i]) + '\n')
                i += 1

        daysFile.close()



    # repo_path = "C:/Users/ahmed/Documents/GitHub/Thesis/androidannotations"  # Change this to your Git repo path
    #
    # author_files = get_commit_dates(repo_path)
    #
    # if commit_dates:
    #     developer_days_worked = count_unique_days(commit_dates)
    #     for author_email, days in developer_days_worked.items():
    #         num_days = len(days)
    #         print(f"{author_email} worked on the project for {num_days} days.")
    # else:
    #     print("No commit dates found.")
