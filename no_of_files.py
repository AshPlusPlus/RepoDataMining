import git
import os
from collections import defaultdict


def count_files_by_developer(repo_path):
    # Initialize a dictionary to store file counts by developer
    developer_file_counts = defaultdict(int)

    # Open the Git repository
    repo = git.Repo(repo_path)

    # Iterate through all commits in the repository
    for commit in repo.iter_commits():
        author_name = commit.author.name

        # Get the list of changed files in this commit
        changed_files = commit.stats.files.keys()

        # Increment the count for each changed file by the author
        for file in changed_files:
            developer_file_counts[(author_name, file)] += 1

    # Sum up the counts for each developer
    developer_counts = defaultdict(int)
    for (author, _), count in developer_file_counts.items():
        developer_counts[author] += count

    return developer_counts


if __name__ == "__main__":
    repo_address = input("Enter the Git repository path: ")

    if os.path.exists(repo_address):
        developer_counts = count_files_by_developer(repo_address)

        print("Number of files created/modified by each developer:")
        for developer, count in developer_counts.items():
            print(f"{developer}: {count} files")
    else:
        print("Invalid repository path.")