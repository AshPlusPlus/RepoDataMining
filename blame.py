import subprocess
import os
import pandas as pd
import re
from Levenshtein import distance
import datetime
import multiprocessing

def extract_developer_info(repo_path, file, avl):
    if avl == 1:
        cmd = f'git blame --line-porcelain --until="2015-08-25" "{file}"'
    else:
        cmd = f'git blame --line-porcelain --until="2016-09-25" "{file}"'

    try:
        output = subprocess.check_output(cmd, cwd=repo_path, shell=True, stderr=subprocess.STDOUT,
                                         universal_newlines=True, encoding='utf-8', errors='ignore')

        current_author = None
        current_email = None
        recent_author = None  # Initialize recent_author variable
        recent_email = None  # Initialize recent_email variable
        max_commit_time = 0  # Initialize with a timestamp of 0

        for line in output.splitlines():
            if line.startswith("author "):
                current_author = line[len("author "):].strip()
            elif line.startswith("author-mail "):
                current_email = line[len("author-mail "):].strip()
            elif line.startswith("author-time "):
                commit_time = int(line[len("author-time "):].strip())
                if commit_time > max_commit_time:
                    max_commit_time = commit_time
                    # Set the author and email for the most recent change
                    recent_author = current_author
                    recent_email = current_email

        return recent_author, recent_email

    except subprocess.CalledProcessError as e:
        print("Error executing Git blame for file:", file, "-", e.output)
        return None, None



def main(repo_path, avl):
    cmd = f'git ls-files'

    try:
        files = subprocess.check_output(cmd, cwd=repo_path, shell=True, stderr=subprocess.STDOUT,
                                        universal_newlines=True, encoding='utf-8', errors='ignore')
        files = files.splitlines()

        developer_info = {}  # Dictionary to store developer information

        # Create a pool of worker processes
        with multiprocessing.Pool() as pool:
            # Use pool.starmap to parallelize execution of extract_developer_info
            results = pool.starmap(extract_developer_info, [(repo_path, file, avl) for file in files])

        for author, email in results:
            if author:
                if author in developer_info:
                    developer_info[author][0] += 1  # Increment file count
                    if email:
                        developer_info[author][1] = email  # Set the email if available
                else:
                    developer_info[author] = [1, email or "N/A"]  # Initialize file count and email

        return developer_info

    except subprocess.CalledProcessError as e:
        print("Error executing Git ls-files command:", e.output)
        return {}

if __name__ == "__main__":
    # repo_path = "C:/Users/ahmed/Documents/GitHub/Thesis/androidannotations"  # Change this to your Git repo path
    # until_date = "2023-01-01"  # Specify the date until which you want blame information
    #
    # developer_info = main(repo_path, until_date)
    #
    # if developer_info:
    #     for developer, info in developer_info.items():
    #         num_files_blamed = info[0]
    #         email = info[1]
    #         print(f"{developer} contributed to {num_files_blamed} files, Email: {email}")
    # else:
    #     print("No blame information found.")

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
        developer_info = main(repo_path, row['AVL'])
        authorList = []
        emailList = []
        blameList = []
        if developer_info:
            for developer, info in developer_info.items():
                authorList.append(developer)
                email = info[1].replace("<", "").replace(">", "")
                emailList.append(email)
                blameList.append(info[0])
        else:
            print(f"Error! No blame data found for {repoName}.")
            continue

      #  print(authorList)
    #    print(emailList)
    #    print(daysList)

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
                    blameList[k] = blameList[k] + blameList[l]
                    authorList.pop(l)
                    blameList.pop(l)
                    emailList.pop(l)
                    size -= 1

        commitsFile = open(targetPath + repoName + '/commits.txt', "r", encoding='utf-8', errors='ignore')
        lines = commitsFile.readlines()
        newAuthorsList = []
        newBlameList = []

        for line in lines:
            author = line.split('\t')[1].strip()
            if author in authorList:
                newAuthorsList.append(author)
                newBlameList.append(blameList[authorList.index(author)])
            else:
                for authorItem in duplicates.keys():
                    if author in duplicates[authorItem]:
                        newAuthorsList.append(author)
                        newBlameList.append(blameList[authorList.index(authorItem)])
                        break
        blameFile = open(targetPath + repoName + '/filesBlame.txt', "w", encoding='utf-8', errors='ignore')
        i = 0
        for line in lines:
            author = line.split('\t')[1].strip()
            if author not in newAuthorsList:
                blameFile.write('\n')
            else:
                blameFile.write(str(newBlameList[i]) + '\n')
                i += 1

        blameFile.close()












