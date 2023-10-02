import subprocess
import os

def get_blame_info(repo_path):
    cmd = 'git ls-files'
    try:
        files = subprocess.check_output(cmd, cwd=repo_path, shell=True, stderr=subprocess.STDOUT, universal_newlines=True, encoding='utf-8')
        files = files.splitlines()
        blame_info = []

        for file in files:
            cmd = f'git blame --line-porcelain "{file}"'
            try:
                output = subprocess.check_output(cmd, cwd=repo_path, shell=True, stderr=subprocess.STDOUT, universal_newlines=True, encoding='latin-1')
                blame_info.append(output)
            except subprocess.CalledProcessError as e:
                print("Error executing Git command:", e.output)

        return blame_info
    except subprocess.CalledProcessError as e:
        print("Error executing Git command:", e.output)
        return []

def count_blamed_files(blame_info):
    developer_files = {}

    for info in blame_info:
        current_file = None

        for line in info.splitlines():
            if line.startswith("filename "):
                current_file = line[len("filename "):].strip()
            elif line.startswith("author "):
                developer_name = line[len("author "):].strip().split('<')[0].strip()
                if developer_name not in developer_files:
                    developer_files[developer_name] = set()
                developer_files[developer_name].add(current_file)

    return developer_files

if __name__ == "__main__":
    repo_path = "C:/Users/ahmed/Documents/GitHub/Thesis/androidannotations"  # Change this to your Git repo path

    blame_info = get_blame_info(repo_path)

    if blame_info:
        developer_files_blamed = count_blamed_files(blame_info)
        for developer, files in developer_files_blamed.items():
            num_files = len(files)
            print(f"{developer} is blamed for {num_files} files.")
    else:
        print("No blame information found.")
