import subprocess
import os
import pandas as pd
import re
from Levenshtein import distance


def count_files_by_developer(repo_path, avl):
    developer_file_counts = {}

    try:
        # Change to the Git repository directory
        os.chdir(repo_path)

        # Run 'git log' with '--name-status' and '--until' options to get commits until the specified date
        if avl == 1:
            git_log_command = f"git log --format='%an;;;%aE' --name-status --until='2015-08-25'"
        else:
            git_log_command = f"git log --format='%an;;;%aE' --name-status --until='2016-09-25'"

        git_log_output_bytes = subprocess.check_output(git_log_command, shell=True)
        git_log_output = git_log_output_bytes.decode("utf-8", errors='ignore')

        # Initialize a dictionary to keep track of files modified or added by each developer
        developer_file_changes = {}

        for line in git_log_output.splitlines():
            if line.startswith("'"):
                current_developer = line.strip("'")

            elif line.startswith(("M", "A")):
                # Exclude file renames (lines starting with 'R')
                if not line.startswith("R"):
                    # Get the file status and file name
                    parts = line.split('\t')
                    file_status = parts[0]
                    file_name = parts[1]

                    # Increment counts for the current author
                    if current_developer not in developer_file_changes:
                        developer_file_changes[current_developer] = set()
                    developer_file_changes[current_developer].add(file_name)

        # Calculate the count of unique files for each developer
        for developer, files_changed in developer_file_changes.items():
            developer_file_counts[developer] = len(files_changed)

        return developer_file_counts
    except FileNotFoundError:
        return None

if __name__ == "__main__":
    df = pd.read_excel('C:/Users/ahmed/Desktop/Thesis Prog/dataset.xlsx')
    df = df.reset_index()
    reposPath = 'C:/Users/ahmed/Documents/GitHub/Thesis/'
    targetPath = reposPath + 'XXrepostatsXX/'

    for index, row in df.iterrows():
     #   print(row['AVL'])
        repoName = row['Repository']
        if repoName != 'openage':
            continue
        print("Working in " + repoName + "...")
        repo_path = reposPath + repoName
        #repo_path = "C:/Users/ahmed/Documents/GitHub/Thesis/androidannotations"
        print('\tGenerating files...')
        author_files = count_files_by_developer(repo_path, row['AVL'])
        authorList = []
        emailList = []
        filesList = list(author_files.values())
        for author_email in author_files.keys():
            authorList.append(author_email.split(";;;")[0])
            emailList.append(author_email.split(";;;")[1])

        duplicates = {}
        size = len(authorList)
        print('\tEliminating duplicates...')
        for k in range(len(authorList)):
            if (k == size - 1):
                break
            for l in reversed(range(k + 1, len(authorList))):
                if k ==l:
                    print('here')
                string1 = authorList[k].replace(' ', '').lower()
                string2 = authorList[l].replace(' ', '').lower()
                initials_match = False
                #if (len(string1) > 0 and len(string2) > 0):
                #    initials_match = mapInitials(string1, string2)

                string1 = re.sub("[\(\[].*?[\)\]]", "", string1)
                string2 = re.sub("[\(\[].*?[\)\]]", "", string2)
                email1 = emailList[k]#.split('@')[0]
                email2 = emailList[l]#.split('@')[0]
                email_initials_match = False
                #if (len(email1) > 0 and len(email2) > 0):
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
                    filesList[k] = filesList[k] + filesList[l]
                    authorList.pop(l)
                    filesList.pop(l)
                    emailList.pop(l)
                    size -= 1



        commitsFile = open(targetPath + repoName + '/commits.txt', "r", encoding='utf-8', errors='ignore')
        lines = commitsFile.readlines()
        newAuthorsList = []
        newFilesList = []

        for line in lines:
            author = line.split('\t')[1].strip()
            if author in authorList:
                newAuthorsList.append(author)
                newFilesList.append(filesList[authorList.index(author)])
            else:
                for authorItem in duplicates.keys():
                    if author in duplicates[authorItem]:
                        newAuthorsList.append(author)
                        newFilesList.append(filesList[authorList.index(authorItem)])
                        break
        filesFile = open(targetPath + repoName + '/files.txt', "w", encoding='utf-8', errors='ignore')
        i = 0
        for line in lines:
            author = line.split('\t')[1].strip()
            if author not in newAuthorsList:
                filesFile.write('\n')
            else:
                filesFile.write(str(newFilesList[i]) + '\n')
                i += 1

        filesFile.close()
    # repo_address = input("Enter the Git repository path: ")
    # until_date = input("Enter the date (YYYY-MM-DD) until which to consider commits: ")
    #
    # if os.path.exists(repo_address):
    #     developer_counts = count_files_by_developer(repo_address, until_date)
    #
    #     if developer_counts is not None:
    #         print("Number of files modified/created (excluding renames) by each developer:")
    #         for developer, count in developer_counts.items():
    #             print(f"{developer}: {count} files")
    #     else:
    #         print("Invalid Git repository.")
    # else:
    #     print("Invalid repository path.")
