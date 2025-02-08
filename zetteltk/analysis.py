import json
from pathlib import Path
import hashlib
from .utils import keyword_report as kr
from .utils import similarity_checker as sc
from .utils.utils import get_md_files, tokenize_text, calculate_sentiment
from collections import defaultdict
import os

# Get the package directory path
PACKAGE_DIR = Path(__file__).parent
ANALYSIS_FILE = PACKAGE_DIR / "cache/ztk_analysis.json"

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
    
    analysis = {
        'file_stats': calculate_file_stats(md_files),
        'text_stats': process_text_content(md_files),
    }

    # Save analysis to JSON
    with open(ANALYSIS_FILE, 'w+') as f:
        json.dump(analysis, f)

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
    if not md_files:
        return {
            'unique_tokens': 0,
            'avg_tokens_per_file': 0,
            'sentiment': {'compound': 0, 'pos': 0, 'neu': 0, 'neg': 0}
        }
        
    token_counts = []
    all_tokens = set()
    sentiments = []

    for file in md_files:
        text = file.read_text(encoding='utf-8')
        tokens = tokenize_text(text)
        token_counts.append(len(tokens))
        all_tokens.update(tokens)
        sentiments.append(calculate_sentiment(text))

    return {
        'unique_tokens': len(all_tokens),
        'avg_tokens_per_file': sum(token_counts) // len(token_counts) if token_counts else 0,
        'sentiment': average_sentiment(sentiments)
    }

def average_sentiment(sentiments):
    if not sentiments:
        return {'compound': 0, 'pos': 0, 'neu': 0, 'neg': 0}

    avg = defaultdict(float)
    for key in sentiments[0]:
        avg[key] = sum(s[key] for s in sentiments) / len(sentiments)
    return avg
