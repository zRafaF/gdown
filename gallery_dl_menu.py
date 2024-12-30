import os
import subprocess
from tqdm import tqdm


def run_gallery_dl_with_progress(url, auth_args=None):
    """
    Runs gallery-dl with progress bar updates by parsing its stdout.
    Optionally includes authentication arguments.
    """
    command = ["gallery-dl", "--download-archive", "downloaded.txt"]

    if auth_args:
        command.extend(auth_args)

    command.append(url)

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    with tqdm(
        desc=f"Downloading: {url}", unit="B", unit_scale=True, unit_divisor=1024
    ) as pbar:
        for line in process.stdout:
            if "%" in line:  # Try to parse progress info
                try:
                    percentage = float(line.split("%")[0].strip())
                    pbar.n = int(percentage * pbar.total / 100) if pbar.total else 0
                    pbar.refresh()
                except ValueError:
                    pass  # Skip lines that don't conform to expected format
            print(line.strip())

        process.wait()


def get_auth_args():
    """
    Prompts the user for authentication credentials or reads them from a file.
    Returns the necessary gallery-dl authentication arguments.
    """
    print("Authentication Options:")
    print("1. Enter credentials via CLI")
    print("2. Use credentials from a text file")
    print("3. Skip authentication")

    auth_choice = input("Choose an option (1-3): ")

    if auth_choice == "1":
        username = input("Enter username: ").strip()
        password = input("Enter password: ").strip()
        return ["--username", username, "--password", password]

    elif auth_choice == "2":
        auth_file = input("Enter the path to the credentials file: ").strip()
        if os.path.exists(auth_file):
            with open(auth_file, "r") as file:
                lines = file.readlines()
                if len(lines) >= 2:
                    username = lines[0].strip()
                    password = lines[1].strip()
                    return ["--username", username, "--password", password]
                else:
                    print(
                        "Invalid file format. Ensure the file contains a username and password on separate lines."
                    )
        else:
            print("File not found. Skipping authentication.")

    return None


def download_single():
    url = input("Enter the URL to download: ")
    try:
        auth_args = get_auth_args()
        run_gallery_dl_with_progress(url, auth_args)
    except Exception as e:
        print(f"An error occurred during the download: {e}")


def bulk_download():
    urls_file = "./URLS.txt"
    if os.path.exists(urls_file):
        auth_args = get_auth_args()
        with open(urls_file, "r") as file:
            urls = [url.strip() for url in file if url.strip()]
            for url in urls:
                try:
                    run_gallery_dl_with_progress(url, auth_args)
                except Exception as e:
                    print(f"Error downloading {url}: {e}")
    else:
        print("URLS.txt file not found. Please run Setup to create it.")


def setup_urls_file():
    urls_file = "./URLS.txt"
    print("Creating or editing the URLS.txt file.")
    print("Enter URLs line by line. Press Enter on an empty line to finish.")
    with open(urls_file, "w") as file:
        while True:
            url = input("Enter a URL (or leave blank to finish): ")
            if not url.strip():
                break
            file.write(url.strip() + "\n")
    print(f"URLs saved to {urls_file}.")


def show_help():
    help_text = """
Gallery-dl Terminal Utility

Options:
1. Download Single: Enter a single URL to download.
2. Bulk Download: Load and download URLs from the URLS.txt file.
3. Setup: Create or edit the URLS.txt file.
4. Help: Show this help menu.
5. Exit: Exit the program.
"""
    print(help_text)


def main():
    while True:
        print("\nGallery-dl Menu:")
        print("1. Download Single")
        print("2. Bulk Download")
        print("3. Setup")
        print("4. Help")
        print("5. Exit")

        choice = input("Choose an option (1-5): ")
        if choice == "1":
            download_single()
        elif choice == "2":
            bulk_download()
        elif choice == "3":
            setup_urls_file()
        elif choice == "4":
            show_help()
        elif choice == "5":
            print("Exiting the program.")
            break
        else:
            print("Invalid option. Please choose a number between 1 and 5.")


if __name__ == "__main__":
    main()
