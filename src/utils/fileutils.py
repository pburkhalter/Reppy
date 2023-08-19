import os
import time
import shutil
import logging


def delete_old_folders(directory, max_age):
    for folder_name in os.listdir(directory):
        folder_path = os.path.join(directory, folder_name)
        if os.path.isdir(folder_path):
            folder_age = time.time() - os.path.getmtime(folder_path)
            if folder_age > max_age:
                # Check if files in folder are locked
                try:
                    os.listdir(folder_path)
                    # If files are locked, skip deletion
                    logger.warning(f"Skipping deletion of {folder_path} because files are locked")
                    continue
                except PermissionError:
                    # If files are not locked, delete folder
                    shutil.rmtree(folder_path)
                    logger.info(f"Deleted {folder_path}")


def create_folders(directories):
    for directory in directories:
        if not os.path.exists(directories[directory]):
            os.makedirs(directories[directory])
