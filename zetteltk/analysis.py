import json
from pathlib import Path
from .utils import keyword_report as kr
from .utils import similarity_checker as sc
from .utils.utils import get_md_files, tokenize_text, calculate_sentiment
from collections import defaultdict
from datetime import datetime

# Get the package directory path
PACKAGE_DIR = Path(__file__).parent
# Updated filename as you specified
ANALYSIS_FILE = PACKAGE_DIR / "cache/analysis.json"
TOKEN_CACHE_FILE = PACKAGE_DIR / "cache/tokens.json"


def ensure_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        PACKAGE_DIR / 'data',
        PACKAGE_DIR / 'cache'
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def analyze_directory(dir_path):
    # Ensure directories exist
    ensure_directories()

    # Convert dir_path to absolute path relative to package
    absolute_dir_path = PACKAGE_DIR / dir_path

    # Get markdown files, return empty list if none exist
    md_files = get_md_files(absolute_dir_path)

    # Run analysis even if no files exist
    kr.generate_keyword_report(absolute_dir_path)
    sc.run_similarity_pipeline(absolute_dir_path)

    text_stats = process_text_content(md_files)

    # Prepare full analysis
    analysis = {
        'generated_at': datetime.now().isoformat(),
        'file_stats': {
            'total_files': len(md_files),
            'total_size': sum(f.stat().st_size for f in md_files),
            'avg_size': sum(f.stat().st_size for f in md_files) // len(md_files) if md_files else 0
        },
        'text_stats': {
            'unique_tokens': text_stats['unique_tokens'],
            'avg_tokens_per_file': text_stats['avg_tokens_per_file'],
            'sentiment': text_stats['sentiment']
        }
    }

    # Save analysis to JSON (without token list)
    with open(ANALYSIS_FILE, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2)

    return analysis


def calculate_file_stats(md_files):
    if not md_files:
        return {
            'total_files': 0,
            'total_size': 0,
            'avg_size': 0
        }

    total_size = sum(f.stat().st_size for f in md_files)
    return {
        'total_files': len(md_files),
        'total_size': total_size,
        'avg_size': total_size // len(md_files) if md_files else 0
    }


def process_text_content(md_files):
    # Initialize data structures for token processing
    token_counts = []
    all_tokens = set()
    sentiments = []
    file_tokens = {}

    def normalize_filename(filename):
        return filename.replace('.md', '').strip().lower()

    # Process each markdown file
    for file in md_files:
        # Read file content
        text = file.read_text(encoding='utf-8')

        # Generate tokens
        tokens = tokenize_text(text)

        # Normalize filename for consistent key
        normalized_filename = normalize_filename(file.name)

        # Store tokens for each file
        file_tokens[normalized_filename] = tokens

        # Collect token statistics
        token_counts.append(len(tokens))
        all_tokens.update(tokens)
        all_unique_tokens = list(all_tokens)

        # Calculate sentiment for each file
        sentiments.append(calculate_sentiment(text))

    # Prepare token analysis results
    token_analysis = {
        'unique_tokens': len(all_tokens),
        'avg_tokens_per_file': sum(token_counts) // len(token_counts) if token_counts else 0,
        'sentiment': average_sentiment(sentiments)
    }

    # Save tokens to a separate JSON file
    with open(TOKEN_CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_unique_tokens, f, indent=1)

    return token_analysis


def average_sentiment(sentiments):
    if not sentiments:
        return {'compound': 0, 'pos': 0, 'neu': 0, 'neg': 0}

    avg = defaultdict(float)
    for key in sentiments[0]:
        avg[key] = sum(s[key] for s in sentiments) / len(sentiments)
    return avg
