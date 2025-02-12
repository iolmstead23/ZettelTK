from pathlib import Path
import re
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Download necessary NLTK resources
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('vader_lexicon')


def clear_screen():
    print("\033[H\033[J", end="")


def get_md_files(dir_path):
    return list(Path(dir_path).glob("**/*.md"))


def tokenize_text(text):
    # Initialize lemmatizer
    lemmatizer = WordNetLemmatizer()

    # Get English stop words
    stop_words = set(stopwords.words('english'))

    # Additional custom stop words specific to your domain
    custom_stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at',
        'to', 'for', 'of', 'with', 'by', 'from', 'up', 'about',
        'into', 'over', 'after', 'is', 'are', 'was', 'were'
    }

    # Combine stop words
    all_stop_words = stop_words.union(custom_stop_words)

    # Tokenize and preprocess
    tokens = word_tokenize(text.lower())

    # Filter and lemmatize tokens
    filtered_tokens = [
        lemmatizer.lemmatize(token)  # Lemmatize
        for token in tokens
        if (token.isalnum() and  # Only alphanumeric
            len(token) > 1 and    # Longer than 1 character
            token not in all_stop_words)  # Not a stop word
    ]

    return list(set(filtered_tokens))  # Remove duplicates


def calculate_sentiment(text):
    sia = SentimentIntensityAnalyzer()
    return sia.polarity_scores(text)


def format_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"
