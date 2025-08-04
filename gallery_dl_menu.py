import os
import subprocess
from tqdm import tqdm


def setup_directories():
    """Ensures the required directories and placeholder files exist."""
    # Ensure download directory exists
    os.makedirs("./downloads", exist_ok=True)

    # Ensure cookies directory and placeholder file exist
    cookies_dir = "./cookies"
    placeholder_file = os.path.join(cookies_dir, ".put_cookies_here")
    if not os.path.exists(cookies_dir):
        os.makedirs(cookies_dir)
        print(f"Created directory: {cookies_dir}")
    if not os.path.exists(placeholder_file):
        with open(placeholder_file, "w") as f:
            f.write("Place your cookie files (ending in .txt) in this directory.")


def run_gallery_dl_with_progress(url, auth_args=None):
    """
    Runs gallery-dl with a progress bar by parsing its output.
    Optionally includes authentication or cookie arguments.
    """
    download_dir = "./downloads"

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
            encoding="utf-8",
            errors="replace",
        )

        with tqdm(
            desc=f"Downloading: {url}",
            unit="%",
            total=100,
            bar_format="{l_bar}{bar}| {n_fmt}% [{elapsed}<{remaining}]",
        ) as pbar:
            current_percent = 0
            for line in iter(process.stdout.readline, ""):
                line = line.strip()
                print(line)  # Print gallery-dl output for debugging

                if "%" in line:
                    try:
                        percent_str = line.split("%")[0].split()[-1]
                        new_percent = float(percent_str)
                        if new_percent > current_percent:
                            pbar.update(new_percent - current_percent)
                            current_percent = new_percent
                    except (ValueError, IndexError):
                        pass

            if pbar.n < 100:
                pbar.update(100 - pbar.n)

        return_code = process.wait()
        if return_code != 0:
            raise subprocess.CalledProcessError(
                return_code, command, output="Error during download."
            )

    except FileNotFoundError:
        print("Error: 'gallery-dl' is not installed or not in your system's PATH.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def get_auth_args():
    """
    Prompts the user for authentication or cookie options and returns the
    necessary gallery-dl command-line arguments.
    """
    print("\n🔐 Authentication & Cookie Options:")
    print("1. Enter username & password")
    print("2. Use username & password from a file")
    print("3. **Select a cookie file from the '/cookies' folder**")
    print("4. Use cookies from a web browser")
    print("5. Skip (no credentials or cookies)")

    while True:
        choice = input("Choose an option (1-5): ").strip()
        if choice in ("1", "2", "3", "4", "5"):
            break
        print("Invalid choice. Please enter a number from 1 to 5.")

    # Option 1: Manual username/password
    if choice == "1":
        username = input("Enter username: ").strip()
        password = input("Enter password: ").strip()
        return ["--username", username, "--password", password]

    # Option 2: Username/password from file
    elif choice == "2":
        while True:
            path = input("Enter path to credentials file (or 'cancel'): ").strip()
            if path.lower() == "cancel":
                break
            if os.path.exists(path):
                try:
                    with open(path, "r") as file:
                        lines = [line.strip() for line in file if line.strip()]
                    if len(lines) >= 2:
                        return ["--username", lines[0], "--password", lines[1]]
                    print(
                        "Error: File must have username and password on the first two lines."
                    )
                except Exception as e:
                    print(f"Error reading file: {e}")
            else:
                print("File not found. Please try again.")

    # Option 3: Select a cookie file from the './cookies' directory
    elif choice == "3":
        cookies_dir = "./cookies"
        try:
            cookie_files = [f for f in os.listdir(cookies_dir) if f.endswith(".txt")]
        except FileNotFoundError:
            print(f"Error: The '{cookies_dir}' directory was not found.")
            return None

        if not cookie_files:
            print(f"\nNo cookie files (.txt) found in the '{cookies_dir}' folder.")
            print("Please add your cookie files there to use this option.")
            return None

        print("\nPlease select a cookie file to use:")
        for i, filename in enumerate(cookie_files, 1):
            print(f"  {i}. {filename}")
        print("  0. Cancel")

        while True:
            try:
                selection = int(
                    input(f"Enter number (1-{len(cookie_files)}, or 0): ").strip()
                )
                if 0 <= selection <= len(cookie_files):
                    break
                else:
                    print("Invalid number. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        if selection == 0:
            return None  # User cancelled

        selected_file = cookie_files[selection - 1]
        full_path = os.path.join(cookies_dir, selected_file)
        print(f"✅ Using cookie file: {selected_file}")
        return ["--cookies", full_path]

    # Option 4: Cookies from a browser
    elif choice == "4":
        print(
            "💡 Note: For some browsers (like Firefox), you may need to close it first."
        )
        browser = input("Enter browser name (e.g., chrome, firefox, edge): ").strip()
        if browser:
            return ["--cookies-from-browser", browser]

    return None


def download_single():
    """Handles downloading from a single URL."""
    url = input("\nEnter the URL to download: ").strip()
    if not url:
        print("No URL entered.")
        return

    auth_args = get_auth_args()
    try:
        run_gallery_dl_with_progress(url, auth_args)
        print(f"\n✅ Download completed for: {url}")
    except Exception as e:
        print(f"\n❌ Error during download: {e}")


def bulk_download():
    """Handles downloading from a list of URLs in a file."""
    urls_file = "./URLS.txt"
    if not os.path.exists(urls_file):
        print(f"'{urls_file}' not found. Please create it and add URLs, one per line.")
        return

    auth_args = get_auth_args()
    try:
        with open(urls_file, "r") as file:
            urls = [line.strip() for line in file if line.strip()]
        if not urls:
            print(f"'{urls_file}' is empty.")
            return
    except Exception as e:
        print(f"Error reading URLs file: {e}")
        return

    for i, url in enumerate(urls, 1):
        print(f"\n--- Processing URL {i}/{len(urls)}: {url} ---")
        try:
            run_gallery_dl_with_progress(url, auth_args)
            print(f"\n✅ Download completed for: {url}")
        except Exception as e:
            print(f"❌ Failed to download {url}: {e}")
            continue


def update():
    """Checks for gallery-dl updates."""
    print("\nUpdating gallery-dl...")
    try:
        subprocess.run(["gallery-dl", "-U"], check=True)
        print("\nUpdate check completed.")
    except subprocess.CalledProcessError as e:
        print(f"Update command failed: {e}")
    except FileNotFoundError:
        print("Error: 'gallery-dl' is not installed or not in your system's PATH.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def show_help():
    """Displays the help message."""
    help_text = """
    Gallery-dl Terminal Utility 📜

    Options:
    1. Download Single:   Download content from a single URL.
    2. Bulk Download:     Download from all URLs listed in 'URLS.txt'.
    3. Update:            Check for and apply updates to gallery-dl.
    4. Help:              Show this help message.
    5. Exit:              Quit the program.

    Authentication:
    Before downloading, you can choose to log in with a username/password,
    or use cookies from the '/cookies' folder or directly from a browser.
    This is necessary for sites that require you to be logged in.
    """
    print(help_text)


def main():
    """Main function to run the utility."""
    setup_directories()
    print("\n--- Gallery-dl Terminal Utility ---")
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
            print("\nExiting program. Goodbye! 👋")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")


if __name__ == "__main__":
    main()
