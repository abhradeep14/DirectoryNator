import os
import datetime
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import deque


def print_banner():
    banner = r"""



$$$$$$$\  $$\                                 $$\                                   $$\   $$\             $$\                         
$$  __$$\ \__|                                $$ |                                  $$$\  $$ |            $$ |                        
$$ |  $$ |$$\  $$$$$$\   $$$$$$\   $$$$$$$\ $$$$$$\    $$$$$$\   $$$$$$\  $$\   $$\ $$$$\ $$ | $$$$$$\  $$$$$$\    $$$$$$\   $$$$$$\  
$$ |  $$ |$$ |$$  __$$\ $$  __$$\ $$  _____|\_$$  _|  $$  __$$\ $$  __$$\ $$ |  $$ |$$ $$\$$ | \____$$\ \_$$  _|  $$  __$$\ $$  __$$\ 
$$ |  $$ |$$ |$$ |  \__|$$$$$$$$ |$$ /        $$ |    $$ /  $$ |$$ |  \__|$$ |  $$ |$$ \$$$$ | $$$$$$$ |  $$ |    $$ /  $$ |$$ |  \__|
$$ |  $$ |$$ |$$ |      $$   ____|$$ |        $$ |$$\ $$ |  $$ |$$ |      $$ |  $$ |$$ |\$$$ |$$  __$$ |  $$ |$$\ $$ |  $$ |$$ |      
$$$$$$$  |$$ |$$ |      \$$$$$$$\ \$$$$$$$\   \$$$$  |\$$$$$$  |$$ |      \$$$$$$$ |$$ | \$$ |\$$$$$$$ |  \$$$$  |\$$$$$$  |$$ |      
\_______/ \__|\__|       \_______| \_______|   \____/  \______/ \__|       \____$$ |\__|  \__| \_______|   \____/  \______/ \__|      
                                                                          $$\   $$ |                                                  
                                                                          \$$$$$$  |                                                  
                                                                           \______/
                                                                           
                                                                                                                                                                                                                                                                                  
                                                         by Abhradeep Basak    
    """
    print(banner)


def count_total_items(root_dir):
    total_folders, total_files = 0, 0
    for _, dirnames, filenames in os.walk(root_dir):
        total_folders += len(dirnames)
        total_files += len(filenames)
    return total_folders, total_files


def traverse_directory(dirpath):
    folder_paths = []
    file_paths = []
    try:
        for entry in os.scandir(dirpath):
            if entry.is_dir(follow_symlinks=False):
                folder_paths.append(entry.path)
            elif entry.is_file(follow_symlinks=False):
                file_paths.append(entry.path)
    except PermissionError:
        pass
    return folder_paths, file_paths


def write_report(file_path, folder_files_map):
    """Writes the folder and file hierarchy to the report file."""
    try:
        with open(file_path, "w", encoding="latin-1", errors="replace") as report_file:
            for folder, files in folder_files_map.items():
                report_file.write(f"{folder}:\n")
                for file in files:
                    report_file.write(f"    {file}\n")
                report_file.write("\n")
    except Exception as e:
        print(f"Error writing report: {e}")


def generate_directory_report_multithread(thread_count):
    """Generates a file with a timestamped name containing a list of all folders and files in the entire file system using multithreading."""

    root_dir = os.path.abspath(os.sep)
    current_dir = os.getcwd()
    directorynator_folder = os.path.join(current_dir, "directorynator")
    if not os.path.exists(directorynator_folder):
        os.makedirs(directorynator_folder)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"directorynator_multithread_{timestamp}.txt"
    file_path = os.path.join(directorynator_folder, file_name)

    start_time = time.time()
    folder_count, file_count = 0, 0

    # Count total number of folders and files
    total_folders, total_files = count_total_items(root_dir)

    folder_paths = [root_dir]
    folder_files_map = {}

    try:
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = {executor.submit(
                traverse_directory, path): path for path in folder_paths}

            while futures:
                done, _ = as_completed(futures), futures
                for future in done:
                    try:
                        result_folders, result_files = future.result()
                        if folder_paths[-1] not in folder_files_map:
                            folder_files_map[folder_paths[-1]] = []
                        folder_files_map[folder_paths[-1]].extend(result_files)
                        for folder in result_folders:
                            folder_files_map[folder] = []
                        folder_paths.extend(result_folders)
                        folder_count += len(result_folders)
                        file_count += len(result_files)

                        # Submit new tasks for subfolders
                        futures.update(
                            {executor.submit(traverse_directory, path): path for path in result_folders})
                    except Exception as e:
                        print(f"Error processing future result: {e}")
                    finally:
                        del futures[future]

        elapsed_time = time.time() - start_time
        summary = (
            f"Total number of folders: {folder_count}\n"
            f"Total number of files: {file_count}\n"
            f"Time taken: {elapsed_time:.2f} seconds\n"
        )

        # Write the report with hierarchical structure
        write_report(file_path, folder_files_map)

        print(f"\nSummary:\n{summary}")
        print(f"Directory report saved to: {file_path} successfully!")
    except Exception as e:
        print(f"Error creating report: {e}")


