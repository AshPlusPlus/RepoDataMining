import subprocess
import os
import multiprocessing


def extract_developer_info(repo_path, file, until_date):
    cmd = f'git blame --line-porcelain --until="{until_date}" "{file}"'

    try:
        output = subprocess.check_output(cmd, cwd=repo_path, shell=True, stderr=subprocess.STDOUT,
                                         universal_newlines=True, encoding='utf-8', errors='ignore')

        if 'Kenneth' in output:
            print('here')


        current_author = None
        current_email = None

        for line in output.splitlines():
            if line.startswith("author "):
                current_author = line[len("author "):].strip()
            elif line.startswith("author-mail "):
                current_email = line[len("author-mail "):].strip()

        return current_author, current_email

    except subprocess.CalledProcessError as e:
        print("Error executing Git blame for file:", file, "-", e.output)
        return None, None


def main(repo_path, until_date):
    cmd = f'git ls-files'

    try:
        files = subprocess.check_output(cmd, cwd=repo_path, shell=True, stderr=subprocess.STDOUT,
                                        universal_newlines=True, encoding='utf-8', errors='ignore')
        files = files.splitlines()

        developer_info = {}  # Dictionary to store developer information

        # Create a pool of worker processes
        with multiprocessing.Pool() as pool:
            # Use pool.starmap to parallelize execution of extract_developer_info
            results = pool.starmap(extract_developer_info, [(repo_path, file, until_date) for file in files])

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
    repo_path = "C:/Users/ahmed/Documents/GitHub/Thesis/flask"  # Change this to your Git repo path
    until_date = "2016-09-25"  # Specify the date until which you want blame information

    developer_info = main(repo_path, until_date)

    if developer_info:
        for developer, info in developer_info.items():
            num_files_blamed = info[0]
            email = info[1]
            print(f"{developer} contributed to {num_files_blamed} files, Email: {email}")
    else:
        print("No blame information found.")

# import subprocess
# import os
#
# def get_blame_info(repo_path):
#     cmd = 'git ls-files'
#     try:
#         files = subprocess.check_output(cmd, cwd=repo_path, shell=True, stderr=subprocess.STDOUT, universal_newlines=True, encoding='utf-8')
#         files = files.splitlines()
#         blame_info = []
#
#         for file in files:
#             cmd = f'git blame --line-porcelain "{file}"'
#             try:
#                 output = subprocess.check_output(cmd, cwd=repo_path, shell=True, stderr=subprocess.STDOUT, universal_newlines=True, encoding='latin-1')
#                 blame_info.append(output)
#             except subprocess.CalledProcessError as e:
#                 print("Error executing Git command:", e.output)
#
#         return blame_info
#     except subprocess.CalledProcessError as e:
#         print("Error executing Git command:", e.output)
#         return []
#
# def count_contributed_files(blame_info):
#     developer_files = {}
#
#     for info in blame_info:
#         current_file = None
#
#         for line in info.splitlines():
#             if line.startswith("filename "):
#                 current_file = line[len("filename "):].strip()
#             elif line.startswith("author "):
#                 developer_name = line[len("author "):].strip().split('<')[0].strip()
#                 if developer_name not in developer_files:
#                     developer_files[developer_name] = set()
#                 developer_files[developer_name].add(current_file)
#
#     return developer_files
#
# if __name__ == "__main__":
#     repo_path = "C:/Users/ahmed/Documents/GitHub/Thesis/androidannotations"  # Change this to your Git repo path
#
#     blame_info = get_blame_info(repo_path)
#
#     if blame_info:
#         developer_files_contributed = count_contributed_files(blame_info)
#         total_files_contributed = set()
#
#         for files in developer_files_contributed.values():
#             total_files_contributed.update(files)
#
#         total_files_in_repo = len(total_files_contributed)
#
#         print(f"Total number of files in the repository: {total_files_in_repo}")
#     else:
#         print("No blame information found.")
