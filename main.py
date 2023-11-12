
import os
from datetime import datetime
import numpy
import pandas as pd
import re
import xlrd
import openpyxl
from Levenshtein import distance

def select_dir(repoName, repoPath, targetPath, row):
    dir = repoPath + repoName
    targetdir = repoPath + 'XXrepostatsXX/' + repoName
    os.chdir(dir)
    if not os.path.exists(targetdir):
        os.makedirs(targetdir)
    if (row['AVL'] == 1):
        os.system('git shortlog --until="2015-08-25" -sne --all --format="%aN <%aE>" --no-merges > ' + targetdir + '/commits.txt')
    else:
        os.system('git shortlog --until="2016-09-25" -sne --all --format="%aN <%aE>" --no-merges > ' + targetdir + '/commits.txt')
    commitsFile = targetdir + '/commits.txt'
    data = open(commitsFile, 'r', encoding='utf-8', errors='ignore')
    return data

def format_date(line):
    line.strip()
    elements = line.split()
    if (len(elements) > 4):
        return (elements[2].strip() + ' ' + elements[1].strip() + ' ' + elements[4].strip())
    else:
        return "Empty"

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


if __name__ == '__main__':
    df = pd.read_excel('C:/Users/ahmed/Desktop/Thesis Prog/dataset.xlsx')
    df = df.reset_index()

    repoPath = 'C:/Users/ahmed/Documents/GitHub/Thesis/'
    targetPath = repoPath + 'XXrepostatsXX/'



    emptyAuthorsFile = open('C:/Users/ahmed/Desktop/Thesis Prog/emptyAuthors.txt', 'w', encoding='utf-8')
    for index, row in df.iterrows():
        repoName = row['Repository']
        print("Working in " + repoName + "...")
        emptyAuthorsFile.write(repoName + " repo:\n")
        editCommandStart = 'git --no-pager log --all --until="2016-09-25" --author="'
        if (row['AVL'] == 1):
            editCommandStart = 'git --no-pager log --all --until="2015-08-25" --author="'


        editCommandEnd = '" --format=tformat: --numstat | q -t "select sum(1), sum(2) from -"'
        editCommandfile = targetPath + repoName + '/aads.txt'

        fdateCommandStart = 'git log --all --reverse --format=%cd --author="'
        fdateCommandEnd = '" | q -t "select * from - limit 1"'
        #fdateCommandfile = targetPath + repoName + '/firstCommit.txt'

        ldateCommandStart = 'git log --all -1 --format=%cd --until="2016-09-25" --author="'
        if (row['AVL'] == 1):
            ldateCommandStart = 'git log --all -1 --format=%cd --until="2015-08-25" --author="'

        ldateCommandEnd = '"'
      #  ldateCommandfile = targetPath + repoName + '/lastCommit.txt'

        data = select_dir(repoName, repoPath, targetPath, row)
        lines = data.readlines()
        data.close()
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

            for l in reversed(range(k+1, len(authorList))):

                string1 = authorList[k].replace(' ', '').lower()
                string2 = authorList[l].replace(' ', '').lower()
                initials_match = mapInitials(string1, string2)


                string1 = re.sub("[\(\[].*?[\)\]]", "", string1)
                string2 = re.sub("[\(\[].*?[\)\]]", "", string2)
                email_initials_match = False
                email1 = emailList[k]#.split('@')[0]
                email2 = emailList[l]#.split('@')[0]
             #   email_initials_match = mapInitials(email1, email2)


                if ((distance(string1, string2) < 2 and len(string1) > 3 and len(string2) > 3) or
                        (string1 == string2) or
                        (email1 == email2) or
                        initials_match or
                        email_initials_match):
                    print('Duplicates: ' + string1 + ' at ' + str(k) + ' - ' + string2 + ' at ' + str(l))
                    if duplicates.get(authorList[k]) is not None:
                        duplicates.get(authorList[k]).append(authorList[l])
                    else:
                        duplicates[authorList[k]] = [authorList[l]]
                    commitList[k] = commitList[k] + commitList[l]
                    authorList.pop(l)
                    commitList.pop(l)
                    emailList.pop(l)
                    size-=1
        #        string1 = authorList[k].replace(' ', '').lower()
         #       string2 = authorList[l].replace(' ', '').lower()
              #  elif string1 in string2 or string2 in string1:
               #     authorList.pop(l)
                #    commitList.pop(l)
                #    size-=1
        x = numpy.quantile(commitList, [0.85])
        i = 0
        j = 0

        data = open(targetPath + repoName + '/commits.txt', 'w', encoding='utf-8')


        for i in range(len(authorList)):
            if commitList[i] >= x[0]:
                if (i > 0):
                    data.write('\n')
                data.write(str(commitList[i]) + '\t' + authorList[i])#+ '\t' + emailList[i])

        print("\t- Committers have been reduced.")
        data.close()
        data = open(targetPath + repoName + '/commits.txt', 'r', encoding='utf-8')
        lines = data.readlines()
        data.close()

        aadsFile = open(targetPath + repoName + '/aads.txt', 'w', encoding='utf-8')
        firstDateFile = open(targetPath + repoName + '/daysBetweenFirstLast.txt', 'w', encoding='utf-8')
        lastDateFile = open(targetPath + repoName + '/daysSinceLast.txt', 'w', encoding='utf-8')
        if (row['AVL'] == 0):
            FINAL_DATE = datetime(2016, 9, 25)
        else:
            FINAL_DATE = datetime(2015, 8, 25)


        print("\t- Getting line edits and dates.")
        for line in lines:
            line.strip()
            commits = line.split('\t')[0]
            commits = commits.strip()
            if int(commits) < x[0]:
                continue
            author = line.split('\t')[1].strip()
            author = author.strip()
            author = author.replace('"', '\\"')
            listOfUsernames = [author]
            if duplicates.get(author) is not None:
                listOfUsernames.extend(duplicates.get(author))
            adds_per_author = 0
            dels_per_author = 0
            username_first_date = 0
            username_last_date = 0

            for authorUsername in listOfUsernames:

                editCommand = editCommandStart + authorUsername + editCommandEnd #+ editCommandfile
                fdateCommand = fdateCommandStart + authorUsername + fdateCommandEnd
                ldateCommand = ldateCommandStart + authorUsername + ldateCommandEnd

                edits_per_username = os.popen(editCommand).read().strip()
                edits_per_username = edits_per_username.strip()
                addsdels_per_username = edits_per_username.split('\t')

                if len(addsdels_per_username) == 2:
                    adds_per_author += int(addsdels_per_username[0].strip())
                    dels_per_author += int(addsdels_per_username[1].strip())


                    #os.system(editCommand)

                first_format_output = format_date(os.popen(fdateCommand).read().strip())
                last_format_output = format_date(os.popen(ldateCommand).read().strip())
                if last_format_output == "Empty":
                    emptyAuthorsFile.write('\t' + authorUsername + '\n')
                    print("Empty Author: " + authorUsername)
               #     firstDateFile.write('\n')
                #    lastDateFile.write('\n')
                elif last_format_output != "Empty" and first_format_output == "Empty":
                    firstDateFile.write('\n')
                    LAST_DATE = datetime.strptime(last_format_output, '%d %b %Y')
                    if username_last_date == 0:
                        username_last_date = LAST_DATE
                    elif LAST_DATE > username_last_date:
                        username_last_date = LAST_DATE


                 #   lastDateFile.write(str((FINAL_DATE - LAST_DATE).days) + '\n')
                else:
                    FIRST_DATE = datetime.strptime(format_date(os.popen(fdateCommand).read().strip()), '%d %b %Y')
                    LAST_DATE = datetime.strptime(format_date(os.popen(ldateCommand).read().strip()), '%d %b %Y')
                    if username_last_date == 0:
                        username_first_date = FIRST_DATE
                        username_last_date = LAST_DATE
                    else:
                        if LAST_DATE > username_last_date:
                            username_last_date = LAST_DATE
                        if FIRST_DATE < username_first_date:
                            username_first_date = FIRST_DATE

                 #   firstDateFile.write(str((LAST_DATE - FIRST_DATE).days) + '\n')
                  #  lastDateFile.write(str((FINAL_DATE - LAST_DATE).days) + '\n')

            if (adds_per_author == 0 and dels_per_author == 0):
                aadsFile.write('\n')
            else:
                aadsFile.write(str(adds_per_author) + '\t' + str(dels_per_author) + '\n')
            if username_last_date == 0:
                lastDateFile.write('\n')
                firstDateFile.write('\n')
            else:
                lastDateFile.write(str((FINAL_DATE - username_last_date).days) + '\n')
                if username_first_date == 0:
                    firstDateFile.write('\n')
                else:
                    firstDateFile.write(str((username_last_date - username_first_date).days) + '\n')
        aadsFile.close()
        firstDateFile.close()
        lastDateFile.close()

'''
        aadsFile = open(targetPath + repoName + '/aads.txt', 'r', encoding='utf-8')
        firstDateFile = open(targetPath + repoName + '/daysBetweenFirstLast.txt', 'r', encoding='utf-8')
        lastDateFile = open(targetPath + repoName + '/daysSinceLast.txt', 'r', encoding='utf-8')
        lines1 = aadsFile.readlines()[:-1]
        lines2 = firstDateFile.readlines()[:-1]
        lines3 = lastDateFile.readlines()[:-1]
        aadsFile = open(targetPath + repoName + '/aads.txt', 'w', encoding='utf-8')
        firstDateFile = open(targetPath + repoName + '/daysBetweenFirstLast.txt', 'w', encoding='utf-8')
        lastDateFile = open(targetPath + repoName + '/daysSinceLast.txt', 'w', encoding='utf-8')
        aadsFile.writelines(lines1)
        firstDateFile.writelines(lines2)
        lastDateFile.writelines(lines3)

'''