from pathlib import Path
import re
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

nltk.download('vader_lexicon')

def clear_screen():
    print("\033[H\033[J", end="")

def get_md_files(dir_path):
    return list(Path(dir_path).glob("**/*.md"))

def tokenize_text(text):
    text = text.lower()
    return set(re.findall(r'\b\w+\b', text))

def calculate_sentiment(text):
    sia = SentimentIntensityAnalyzer()
    return sia.polarity_scores(text)

def format_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"