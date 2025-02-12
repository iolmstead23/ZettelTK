import pandas as pd
from pathlib import Path
import nltk
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import pandas as pd
import re
from collections import Counter, defaultdict
from sklearn.metrics import jaccard_score
import numpy as np
import os

# Initialize NLTK components
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# Get the package directory path
PACKAGE_DIR = Path(__file__).parent.parent
CACHE_DIR = PACKAGE_DIR / "cache"
DATA_DIR = PACKAGE_DIR / "data"

# Load a list of valid English words
nltk.download('words', quiet=True)
valid_words = set(nltk.corpus.words.words())


def ensure_directories():
    """Create necessary directories if they don't exist"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_wordnet_pos(treebank_tag):
    """Maps POS tags to WordNet tags for accurate lemmatization."""
    tag = treebank_tag[0].upper()
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}
    return tag_dict.get(tag, wordnet.NOUN)


def remove_markdown(text):
    """Strips markdown formatting from text."""
    # Remove links and images
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'!\[[^\]]*\]\([^\)]+\)', '', text)
    # Remove code blocks
    text = re.sub(r'`{3}.*?`{3}', '', text, flags=re.DOTALL)
    text = re.sub(r'`([^`]*)`', r'\1', text)
    # Remove bold/italic
    text = re.sub(r'\*\*([^\*]*)\*\*', r'\1', text)
    text = re.sub(r'\*([^\*]*)\*', r'\1', text)
    # Remove headers, lists, blockquotes
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*[\*\-+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\>+', '', text, flags=re.MULTILINE)
    return text.strip()


def process_text(text):
    """Processes text into a set of cleaned and lemmatized tokens."""
    text = remove_markdown(text)
    tokens = word_tokenize(text)
    pos_tags = nltk.pos_tag(tokens)
    lemmas = []
    for token, tag in pos_tags:
        clean_token = re.sub(r'[^a-zA-Z]', '', token)
        if not clean_token:
            continue
        clean_token = clean_token.lower()
        if len(clean_token) < 3 or clean_token in stop_words:
            continue
        pos = get_wordnet_pos(tag)
        lemma = lemmatizer.lemmatize(clean_token, pos=pos)
        if lemma in valid_words:
            lemmas.append(lemma)
    return lemmas


def create_dataframe(notes_dir, top_n=1500):
    """Generates a one-hot encoded DataFrame from markdown notes."""
    notes_dir = Path(notes_dir)
    if not notes_dir.exists():
        print(f"Warning: Directory {notes_dir} does not exist")
        return pd.DataFrame()  # Return empty DataFrame instead of failing

    note_files = list(notes_dir.glob('*.md'))
    if not note_files:
        print(f"Warning: No markdown files found in {notes_dir}")
        return pd.DataFrame()

    notes_data = []
    all_lemmas = []

    for file in note_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            lemmas = process_text(content)
            all_lemmas.extend(lemmas)
            notes_data.append({'title': file.stem, 'lemmas': lemmas})
        except Exception as e:
            print(f"Warning: Error processing {file}: {str(e)}")
            continue

    if not notes_data:
        return pd.DataFrame()

    lemma_counter = Counter(all_lemmas)
    top_lemmas = [lemma for lemma, _ in lemma_counter.most_common(top_n)]

    df = pd.DataFrame(0, index=[note['title']
                      for note in notes_data], columns=top_lemmas)
    for note in notes_data:
        for lemma in note['lemmas']:
            if lemma in top_lemmas:
                df.at[note['title'], lemma] = 1

    df = df.reset_index().rename(columns={'index': 'title'})
    return df


def jaccard_similarity(matrix):
    """Computes the Jaccard similarity matrix."""
    if matrix.empty:
        return np.array([[]])

    num_notes = matrix.shape[0]
    similarity_matrix = np.zeros((num_notes, num_notes))

    for i in range(num_notes):
        for j in range(num_notes):
            try:
                similarity_matrix[i, j] = jaccard_score(
                    matrix.iloc[i], matrix.iloc[j], average='binary', zero_division=0)
            except Exception as e:
                print(
                    f"Warning: Error computing similarity for rows {i} and {j}: {str(e)}")
                similarity_matrix[i, j] = 0

    return similarity_matrix


def create_correlation_matrix(df, output_file):
    """Creates and saves the Jaccard similarity correlation matrix."""
    if df.empty:
        print("Warning: Empty DataFrame, skipping correlation matrix creation")
        return

    similarity_matrix = jaccard_similarity(df)
    correlation_df = pd.DataFrame(
        similarity_matrix, index=df.index, columns=df.index)

    print("\nColumn headers in correlation_df:")
    for col in correlation_df.columns:
        print(f"'{col}'")

    try:
        correlation_df.to_csv(output_file)
        print(f"Correlation matrix saved to {output_file}")
    except Exception as e:
        print(f"Error saving correlation matrix: {str(e)}")


def run_similarity_pipeline(base_dir):
    """Run the complete similarity analysis pipeline."""
    # Ensure directories exist
    ensure_directories()

    # Define paths using package directory
    similarity_path = CACHE_DIR / "similarity.csv"
    correlation_path = CACHE_DIR / "similarity_correlation.csv"

    # Create and save similarity DataFrame
    df = create_dataframe(base_dir, top_n=1500)
    if not df.empty:
        try:
            df.to_csv(similarity_path, index=False)
            print(f"One-hot encoded data saved to {similarity_path}")

            # Create and save correlation matrix
            one_hot_df = pd.read_csv(similarity_path, index_col=0)
            create_correlation_matrix(one_hot_df, correlation_path)
        except Exception as e:
            print(f"Error in similarity pipeline: {str(e)}")
    else:
        print("No data to process, skipping similarity analysis")
