import subprocess

def get_total_file_count(repo_path):
    cmd = 'git ls-files | find /c /v ""'
    try:
        output = subprocess.check_output(cmd, cwd=repo_path, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
        return int(output.strip())
    except subprocess.CalledProcessError as e:
        print("Error executing Git command:", e.output)
        return -1

if __name__ == "__main__":
    repo_path = "C:/Users/ahmed/Documents/GitHub/Thesis/androidannotations"  # Change this to your Git repo path

    total_file_count = get_total_file_count(repo_path)

    if total_file_count != -1:
        print(f"Total number of files in the repository: {total_file_count}")
    else:
        print("Error counting files.")
