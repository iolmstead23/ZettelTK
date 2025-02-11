import json
import sys
import os
from pathlib import Path
from .analysis import analyze_directory
from .utils.utils import clear_screen, format_size
from . import __version__, __author__


def check_for_cached_files():
    """Check if valid cached files exist and are properly formatted"""
    cache_dir = Path(__file__).parent / "cache"
    required_files = {
        'analysis': cache_dir / "ztk_analysis.json",
        'keywords': cache_dir / "keyword_data.json",
        'similarity': cache_dir / "similarity_correlation.csv"
    }

    try:
        # Check if directory exists
        if not cache_dir.exists():
            print("Cache directory not found")
            return False

        # Check each required file
        for file_type, file_path in required_files.items():
            if not file_path.exists():
                print(f"Missing cache file: {file_path.name}")
                return False

            if file_path.stat().st_size == 0:
                print(f"Empty cache file: {file_path.name}")
                return False

            # Verify JSON files are valid
            if file_path.suffix == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    # This will raise an exception if JSON is invalid
                    json.load(f)

            # Verify CSV file is valid
            if file_path.suffix == '.csv':
                with open(file_path, 'r', encoding='utf-8') as f:
                    # Check if file has content and proper CSV format
                    first_line = f.readline()
                    if not first_line or ',' not in first_line:
                        print(f"Invalid CSV format in: {file_path.name}")
                        return False

        return True

    except json.JSONDecodeError:
        print("Invalid JSON format in cache files")
        return False
    except Exception as e:
        print(f"Error checking cache files: {str(e)}")
        return False


def ensure_cache_directory():
    """Ensure cache directory and files exist"""
    cache_dir = Path(__file__).parent / "cache"

    try:
        # Create cache directory if it doesn't exist
        cache_dir.mkdir(exist_ok=True)

        # Define default empty structures
        default_analysis = {"file_stats": {}, "text_stats": {}}
        default_keywords = {}

        # Create empty files if they don't exist
        files_to_create = {
            'ztk_analysis.json': json.dumps(default_analysis),
            'keyword_data.json': json.dumps(default_keywords),
            'similarity_correlation.csv': "source,target,similarity\n"
        }

        for filename, default_content in files_to_create.items():
            file_path = cache_dir / filename
            if not file_path.exists():
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(default_content)

        return True

    except Exception as e:
        print(f"Error ensuring cache directory: {str(e)}")
        return False


def display_menu(analysis_performed=False, cached_files_exist=False):
    """Display the main menu with options"""
    print("\nZettelTK - Main Menu")
    if not analysis_performed and not cached_files_exist:
        print("1. Perform Initial Analysis")
    else:
        print("1. Generate New Analysis")
        print("2. Generate Reports")
        print("3. Exit")
    print("Q. Quit")


def main():
    analysis_data = None
    analysis_performed = False

    # Ensure cache directory exists
    ensure_cache_directory()

    # Check for cached files
    cached_files_exist = check_for_cached_files()

    clear_screen()
    print(f"Welcome to ZettelTK\nAuthor: {__author__}\nVersion: {__version__}")

    # If cached files exist, skip the initial analysis option
    if cached_files_exist:
        print(
            "\nCached analysis files found. You can generate reports or run a new analysis.")
        analysis_performed = True  # Treat as if analysis has already been performed

    while True:
        clear_screen()
        display_menu(analysis_performed, cached_files_exist)
        choice = input("\nEnter your choice: ").strip().lower()

        if choice == '1':
            if not analysis_performed and not cached_files_exist:
                # Initial analysis
                clear_screen()
                print("Performing initial analysis...\n")
                analysis_data = analyze_directory("data")
                analysis_performed = True
                cached_files_exist = True  # Update cache status
                print("\nAnalysis Complete!")
                print(
                    f"Processed {analysis_data['file_stats']['total_files']} files")
                print(
                    f"Total size: {format_size(analysis_data['file_stats']['total_size'])}")
                print(
                    f"Unique tokens: {analysis_data['text_stats']['unique_tokens']}")
                input("\nPress Enter to return to menu...")
            else:
                # Generate new analysis (overwrite existing cache)
                clear_screen()
                print("Generating new analysis...\n")
                analysis_data = analyze_directory("data")
                print("\nNew Analysis Complete!")
                print(
                    f"Processed {analysis_data['file_stats']['total_files']} files")
                print(
                    f"Total size: {format_size(analysis_data['file_stats']['total_size'])}")
                print(
                    f"Unique tokens: {analysis_data['text_stats']['unique_tokens']}")
                input("\nPress Enter to return to menu...")

        elif choice == '2' and (analysis_performed or cached_files_exist):
            clear_screen()
            from .report_generator import generate_markdown_report
            report_file = generate_markdown_report(Path("data"))
            print(f"\nReport generated at: {report_file}")
            input("\nPress Enter to return to menu...")

        elif choice == 'Q' or choice == 'q' or choice == '3':
            sys.exit()


if __name__ == "__main__":
    print("This script is intended to be run as part of the ZettelTK package.")
