import subprocess
import os
import pandas as pd
import re
from Levenshtein import distance
import datetime
import multiprocessing


def get_blame_info_for_file(repo_path, file, avl):
    if avl == 1:
        cmd = f'git blame --line-porcelain --until="2015-08-25" "{file}"'
    else:
        cmd = f'git blame --line-porcelain --until="2016-09-25" "{file}"'
    try:
        output = subprocess.check_output(cmd, cwd=repo_path, shell=True, stderr=subprocess.STDOUT,
                                         universal_newlines=True, encoding='utf-8', errors='ignore')
        return output
    except subprocess.CalledProcessError as e:
        print("Error executing Git command for file", file, ":", e.output)
        return None


def extract_email_from_blame_info(info):
    email = None
    for line in info.splitlines():
        if line.startswith("author-mail "):
            email = line[len("author-mail "):].strip()
            break
    return email


def get_blame_info(repo_path, avl):
    cmd = 'git ls-files'
    try:
        files = subprocess.check_output(cmd, cwd=repo_path, shell=True, stderr=subprocess.STDOUT,
                                        universal_newlines=True, encoding='utf-8', errors='ignore')
        files = files.splitlines()
        blame_info = []

        # Create a pool of worker processes
        with multiprocessing.Pool() as pool:
            # Use pool.map to parallelize execution of get_blame_info_for_file
            blame_info = pool.starmap(get_blame_info_for_file, [(repo_path, file, avl) for file in files])

        # Filter out None values (corresponding to errors in get_blame_info_for_file)
        blame_info = [info for info in blame_info if info is not None]

        return blame_info
    except subprocess.CalledProcessError as e:
        print("Error executing Git command:", e.output)
        return []


# The rest of the code remains the same

def count_contributed_files(blame_info):
    developer_files = {}

    for info in blame_info:
        current_file = None
        developers = set()

        for line in info.splitlines():
            if line.startswith("filename "):
                current_file = line[len("filename "):].strip()
            elif line.startswith("author "):
                developer_name = line[len("author "):].strip().split('<')[0].strip()
                developers.add(developer_name)

        for developer in developers:
            if developer not in developer_files:
                developer_files[developer] = set()
            developer_files[developer].add(current_file)

    return developer_files


if __name__ == "__main__":
    repo_path = "C:/Users/ahmed/Documents/GitHub/Thesis/flask"  # Change this to your Git repo path

    blame_info = get_blame_info(repo_path, 0)

    if blame_info:
        developer_email_mapping = {}

        # Extract emails from blame info
        for info in blame_info:
            email = extract_email_from_blame_info(info)
            if email:
                developer_name = None
                for line in info.splitlines():
                    if line.startswith("author "):
                        developer_name = line[len("author "):].strip().split('<')[0].strip()
                        break
                if developer_name:
                    developer_email_mapping[developer_name] = email

        developer_files_contributed = count_contributed_files(blame_info)
        for developer, files in developer_files_contributed.items():
            num_files = len(files)
            email = developer_email_mapping.get(developer, "N/A")
            print(f"{developer} contributed to {num_files} files, Email: {email}")
    else:
        print("No blame information found.")

# import subprocess
# import os
# import pandas as pd
# import re
# from Levenshtein import distance
# import datetime
# import multiprocessing
#
# def get_blame_info_for_file(repo_path, file, avl):
#     if avl == 1:
#         cmd = f'git blame --line-porcelain --until="2015-08-25" "{file}"'
#     else:
#         cmd = f'git blame --line-porcelain --until="2016-09-25" "{file}"'
#     try:
#         output = subprocess.check_output(cmd, cwd=repo_path, shell=True, stderr=subprocess.STDOUT, universal_newlines=True, encoding='utf-8', errors='ignore')
#         return output
#     except subprocess.CalledProcessError as e:
#         print("Error executing Git command for file", file, ":", e.output)
#         return None
#
# def get_blame_info(repo_path, avl):
#     cmd = 'git ls-files'
#     try:
#         files = subprocess.check_output(cmd, cwd=repo_path, shell=True, stderr=subprocess.STDOUT, universal_newlines=True, encoding='utf-8', errors='ignore')
#         files = files.splitlines()
#         blame_info = []
#
#         # Create a pool of worker processes
#         with multiprocessing.Pool() as pool:
#             # Use pool.map to parallelize execution of get_blame_info_for_file
#             blame_info = pool.starmap(get_blame_info_for_file, [(repo_path, file, avl) for file in files])
#
#         # Filter out None values (corresponding to errors in get_blame_info_for_file)
#         blame_info = [info for info in blame_info if info is not None]
#
#         return blame_info
#     except subprocess.CalledProcessError as e:
#         print("Error executing Git command:", e.output)
#         return []
#
# # The rest of the code remains the same
#
#
# def count_contributed_files(blame_info):
#     developer_files = {}
#
#     for info in blame_info:
#         current_file = None
#         developers = set()
#
#         for line in info.splitlines():
#             if line.startswith("filename "):
#                 current_file = line[len("filename "):].strip()
#             elif line.startswith("author "):
#                 developer_name = line[len("author "):].strip().split('<')[0].strip()
#                 developers.add(developer_name)
#
#         for developer in developers:
#             if developer not in developer_files:
#                 developer_files[developer] = set()
#             developer_files[developer].add(current_file)
#
#     return developer_files
#
# if __name__ == "__main__":
#     repo_path = "C:/Users/ahmed/Documents/GitHub/Thesis/flask"  # Change this to your Git repo path
#
#     blame_info = get_blame_info(repo_path, 0)
#
#     if blame_info:
#         developer_files_contributed = count_contributed_files(blame_info)
#         for developer, files in developer_files_contributed.items():
#             num_files = len(files)
#             print(f"{developer} contributed to {num_files} files.")
#     else:
#         print("No blame information found.")