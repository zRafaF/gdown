import os
import subprocess
from tqdm import tqdm


def run_gallery_dl_with_progress(url, auth_args=None):
    """
    Runs gallery-dl with progress bar updates by parsing its stdout.
    Optionally includes authentication arguments.
    """
    # Specify the download directory
    download_dir = "./downloads"

    # Ensure the directory exists
    os.makedirs(download_dir, exist_ok=True)

    # Build the command
    command = [
        "gallery-dl",
        "--verbose",
        "--download-archive",
        "downloaded.txt",
        "-d",
        download_dir,
    ]

    if auth_args:
        command.extend(auth_args)

    command.append(url)

    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        with tqdm(
            desc=f"Downloading: {url}", unit="B", unit_scale=True, unit_divisor=1024
        ) as pbar:
            for line in iter(process.stdout.readline, ""):
                line = line.strip()
                print(line)  # Print gallery-dl output for debugging

                # Try to parse progress
                if "%" in line:
                    try:
                        percentage = float(line.split("%")[0].strip())
                        pbar.n = int(percentage * pbar.total / 100) if pbar.total else 0
                        pbar.refresh()
                    except ValueError:
                        pass  # Skip lines that don't conform to expected format

            # Process stderr for debugging
            for err_line in process.stderr:
                print(f"ERROR: {err_line.strip()}")

            process.wait()
            if process.returncode != 0:
                raise subprocess.CalledProcessError(
                    process.returncode, command, output="Error during download."
                )
    except FileNotFoundError:
        print("Error: gallery-dl is not installed or not in PATH.")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
    finally:
        pbar.close()


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


def update():
    command = ["gallery-dl", "-U", "--update-check"]
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        for line in process.stdout:
            print(line.strip())

        for err_line in process.stderr:
            print(f"ERROR: {err_line.strip()}")

        process.wait()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(
                process.returncode, command, output="Error during update."
            )
    except FileNotFoundError:
        print("Error: gallery-dl is not installed or not in PATH.")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
    finally:
        print("Update complete.")


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
        print("3. Update")
        print("4. Help")
        print("5. Exit")

        choice = input("Choose an option (1-5): ")
        if choice == "1":
            download_single()
        elif choice == "2":
            bulk_download()
        elif choice == "3":
            update()
        elif choice == "4":
            show_help()
        elif choice == "5":
            print("Exiting the program.")
            break
        else:
            print("Invalid option. Please choose a number between 1 and 5.")


if __name__ == "__main__":
    main()
