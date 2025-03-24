import csv
import os
import subprocess
from uuid import uuid4

# CSV File path
csv_file = 'github_top_1000.csv'

# Directories
repo_dir = 'cloned_repos'
analysis_dir = 'analysis_results'

if not os.path.exists(repo_dir):
    os.makedirs(repo_dir)

if not os.path.exists(analysis_dir):
    os.makedirs(analysis_dir)

# Path to CK jar file
ck_jar = '../ck/target/ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar'

# Read CSV and process each repository
with open(csv_file, 'r') as file:
    reader = list(csv.DictReader(file))  # Convert to list for indexing
    total_repos = len(reader)            # Total number of repositories
    for index, row in enumerate(reader, start=1):
        repo_name = row['full_name']
        repo_url = row['html_url']
        primary_language = row['primary_language']

        # Check if analysis has already been performed
        analysis_output_path = os.path.join(analysis_dir, repo_name)
        if os.path.exists(analysis_output_path) and os.listdir(analysis_output_path):
            print(f"Analysis already performed for {repo_name}. Skipping...")
            continue  # Skip to the next repository

        # Print current item number and remaining items
        remaining = total_repos - index
        print(f"Processing item {index} of {total_repos}. Remaining: {remaining}")

        # Clone repository
        print(f"Cloning {repo_name}...")
        repo_path = os.path.join(repo_dir, repo_name)
        clone_result = subprocess.run(['git', 'clone', repo_url, repo_path], capture_output=True, text=True)
        if clone_result.returncode != 0:
            print(f"Error cloning {repo_name}: {clone_result.stderr}")
            continue  # Skip to the next repository

        # Perform Static Code Analysis with CK tool
        if primary_language == 'Java':
            print(f"Running CK tool on {repo_name}...")
            if not os.path.exists(analysis_output_path):
                os.makedirs(analysis_output_path)
            ck_result = subprocess.run([
                'java', '-jar', ck_jar,
                repo_path,
                'true',  # use jars
                '0',     # max files per partition
                'true',  # variables and fields metrics
                analysis_output_path
            ], capture_output=True, text=True)
            if ck_result.returncode != 0:
                print(f"Error running CK tool on {repo_name}: {ck_result.stderr}")
                continue  # Skip to the next repository

        # Delete repository after analysis using safer approach
        print(f"Deleting {repo_name}...")
        try:
            temp_name = str(uuid4())
            os.rename(repo_path, temp_name)  # Rename the directory to avoid immediate access issues
            os.rmdir(temp_name)             # Remove the directory
        except Exception as e:
            print(f"Error deleting {repo_name}: {e}")

print("Process completed.")
