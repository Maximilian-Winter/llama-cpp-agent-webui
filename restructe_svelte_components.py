import os
import shutil


def restructure_svelte_files(directory):
    # Walk through the directory
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.svelte'):
                file_path = os.path.join(root, file)
                file_name = os.path.splitext(file)[0]

                # Create new folder
                new_folder = os.path.join(root, file_name.replace('_', '-'))
                os.makedirs(new_folder, exist_ok=True)

                # New file path
                new_file_path = os.path.join(new_folder, '+page.svelte')

                # Move and rename the file
                shutil.move(file_path, new_file_path)

                print(f"Moved {file} to {new_file_path}")


# Usage
directory = 'src/components'
restructure_svelte_files(directory)
