import json
import sys
import os
from .analysis import analyze_directory
from .utils.utils import clear_screen, format_size
from . import __version__, __author__


def display_menu(analysis_performed=False):
    print("\nZettelTK - Main Menu")
    if not analysis_performed:
        print("1. Perform Initial Analysis")
    else:
        print("1. Generate New Analysis")
        print("2. Generate Reports")
        print("3. Exit")
    print("Q. Quit")


def main():
    analysis_data = None
    analysis_performed = False

    clear_screen()
    print(f"Welcome to ZettelTK\nAuthor: {__author__}\nVersion: {__version__}")

    while True:
        display_menu(analysis_performed)
        choice = input("\nEnter your choice: ").strip().lower()

        if choice == '1':
            analysis_data = analyze_directory("data")
            analysis_performed = True

            print("\nAnalysis Complete!")
            print(
                f"Processed {analysis_data['file_stats']['total_files']} files")
            print(
                f"Total size: {format_size(analysis_data['file_stats']['total_size'])}")
            print(
                f"Unique tokens: {analysis_data['text_stats']['unique_tokens']}")
        elif choice == 'Q' or choice == 'q':
            sys.exit()


if __name__ == "__main__":
    print("This script is intended to be run as part of the ZettelTK package.")
