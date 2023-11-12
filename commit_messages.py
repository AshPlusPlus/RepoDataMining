import subprocess
import os
import pandas as pd
import re
from Levenshtein import distance


def get_commit_message_lengths(repo_path, avl):

    os.chdir(repo_path)


    author_messages = {}
    if avl == 1:
        git_log_command = 'git log --all --until="2015-08-25" --format="%aN;;;%aE:::%s"'
    else:
        git_log_command = 'git log --all --until="2019-09-25" --format="%aN;;;%aE:::%s"'
    try:
        git_log_output_bytes = subprocess.check_output(git_log_command, shell=True)
        git_log_output = git_log_output_bytes.decode("utf-8", errors='ignore')
    except subprocess.CalledProcessError as e:
        # Handle the subprocess error, e.g., print the error message.
        print(f"Subprocess error: {e}")
    except UnicodeDecodeError as e:
        # Handle the decoding error, e.g., print the error message.
        print(f"UnicodeDecodeError: {e}")
        git_log_output = git_log_output_bytes.decode("utf-8", errors='ignore')
    for line in git_log_output.split('\n'):
        if line:
            author, message = line.split(":::", 1)
            if author in author_messages:
                author_messages[author].append(message)
            else:
                author_messages[author] = [message]


    author_message_lengths = {}
    for author, messages in author_messages.items():
        total_length = sum(len(message) for message in messages)
        author_message_lengths[author] = total_length

    return author_message_lengths



# def count_files_by_developer(repo_path, avl, duplicates):
#     developer_file_counts = {}
#
#     try:
#         # Change to the Git repository directory
#         os.chdir(repo_path)
#
#         # Run 'git log' to get the commit history
#         if avl == 1:
#             git_log_command = f"git log --format='%an' --name-status --until='2015-08-25'"
#         else:
#             git_log_command = f"git log --format='%an' --name-status --until='2016-09-25'"
#
#         try:
#             git_log_output_bytes = subprocess.check_output(git_log_command, shell=True)
#             git_log_output = git_log_output_bytes.decode("utf-8", errors='ignore')
#            #git_log_output = subprocess.check_output(git_log_command, shell=True, universal_newlines=True)
#         except subprocess.CalledProcessError as e:
#             # Handle the subprocess error, e.g., print the error message.
#             print(f"Subprocess error: {e}")
#         except UnicodeDecodeError as e:
#             # Handle the decoding error, e.g., print the error message.
#             print(f"UnicodeDecodeError: {e}")
#             git_log_output = git_log_output_bytes.decode("utf-8", errors='ignore')
#
#         current_developer = None
#         unique_authors = set()  # Maintain a set of unique author names
#
#         for line in git_log_output.splitlines():
#             if line.startswith("'"):
#                 current_developer = line.strip("'")
#                 unique_authors.add(current_developer)  # Add the author to the set
#
#             elif line.startswith(("M", "A")):
#                 # Exclude file renames (lines starting with 'R')
#                 if not line.startswith("R"):
#                     # Increment counts for each unique author
#                     for author in unique_authors:
#                         developer_file_counts[author] = developer_file_counts.get(author, 0) + 1
#         if repo_path == 'C:/Users/ahmed/Documents/GitHub/Thesis/flask':
#             print('here')
#         if developer_file_counts != {} and duplicates != {}:
#             nodups_developer_file_counts = {}
#             for dev_name in developer_file_counts.keys():
#                 if dev_name in duplicates.keys():
#                     nodups_developer_file_counts[dev_name] = developer_file_counts[dev_name]
#                     for dev_duplicate in duplicates[dev_name]:
#                         nodups_developer_file_counts[dev_name] += developer_file_counts.get(dev_duplicate, 0)
#                 else:
#                     is_a_duplicate = False
#                     for duplicate_key in duplicates.keys():
#                         for dev_duplicate in duplicates[duplicate_key]:
#                             if dev_name == dev_duplicate:
#                                 is_a_duplicate = True
#                     if not is_a_duplicate:
#                         nodups_developer_file_counts[dev_name] = developer_file_counts[dev_name]
#
#             # for dev_name in duplicates.keys():
#             #     try:
#             #
#             #         nodups_developer_file_counts[dev_name] = developer_file_counts[dev_name]
#             #     except KeyError:
#             #         nodups_developer_file_counts[dev_name] = -1
#             #         print('\n' + dev_name + '\t' + repo_path + '\n')
#             #     for dup_dev_name in duplicates[dev_name]:
#             #         try:
#             #
#             #             nodups_developer_file_counts[dev_name] = nodups_developer_file_counts[dev_name] + developer_file_counts[dup_dev_name]
#             #         except KeyError:
#             #             nodups_developer_file_counts[dev_name] = -1
#
#             return nodups_developer_file_counts
#         return developer_file_counts
#     except FileNotFoundError:
#         return None

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


if __name__ == "__main__":
    df = pd.read_excel('C:/Users/ahmed/Desktop/Thesis Prog/dataset.xlsx')
    df = df.reset_index()
    reposPath = 'C:/Users/ahmed/Documents/GitHub/Thesis/'
    targetPath = reposPath + 'XXrepostatsXX/'

    for index, row in df.iterrows():
        repoName = row['Repository']
        print("Working in " + repoName + "...")
        repo_path = reposPath + repoName
        #repo_path = "C:/Users/ahmed/Documents/GitHub/Thesis/androidannotations"
        print('\tGenerating message lengths...')
        author_message_lengths = get_commit_message_lengths(repo_path, row['AVL'])
        authorList = []
        emailList = []
        msgsList = list(author_message_lengths.values())
        for author_email in author_message_lengths.keys():
            authorList.append(author_email.split(";;;")[0])
            emailList.append(author_email.split(";;;")[1])
        duplicates = {}
        size = len(authorList)
        print('\tEliminating duplicates...')
        for k in range(len(authorList)):
            if (k == size - 1):
                break
            for l in reversed(range(k + 1, len(authorList))):

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
                    msgsList[k] = msgsList[k] + msgsList[l]
                    authorList.pop(l)
                    msgsList.pop(l)
                    emailList.pop(l)
                    size -= 1



        commitsFile = open(targetPath + repoName + '/commits.txt', "r", encoding='utf-8', errors='ignore')
        lines = commitsFile.readlines()
        newAuthorsList = []
        newMsgsList = []

        for line in lines:
            author = line.split('\t')[1].strip()
            if author in authorList:
                newAuthorsList.append(author)
                newMsgsList.append(msgsList[authorList.index(author)])
            else:
                for authorItem in duplicates.keys():
                    if author in duplicates[authorItem]:
                        newAuthorsList.append(author)
                        newMsgsList.append(msgsList[authorList.index(authorItem)])
                        break
        msgsFile = open(targetPath + repoName + '/commitMsgs.txt', "w", encoding='utf-8', errors='ignore')
        i = 0
        for line in lines:
            author = line.split('\t')[1].strip()
            if author not in newAuthorsList:
                msgsFile.write('\n')
            else:
                msgsFile.write(str(newMsgsList[i]) + '\n')
                i += 1

        msgsFile.close()


     #   for author, length in author_message_lengths.items():
    #        print(f"{author}: {length} characters in commit messages")
