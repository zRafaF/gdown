import os
import subprocess
from tqdm import tqdm


def run_gallery_dl_with_progress(url, auth_args=None):
    """
    Runs gallery-dl with progress bar updates by parsing its output.
    Optionally includes authentication arguments.
    """
    download_dir = "./downloads"
    os.makedirs(download_dir, exist_ok=True)

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
            stderr=subprocess.STDOUT,  # Merge stderr with stdout
            text=True,
            bufsize=1,
        )

        with tqdm(
            desc=f"Downloading: {url}",
            unit="%",
            total=100,
            bar_format="{l_bar}{bar}| {n_fmt}% [{elapsed}<{remaining}]",
        ) as pbar:
            current_percent = 0
            while True:
                line = process.stdout.readline()
                if not line:
                    break

                line = line.strip()
                print(line)  # Print output for debugging

                # Parse percentage from line
                if "%" in line:
                    try:
                        # Extract percentage value from line
                        percent_str = line.split("%")[0].split()[-1]
                        new_percent = float(percent_str)
                        if new_percent > current_percent:
                            pbar.update(new_percent - current_percent)
                            current_percent = new_percent
                    except (ValueError, IndexError):
                        pass

            # Check process completion
            return_code = process.wait()
            if return_code != 0:
                raise subprocess.CalledProcessError(
                    return_code, command, output="Error during download."
                )

    except FileNotFoundError:
        print("Error: gallery-dl is not installed or not in PATH.")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")


def get_auth_args():
    """
    Prompts the user for authentication credentials or reads them from a file.
    Returns the necessary gallery-dl authentication arguments.
    """
    print("\nAuthentication Options:")
    print("1. Enter credentials via CLI")
    print("2. Use credentials from a text file")
    print("3. Skip authentication")

    while True:
        auth_choice = input("Choose an option (1-3): ").strip()
        if auth_choice in ("1", "2", "3"):
            break
        print("Invalid choice. Please enter 1, 2, or 3.")

    if auth_choice == "1":
        username = input("Enter username: ").strip()
        password = input("Enter password: ").strip()
        return ["--username", username, "--password", password]

    elif auth_choice == "2":
        while True:
            auth_file = input("Enter the path to the credentials file: ").strip()
            if os.path.exists(auth_file):
                try:
                    with open(auth_file, "r") as file:
                        lines = [
                            line.strip() for line in file.readlines() if line.strip()
                        ]
                    if len(lines) >= 2:
                        return ["--username", lines[0], "--password", lines[1]]
                    print("File must contain username and password on first two lines.")
                except Exception as e:
                    print(f"Error reading file: {e}")
            else:
                print("File not found. Try again or enter 'cancel' to abort.")
                if input("Your choice: ").lower() == "cancel":
                    break

    return None


def download_single():
    url = input("\nEnter the URL to download: ").strip()
    if not url:
        print("No URL entered.")
        return

    auth_args = get_auth_args()
    try:
        run_gallery_dl_with_progress(url, auth_args)
    except Exception as e:
        print(f"\nError during download: {e}")


def bulk_download():
    urls_file = "./URLS.txt"
    if not os.path.exists(urls_file):
        print("URLS.txt file not found. Please create it first.")
        return

    auth_args = get_auth_args()
    try:
        with open(urls_file, "r") as file:
            urls = [line.strip() for line in file if line.strip()]
    except Exception as e:
        print(f"Error reading URLs file: {e}")
        return

    for url in urls:
        print(f"\nProcessing URL: {url}")
        try:
            run_gallery_dl_with_progress(url, auth_args)
        except Exception as e:
            print(f"Failed to download {url}: {e}")
            continue


def update():
    print("\nChecking for gallery-dl updates...")
    try:
        result = subprocess.run(
            ["gallery-dl", "-U", "--update-check"],
            capture_output=True,
            text=True,
            check=True,
        )
        print(result.stdout)
        print("Update check completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Update failed with error:\n{e.stderr}")
    except FileNotFoundError:
        print("Error: gallery-dl is not installed or not in PATH.")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")


def show_help():
    help_text = """
Gallery-dl Terminal Utility

Options:
1. Download Single: Enter a single URL to download
2. Bulk Download: Download multiple URLs from URLS.txt
3. Update: Check for gallery-dl updates
4. Help: Show this help message
5. Exit: Quit the program
"""
    print(help_text)


def main():
    print("Gallery-dl Terminal Utility")
    while True:
        print("\nMain Menu:")
        print("1. Download Single")
        print("2. Bulk Download")
        print("3. Update")
        print("4. Help")
        print("5. Exit")

        choice = input("\nChoose an option (1-5): ").strip()
        if choice == "1":
            download_single()
        elif choice == "2":
            bulk_download()
        elif choice == "3":
            update()
        elif choice == "4":
            show_help()
        elif choice == "5":
            print("\nExiting the program. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")


if __name__ == "__main__":
    main()
