import json
from pathlib import Path
import os
import re
import nltk
import markdown
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag

# Get the package directory path
PACKAGE_DIR = Path(__file__).parent.parent
CACHE_DIR = PACKAGE_DIR / "cache"
DATA_DIR = PACKAGE_DIR / "data"

# Download required NLTK packages
nltk.download('punkt', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('stopwords', quiet=True)

# Initialize stopwords
stop_words = set(stopwords.words('english'))

def ensure_directories():
    """Create necessary directories if they don't exist"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def has_unique_tokens(ngram):
    if isinstance(ngram, str):
        tokens = ngram.split()
    else:
        tokens = ngram
    return len(tokens) == len(set(tokens))

def remove_used_tokens(tokens, used_ngrams):
    """Remove tokens that were used in ngrams from the token list"""
    used_tokens = set()
    for ngram in used_ngrams:
        used_tokens.update(ngram)
    return [token for token in tokens if token not in used_tokens]

def generate_ngrams(tokens, n):
    """Generate n-grams from tokens while validating each token"""
    ngrams = []
    for i in range(len(tokens)-n+1):
        ngram = ' '.join(tokens[i:i+n])
        if all(is_valid_word(token) for token in tokens[i:i+n]):
            ngrams.append(ngram)
    return ngrams

def is_valid_word(word):
    """Validate if a word meets the criteria for processing"""
    if len(word) < 3:
        return False
    if any(c in word for c in '₁₂₃₄₅₆₇₈₉₀¹²³⁴⁵⁶⁷⁸⁹⁰'):
        return False
    if not any(c.isalpha() for c in word):
        return False
    if sum(not c.isalnum() for c in word) > 1:
        return False
    return True

def get_top_ngrams(tokens, n, count=20):
    """Get top n-grams and return remaining unused tokens"""
    if not tokens:
        return [], []
        
    ngram_counts = {}
    used_tokens = set()

    ngrams = generate_ngrams(tokens, n)
    for ngram in ngrams:
        ngram_counts[ngram] = ngram_counts.get(ngram, 0) + 1

    top_ngrams = sorted(ngram_counts.items(),
                       key=lambda x: x[1], reverse=True)[:count]

    for ngram, _ in top_ngrams:
        used_tokens.update(ngram.split())

    remaining_tokens = [token for token in tokens if token not in used_tokens]
    return top_ngrams, remaining_tokens

def markdown_directory_to_keywords(dir_path, unique=False):
    """Process markdown files and extract keywords"""
    dir_path = Path(dir_path)
    if not dir_path.exists():
        print(f"Warning: Directory {dir_path} does not exist")
        return {'trigrams': [], 'bigrams': [], 'unigrams': []}

    lemmatizer = WordNetLemmatizer()
    symbols = ['', '.', ":", "'s", "(", ")", "", "[", "]", None,
              "'", ",", "`", "--", "|", ";", "?", "%", "!", " ", "*"]

    all_tokens = []

    try:
        # Get all markdown files
        files = list(dir_path.glob('*.md'))
        if not files:
            print(f"Warning: No markdown files found in {dir_path}")
            return {'trigrams': [], 'bigrams': [], 'unigrams': []}

        # Process each markdown file
        for file_path in files:
            try:
                file_title = file_path.stem.lower()
                filename_tokens = file_title.split()

                content = file_path.read_text(encoding="utf8")
                # Clean and process content
                content = re.sub(r'```[\s\S]*?```', '', content)
                content = re.sub(r'\${1,2}[^$]*\${1,2}', '', content)
                content = re.sub(r'\[[^\]]*\]', '', content)
                content = re.sub(r'e\.g\.|i\.e\.', '', content)
                html = markdown.markdown(content)
                text = re.sub('<[^>]*>', '', html)
                text = re.sub(r'\w+:', '', text)
                text = re.sub('example', '', text)

                # Process tokens
                tokens = word_tokenize(text.lower())
                tagged = pos_tag(tokens)

                valid_tokens = []
                for token, tag in tagged:
                    if (tag == 'NN' and
                        token not in stop_words and
                        token not in symbols and
                        is_valid_word(token) and
                            token not in filename_tokens):
                        valid_tokens.append(lemmatizer.lemmatize(token))

                all_tokens.extend(valid_tokens)

            except Exception as e:
                print(f"Warning: Error processing file {file_path}: {str(e)}")
                continue

        # Process n-grams
        trigrams, remaining_after_trigrams = get_top_ngrams(all_tokens, 3)
        trigrams = [(gram, count)
                   for gram, count in trigrams if has_unique_tokens(gram)]

        bigrams, remaining_after_bigrams = get_top_ngrams(
            remaining_after_trigrams, 2)
        bigrams = [(gram, count)
                  for gram, count in bigrams if has_unique_tokens(gram)]

        unigram_freq = nltk.FreqDist(remaining_after_bigrams)
        unigrams = unigram_freq.most_common(20)

        return {
            'trigrams': [{"phrase": p, "count": c} for p, c in trigrams],
            'bigrams': [{"phrase": p, "count": c} for p, c in bigrams],
            'unigrams': [{"word": w, "count": c} for w, c in unigrams]
        }

    except Exception as e:
        print(f"Error processing markdown files: {str(e)}")
        return {'trigrams': [], 'bigrams': [], 'unigrams': []}

def save_keyword_data(keywords, output_file):
    """Save keyword data to JSON file"""
    try:
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with output_file.open('w', encoding='utf-8') as f:
            json.dump(keywords, f, indent=2)
            
    except Exception as e:
        print(f"Error saving keyword data: {str(e)}")

def generate_keyword_report(base_dir):
    """Generate and save keyword report"""
    # Ensure directories exist
    ensure_directories()
    
    # Define output path using package directory
    output_file = CACHE_DIR / "keyword_data.json"
    
    try:
        keywords = markdown_directory_to_keywords(base_dir)
        save_keyword_data(keywords, output_file)
        print(f"Keyword data saved to {output_file}")
    except Exception as e:
        print(f"Error generating keyword report: {str(e)}")
