import json
import sys
from pathlib import Path
from .analysis import analyze_directory
from .utils.utils import clear_screen, format_size
from . import __version__, __author__
from .report_generator import generate_markdown_report


def check_for_cached_files():
    """Check if valid cached files exist and are properly formatted"""
    cache_dir = Path(__file__).parent / "cache"
    required_files = {
        'analysis': cache_dir / "analysis.json",
        'keywords': cache_dir / "keyword_data.json",
        # Note: Your output shows 'similarity.csv' instead
        'similarity': cache_dir / "similarity_correlation.csv"
    }

    try:
        # Check if directory exists
        if not cache_dir.exists():
            return False

        # Check each required file
        for file_type, file_path in required_files.items():
            if not file_path.exists():
                return False

            if file_path.stat().st_size == 0:
                return False

            # Validate JSON files
            if file_path.suffix == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if not data:
                        return False

            # Validate CSV file - match the actual filename being generated
            if file_type == 'similarity':
                # Use the actual filename being generated
                csv_path = cache_dir / "similarity.csv"
                if not csv_path.exists() or csv_path.stat().st_size == 0:
                    return False
                try:
                    import pandas as pd
                    df = pd.read_csv(csv_path)
                    if df.empty:
                        return False
                except Exception:
                    return False

        return True

    except Exception:
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
            'analysis.json': json.dumps(default_analysis),
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


def display_menu(cached_files_exist=False):
    """Display the main menu with options based on cache status"""
    print("\nZettelTK - Main Menu")
    if not cached_files_exist:
        print("1. Perform Initial Analysis")
    else:
        print("1. Generate New Analysis")
        print("2. Generate Reports")
    print("Q. Quit")


def main():
    # Ensure cache directory exists
    ensure_cache_directory()

    # Check for cached files
    cached_files_exist = check_for_cached_files()

    clear_screen()
    print(f"Welcome to ZettelTK\nAuthor: {__author__}\nVersion: {__version__}")

    while True:
        # Recheck cache status at start of each loop
        cached_files_exist = check_for_cached_files()

        clear_screen()
        display_menu(cached_files_exist)
        choice = input("\nEnter your choice: ").strip().lower()

        if choice == '1':
            clear_screen()
            print("Performing analysis...\n")
            analysis_data = analyze_directory("data")
            cached_files_exist = check_for_cached_files()
            print("\nAnalysis Complete!")
            print(
                f"Processed {analysis_data['file_stats']['total_files']} files")
            print(
                f"Total size: {format_size(analysis_data['file_stats']['total_size'])}")
            print(
                f"Unique tokens: {analysis_data['text_stats']['unique_tokens']}")
            input("\nPress Enter to return to menu...")

        elif choice == '2' and cached_files_exist:
            clear_screen()
            generate_markdown_report(Path("reports"))
            input("\nPress Enter to return to menu...")

        elif choice in ['q', 'Q']:
            sys.exit()


if __name__ == "__main__":
    print("This script is intended to be run as part of the ZettelTK package.")
