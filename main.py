
import os
from datetime import datetime
import numpy
import pandas as pd
import re
import xlrd
import openpyxl
from Levenshtein import distance

def select_dir(repoName, repoPath, targetPath, row, cc):
    dir = repoPath + repoName
    targetdir = repoPath + 'XXrepostatsXX/' + repoName
    os.chdir(dir)
    if not os.path.exists(targetdir):
        os.makedirs(targetdir)
    if (row['AVL'] == 1 or cc == 1):
        os.system('git shortlog --until="2015-08-25" -sne --all --format="%aN <%aE>" > ' + targetdir + '/commits.txt')
    else:
        os.system('git shortlog --until="2016-09-25" -sne --all --format="%aN <%aE>" > ' + targetdir + '/commits.txt')
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

if __name__ == '__main__':
    df = pd.read_excel('C:/Users/ahmed/Desktop/Thesis Prog/dataset.xlsx')
    df = df.reset_index()

    repoPath = 'C:/Users/ahmed/Documents/GitHub/Thesis/'
    targetPath = repoPath + 'XXrepostatsXX/'






    cc = 0

    emptyAuthorsFile = open('C:/Users/ahmed/Desktop/Thesis Prog/emptyAuthors.txt', 'w', encoding='utf-8')
    for index, row in df.iterrows():
        print(row['AVL'] )
        repoName = row['Repository']
        if cc > 0:
            break
      #  cc+=2
     #   repoName = "symfony"
       # if repoName[0] < 'i' or repoName == "salt" or repoName == "symfony":
       #     continue


        print("Working in " + repoName + "...")
        emptyAuthorsFile.write(repoName + " repo:\n")
        editCommandStart = 'git --no-pager log --until="2016-09-25" --author="'
        if (row['AVL'] == 1 or cc == 1):
            editCommandStart = 'git --no-pager log --until="2015-08-25" --author="'


        editCommandEnd = '" --format=tformat: --numstat | q -t "select sum(1), sum(2) from -"'
        editCommandfile = targetPath + repoName + '/aads.txt'

        fdateCommandStart = 'git log --reverse --format=%cd --author="'
        fdateCommandEnd = '" | q -t "select * from - limit 1"'
        #fdateCommandfile = targetPath + repoName + '/firstCommit.txt'

        ldateCommandStart = 'git log -1 --format=%cd --until="2016-09-25" --author="'
        if (row['AVL'] == 1 or cc==1):
            ldateCommandStart = 'git log -1 --format=%cd --until="2015-08-25" --author="'

        ldateCommandEnd = '"'
      #  ldateCommandfile = targetPath + repoName + '/lastCommit.txt'

        data = select_dir(repoName, repoPath, targetPath, row, cc)
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
                string1 = re.sub("[\(\[].*?[\)\]]", "", string1)
                string2 = re.sub("[\(\[].*?[\)\]]", "", string2)

                if ((distance(string1, string2) < 2 and len(string2) > 3 and len(string2) > 3) or
                        (emailList[k] == emailList[l])):
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
        v = len(authorList)
        vv = len(emailList)

        for i in range(len(authorList)):
            if commitList[i] >= x[0]:
                if (i > 0):
                    data.write('\n')
                data.write(str(commitList[i]) + '\t' + authorList[i])#+ '\t' + emailList[i])

        print("\t- Committers have been reduced.")
'''
        data = open(targetPath + repoName + '/commits.txt', 'r', encoding='utf-8')
        lines = data.readlines()

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
            authorMail = line.split('\t')[1].strip()
            if (len(authorMail) < 2):
                print(authorMail)
            author = line.split('\t')[1].strip()
           # email = line.split('\t')[2].strip()
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
'''
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