from pathlib import Path
import json
import pandas as pd
from datetime import datetime


def generate_markdown_report(base_dir, analysis_data=None):
    """Generate a markdown format report from cached data"""
    base_dir = Path(base_dir)
    cache_dir = Path(__file__).parent / "cache"  # Fix cache directory path

    # Create data directory if it doesn't exist
    base_dir.mkdir(exist_ok=True)

    # Add timestamp to report filename
    timestamp = datetime.now().strftime("%Y-%m-%d")
    report_file = base_dir / f"analysis_report_{timestamp}.md"

    # Load cached data with correct paths
    analysis_file = cache_dir / "ztk_analysis.json"
    keyword_file = cache_dir / "keyword_data.json"
    similarity_file = cache_dir / "similarity_correlation.csv"

    # Load data with error handling and debug printing
    try:
        with open(analysis_file, 'r') as f:
            analysis = json.load(f)
            print(f"Successfully loaded analysis data from {analysis_file}")
    except FileNotFoundError:
        print(f"Analysis file not found at {analysis_file}")
        analysis = None
    except json.JSONDecodeError:
        print(f"Invalid JSON in analysis file at {analysis_file}")
        analysis = None

    try:
        with open(keyword_file, 'r') as f:
            keywords = json.load(f)
            print(f"Successfully loaded keyword data from {keyword_file}")
    except FileNotFoundError:
        print(f"Keyword file not found at {keyword_file}")
        keywords = None
    except json.JSONDecodeError:
        print(f"Invalid JSON in keyword file at {keyword_file}")
        keywords = None

    try:
        if similarity_file.exists():
            similarity_df = pd.read_csv(similarity_file)
            print(
                f"Successfully loaded similarity data from {similarity_file}")
        else:
            print(f"Similarity file not found at {similarity_file}")
            similarity_df = None
    except Exception as e:
        print(f"Error loading similarity file: {str(e)}")
        similarity_df = None

    # Start building markdown content
    md_content = [
        "# ZettelTK Analysis Report\n",
        f"Generated on: {datetime.now().strftime('%B %d, %Y')}\n"
    ]

    # File Statistics
    if analysis and 'file_stats' in analysis:
        md_content.append("## File Statistics\n")
        md_content.append(
            f"- Total files: {analysis['file_stats']['total_files']}")
        md_content.append(
            f"- Total size: {analysis['file_stats']['total_size']} bytes")
        md_content.append(
            f"- Average file size: {analysis['file_stats']['avg_size']} bytes\n")

    # Text Statistics
    if analysis and 'text_stats' in analysis:
        md_content.append("## Text Statistics\n")
        md_content.append(
            f"- Unique tokens: {analysis['text_stats']['unique_tokens']}")
        md_content.append(
            f"- Average tokens per file: {analysis['text_stats']['avg_tokens_per_file']}")
        md_content.append("\n### Sentiment Analysis\n")
        for k, v in analysis['text_stats']['sentiment'].items():
            md_content.append(f"- {k.capitalize()}: {v:.2f}")

    # Keyword Analysis
    if keywords:
        md_content.append("\n## Keyword Analysis\n")
        for gram_type in ['trigrams', 'bigrams', 'unigrams']:
            md_content.append(f"### Top {gram_type.capitalize()}")
            items = keywords.get(gram_type, [])[:5]  # Show top 5
            for item in items:
                if gram_type == 'unigrams':
                    md_content.append(
                        f"- {item['word']} ({item['count']} occurrences)")
                else:
                    md_content.append(
                        f"- {item['phrase']} ({item['count']} occurrences)")
            md_content.append("")

# In report_generator.py, replace the similarity analysis section with:

    # Similarity Analysis
    if similarity_df is not None:
        md_content.append("\n## Document Similarity\n")
        md_content.append("### Most Similar Documents\n")

        # Find pairs with similarity < 1
        similarities = []
        for i in range(len(similarity_df)):
            for j in range(i+1, len(similarity_df)):
                similarity = similarity_df.iloc[i, j]
                if 0 < similarity < 1:  # Only include similarities between 0 and 1
                    similarities.append((
                        similarity_df.columns[i],  # Use actual note names
                        similarity_df.columns[j],
                        similarity
                    ))

        # Sort and take top 5
        top_pairs = sorted(similarities, key=lambda x: x[2], reverse=True)[:5]

        if top_pairs:
            for pair in top_pairs:
                md_content.append(
                    f"- {Path(pair[0]).stem} ↔ {Path(pair[1]).stem} (similarity: {pair[2]:.3f})")
        else:
            md_content.append(
                "No similar documents found with correlation between 0 and 1.")

    # Write to file
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_content))
        print(f"Successfully wrote report to {report_file}")
    except Exception as e:
        print(f"Error writing report: {str(e)}")

    print(f"Markdown report generated at {report_file}")
