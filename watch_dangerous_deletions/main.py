import os
import pickle
import sys
import time
import tkinter as tk
from tkinter import messagebox

from pyfiglet import Figlet
from rich import print

from winsound import PlaySound, SND_FILENAME, SND_ASYNC

from . import settings


def sync_blacklist(writables=None):

    # Ensure the custom blacklist file exists
    if not os.path.exists("custom_blacklist.pkl"):
        with open("custom_blacklist.pkl", "wb") as f:
            pickle.dump([], f)
        return []

    # Read the blacklist

    with open("custom_blacklist.pkl", "rb") as f:
        initial_blacklist_data = pickle.load(f)

    # Write any writables
    if writables:
        with open("custom_blacklist.pkl", "wb") as f:
            if initial_blacklist_data:
                merged_blacklist_data = initial_blacklist_data.append(writables)
            else:
                merged_blacklist_data = writables
            pickle.dump(merged_blacklist_data, f)

    # Read the blacklist again
    with open("custom_blacklist.pkl", "rb") as f:
        summed_blacklist_data = pickle.load(f)

    return summed_blacklist_data


def init():

    global ROOT_WIN
    ROOT_WIN = tk.Tk()
    ROOT_WIN.withdraw()

    # Print CLI title
    fig = Figlet()
    text = fig.renderText("Watch Dangerous Deletions")
    print(f"[green]{text}[/]")

    sync_blacklist()


def warning(title, message, ignorable):

    print(settings.warning_sound)
    PlaySound(settings.warning_sound, SND_FILENAME | SND_ASYNC)

    answer = messagebox.askyesno(
        title=title,
        message=message,
    )

    if answer is True:
        print(f"\n[cyan]Ignoring '{ignorable}'[/]\n")
        sync_blacklist(ignorable)
    elif answer is False:
        return
    else:
        print("[yellow]Exiting![/]")
        sys.exit(1)

    ROOT_WIN.destroy()


def check_ignorable(ignorable):
    """Check if files are on the user ignorable blacklist doodad"""

    if ignorable in sync_blacklist():

        print(f"[yellow]'{ignorable}' in user ignorable list. Ignoring...[/]")
        return True


def scan_recycle_path(origin_path):
    """Scan the recycle path for deleted files and folders matching criteria."""

    # Get the recycle bin path for the origin path
    recycle_path = os.path.join(origin_path, settings.recycle_suffix)

    # Get temp list of top level dirs in all drives
    all_origin_top_level_dirs = sum([os.listdir(x) for x in settings.origin_paths], [])
    # print(all_origin_top_level_dirs)

    i = 0
    print(f"[yellow]Scanning Recycle Bin: {recycle_path}...[/]")
    for root, dirs, files in os.walk(recycle_path):

        # ROOT STUFF: #############################################################
        # Ignore root if it is on the blacklist

        if not check_ignorable(root):

            if os.path.split(root)[1] == "@Recycle":
                print("[yellow]Ignoring Recycle Bin[/]")
                continue

            print("----> " + root)

            # Split the root path into its components
            split_path = root.split(os.sep)

            # Check root is top level dir
            if len(split_path) == 3:

                # Check it exists in one of the origin paths
                if split_path[-1] not in all_origin_top_level_dirs:

                    print(f"[red]Top level folder deletion detected\n'{root}'...[/]\n")

                    warning(
                        title="Dangerous Deletion detected!",
                        message=f"A top level folder has been deleted!\n'{root}'"
                        + "\n\nDo you want to ignore this? Selecting no will retry scan.",
                        ignorable=root,
                    )

            # Warn if deleted folder is larger than 100GB
            if os.path.getsize(root) > (
                settings.warn_delete_size * 1000000000
            ):  # in bytes

                print(
                    f"[red]Oversize deletion detected\n'{root}'[/]"
                    + f"is larger than {int(settings.warn_delete_size)}GB...[/]\n"
                )

                warning(
                    title="Dangerous Deletion detected!",
                    message=f"Woah! Content in deleted folder\n'{root}' "
                    + f"is larger than {int(settings.warn_delete_size)}GB...[/]\n"
                    + "\n\nDo you want to ignore this? Selecting no will retry scan.",
                    ignorable=root,
                )

        # DIR STUFF: ##############################################################

        for dir in dirs:
            # print("----> " + os.path.join(root, dir))
            if not check_ignorable(dir):

                # Warn if deleted folder is in the whitelist
                if dir in settings.warn_dir_whitelist:

                    print(
                        f"[red]Woah! Deleted folder name '{root}' "
                        + f"is in the whitelist...[/]\n"
                    )
                    warning(
                        title="Dangerous Deletion detected!",
                        message=f"Woah! Deleted folder name is in the whitelist\n'{root}'"
                        + "\n\nDo you want to ignore this? Selecting no will retry scan.",
                        ignorable=root,
                    )

        # FILES STUFF: ############################################################
        # Warn if files in deleted folder are in the whitelist

        for file_ in files:
            # print("----> " + os.path.join(root, file_))
            if not check_ignorable(file_):

                file_ext = os.path.splitext(file_)[1]
                if file_ext in (settings.warn_file_ext_whitelist):

                    warning(
                        title="Dangerous Deletion detected!",
                        message=f"Woah! Deleted file is in the whitelist\n'{root}'"
                        + "\n\nDo you want to ignore this? Selecting no will retry scan.",
                        ignorable=root,
                    )

    # print(f"[cyan]Done scanning :thumbs_up:[/]\n")
    return


def main():

    try:

        init()  # Ensure the custom blacklist file exists, etc

        # Loop forevz
        while True:

            for path_ in settings.origin_paths:
                scan_recycle_path(path_)

            # Wait before next loop iteration
            print(
                f"\n[cyan]Waiting for {settings.scan_interval} seconds before scanning...[/]"
            )
            try:
                time.sleep(settings.scan_interval)
            except KeyboardInterrupt:
                print("Starting next search in 3 seconds...")
                print("Press Ctrl+C again to exit.")
                time.sleep(3)

    except KeyboardInterrupt:

        print("[green]User exited[/]\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
