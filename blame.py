import os
import subprocess
from collections import defaultdict


def get_last_editor_for_files(repo_path):
    # Change to the repository directory
    os.chdir(repo_path)

    # Get the list of all files in the repository
    all_files = []
    for root, dirs, files in os.walk("."):
        for file in files:
            all_files.append(os.path.join(root, file))

    # Dictionary to store the last editor for each file
    last_editors = {}

    for file_path in all_files:
        try:
            # Use the 'git blame' command to find the last editor of the file
            blame_output = subprocess.check_output(["git", "blame", "--line-porcelain", file_path]).decode("utf-8")

            # Extract the author's name
            for line in blame_output.splitlines():
                if line.startswith("author "):
                    last_editor = line[len("author "):]
                    last_editors[file_path] = last_editor
                    break
        except subprocess.CalledProcessError:
            # Handle cases where 'git blame' fails, e.g., for binary files
            last_editors[file_path] = "Unable to determine"

    # Create a dictionary to store the count of files edited by each developer
    developer_file_counts = defaultdict(int)

    for file_path, last_editor in last_editors.items():
        developer_file_counts[last_editor] += 1

    return developer_file_counts


if __name__ == "__main__":
    repo_path = input("Enter the path to the Git repository: ")

    if os.path.exists(repo_path):
        developer_file_counts = get_last_editor_for_files(repo_path)

        print("Number of files edited by each developer:")
        for developer, file_count in developer_file_counts.items():
            print(f"{developer}: {file_count} files")
    else:
        print("Invalid repository path.")