def bfs_traverse_directory(root_dir):
    """Uses BFS to traverse the directory structure."""
    current_dir = os.getcwd()
    directorynator_folder = os.path.join(current_dir, "directorynator")
    if not os.path.exists(directorynator_folder):
        os.makedirs(directorynator_folder)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"directorynator_bfs_{timestamp}.txt"
    file_path = os.path.join(directorynator_folder, file_name)

    folder_files_map = {}
    queue = deque([root_dir])
    folder_count, file_count = 0, 0

    start_time = time.time()

    try:
        while queue:
            current_path = queue.popleft()
            try:
                folder_files_map[current_path] = []
                for entry in os.scandir(current_path):
                    if entry.is_dir(follow_symlinks=False):
                        queue.append(entry.path)
                        folder_files_map[entry.path] = []
                        folder_count += 1
                    elif entry.is_file(follow_symlinks=False):
                        folder_files_map[current_path].append(entry.path)
                        file_count += 1
            except PermissionError:
                pass

        elapsed_time = time.time() - start_time
        summary = (
            f"Total number of folders: {folder_count}\n"
            f"Total number of files: {file_count}\n"
            f"Time taken: {elapsed_time:.2f} seconds\n"
        )

        # Write the report with hierarchical structure
        write_report(file_path, folder_files_map)

        print(f"\nSummary:\n{summary}")
        print(f"BFS directory report saved to: {file_path} successfully!")
    except Exception as e:
        print(f"Error creating BFS report: {e}")


def dfs_traverse_directory(root_dir):
    """Uses DFS to traverse the directory structure."""
    current_dir = os.getcwd()
    directorynator_folder = os.path.join(current_dir, "directorynator")
    if not os.path.exists(directorynator_folder):
        os.makedirs(directorynator_folder)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"directorynator_dfs_{timestamp}.txt"
    file_path = os.path.join(directorynator_folder, file_name)

    folder_files_map = {}
    stack = [root_dir]
    folder_count, file_count = 0, 0

    start_time = time.time()

    try:
        while stack:
            current_path = stack.pop()
            try:
                folder_files_map[current_path] = []
                for entry in os.scandir(current_path):
                    if entry.is_dir(follow_symlinks=False):
                        stack.append(entry.path)
                        folder_files_map[entry.path] = []
                        folder_count += 1
                    elif entry.is_file(follow_symlinks=False):
                        folder_files_map[current_path].append(entry.path)
                        file_count += 1
            except PermissionError:
                pass

        elapsed_time = time.time() - start_time
        summary = (
            f"Total number of folders: {folder_count}\n"
            f"Total number of files: {file_count}\n"
            f"Time taken: {elapsed_time:.2f} seconds\n"
        )

        # Write the report with hierarchical structure
        write_report(file_path, folder_files_map)

        print(f"\nSummary:\n{summary}")
        print(f"DFS directory report saved to: {file_path} successfully!")
    except Exception as e:
        print(f"Error creating DFS report: {e}")


def trie_traverse_directory(root_dir):
    """Uses Trie to traverse the directory structure."""
    current_dir = os.getcwd()
    directorynator_folder = os.path.join(current_dir, "directorynator")
    if not os.path.exists(directorynator_folder):
        os.makedirs(directorynator_folder)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"directorynator_trie_{timestamp}.txt"
    file_path = os.path.join(directorynator_folder, file_name)

    folder_files_map = {}
    trie = {}
    stack = [(root_dir, trie)]
    folder_count, file_count = 0, 0

    start_time = time.time()

    try:
        while stack:
            current_path, current_trie = stack.pop()
            try:
                current_trie['folders'] = {}
                current_trie['files'] = []
                for entry in os.scandir(current_path):
                    if entry.is_dir(follow_symlinks=False):
                        folder_name = os.path.basename(entry.path)
                        current_trie['folders'][folder_name] = {}
                        stack.append(
                            (entry.path, current_trie['folders'][folder_name]))
                        folder_count += 1
                    elif entry.is_file(follow_symlinks=False):
                        current_trie['files'].append(entry.path)
                        file_count += 1
            except PermissionError:
                pass

        
        def flatten_trie(trie, path):
            folder_files_map[path] = trie['files']
            for folder, subtrie in trie['folders'].items():
                flatten_trie(subtrie, os.path.join(path, folder))

        flatten_trie(trie, root_dir)

        elapsed_time = time.time() - start_time
        summary = (
            f"Total number of folders: {folder_count}\n"
            f"Total number of files: {file_count}\n"
            f"Time taken: {elapsed_time:.2f} seconds\n"
        )

        # Write the report with hierarchical structure
        write_report(file_path, folder_files_map)

        print(f"\nSummary:\n{summary}")
        print(f"Trie directory report saved to: {file_path} successfully!")
    except Exception as e:
        print(f"Error creating Trie report: {e}")


def cli_interface():
    """CLI interface to navigate between options."""
    print_banner()
    while True:
        print("\nWelcome to DirectoryNator!")
        print("Select an option:")
        print("1) Multi-Thread Option")
        print("2) Algorithmic Options (Trie, BFS, DFS)")
        print("3) Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            thread_count = int(input("Enter the number of threads to use: "))
            generate_directory_report_multithread(thread_count)
        elif choice == "2":
            print("Select an Algorithm:")
            print("1) Trie Traversal")
            print("2) BFS Traversal")
            print("3) DFS Traversal")
            algo_choice = input("Enter your choice: ")

            if algo_choice == "1":
                trie_traverse_directory(os.path.abspath(os.sep))
            elif algo_choice == "2":
                bfs_traverse_directory(os.path.abspath(os.sep))
            elif algo_choice == "3":
                dfs_traverse_directory(os.path.abspath(os.sep))
            else:
                print("Invalid choice, please try again.")
        elif choice == "3":
            print("Exiting DirectoryNator. Goodbye!")
            break
        else:
            print("Invalid choice, please try again.")


if __name__ == "__main__":
    cli_interface()
