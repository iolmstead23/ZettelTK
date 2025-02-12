from pathlib import Path
import json
import pandas as pd
from datetime import datetime
import numpy as np
from random import sample

def normalize_filename(filename):
    return filename.replace('.md', '').strip().lower()


def generate_markdown_report(base_dir):
    """Generate a markdown format report from cached data"""
    base_dir = Path(base_dir)
    cache_dir = Path(__file__).parent / "cache"

    base_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d")
    report_file = base_dir / f"report_{timestamp}.md"

    # Load data files
    files_to_load = {
        'analysis': cache_dir / "analysis.json",
        'keywords': cache_dir / "keyword_data.json",
        'similarity': cache_dir / "similarity.csv",  # One-hot encoded data
        'similarity_correlation': cache_dir / "similarity_correlation.csv"  # Jaccard scores
    }

    analysis, keywords, similarity_df, one_hot_df = None, None, None, None

    # Load analysis data
    try:
        with open(files_to_load['analysis'], 'r') as f:
            analysis = json.load(f)
            print(f"Loaded analysis data from {files_to_load['analysis']}")
    except Exception as e:
        print(f"Error loading analysis: {str(e)}")

    # Load keyword data
    try:
        with open(files_to_load['keywords'], 'r') as f:
            keywords = json.load(f)
            print(f"Loaded keyword data from {files_to_load['keywords']}")
    except Exception as e:
        print(f"Error loading keywords: {str(e)}")

    # Load similarity data (one-hot encoded)
    try:
        similarity_df = pd.read_csv(
            files_to_load['similarity_correlation'], index_col=0)
        # Actual one-hot encoded token data
        one_hot_df = pd.read_csv(files_to_load['similarity'], index_col=0)

        print("\nSimilarity matrix loaded:")
        print(f"Jaccard Matrix Shape: {similarity_df.shape}")
        print("One-Hot Data Shape:", one_hot_df.shape)

        # Normalize filenames in both dataframes
        similarity_df.index = similarity_df.index.map(normalize_filename)
        one_hot_df.index = one_hot_df.index.map(normalize_filename)

    except Exception as e:
        print(f"Error loading similarity data: {str(e)}")
        similarity_df = None
        one_hot_df = None

    # Start building report content
    md_content = [
        "# ZettelTK Analysis Report\n",
        f"Generated on: {datetime.now().strftime('%B %d, %Y')}\n"
    ]

    # File Statistics
    if analysis and 'file_stats' in analysis:
        md_content.extend([
            "## File Statistics\n",
            f"- Total files: {analysis['file_stats']['total_files']}",
            f"- Total size: {analysis['file_stats']['total_size']} bytes",
            f"- Average file size: {analysis['file_stats']['avg_size']} bytes\n"
        ])

    # Text Statistics
    if analysis and 'text_stats' in analysis:
        md_content.extend([
            "## Text Statistics\n",
            f"- Unique tokens: {analysis['text_stats']['unique_tokens']}",
            f"- Average tokens per file: {analysis['text_stats']['avg_tokens_per_file']}",
            "\n### Sentiment Analysis"
        ] + [f"- {k.capitalize()}: {v:.2f}" for k, v in analysis['text_stats']['sentiment'].items()])

    # Keyword Analysis
    if keywords:
        md_content.append("\n## Keyword Analysis")
        for gram_type in ['trigrams', 'bigrams', 'unigrams']:
            md_content.append(f"### Top {gram_type.capitalize()}")
            items = keywords.get(gram_type, [])[:5]
            for item in items:
                content = item['word' if gram_type == 'unigrams' else 'phrase']
                md_content.append(f"- {content} ({item['count']} occurrences)")
            md_content.append("")

    # Document Similarity
    similarities = []
    if similarity_df is not None and one_hot_df is not None:
        print("\nCalculating document similarities...")
        files = similarity_df.index.tolist()

        for i in range(len(files)):
            for j in range(i + 1, len(files)):
                try:
                    file1, file2 = files[i], files[j]
                    similarity = similarity_df.iloc[i, j]

                    # Skip trivial/nonexistent relationships
                    if similarity <= 0.0 or np.isnan(similarity):
                        continue

                    # Get binary vectors from ONE-HOT DATA
                    doc1_vec = one_hot_df.iloc[i].astype(int)
                    doc2_vec = one_hot_df.iloc[j].astype(int)

                    # Find shared tokens (where both vectors == 1)
                    shared_mask = (doc1_vec == 1) & (doc2_vec == 1)
                    shared_tokens = doc1_vec.index[shared_mask].tolist()
                    shared_count = len(shared_tokens)

                    if shared_count > 0:
                        composite_score = shared_count * similarity

                        similarities.append({
                            'file1': file1,
                            'file2': file2,
                            'similarity': similarity,
                            'shared_token_count': shared_count,
                            'composite_score': composite_score,
                            'shared_tokens': shared_tokens
                        })

                except Exception as e:
                    print(
                        f"Error comparing documents {files[i]} and {files[j]}: {str(e)}")
                    continue

    print(f"Similarities count = {len(similarities)}")

    # When writing the similarity results, adjust the formatting:
    if similarities:
        md_content.append("\n## Document Similarity Analysis")
        md_content.append("### Top 10 Similar Documents (Composite Score)\n")

        # Sort by composite score and take top 10
        similarities.sort(key=lambda x: x['composite_score'], reverse=True)

        for i, pair in enumerate(similarities[:10], 1):
            # Add extra space padding for numbers 10 and above
            index_padding = " " if i >= 10 else ""
            md_content.extend([
                f"{i}.{index_padding}**{pair['file1']}** ↔ **{pair['file2']}**",
                f"   - Composite Score: {pair['composite_score']:.2f}",
                f"   - Jaccard Similarity: {pair['similarity']:.3f}",
                f"   - Shared Tokens: {pair['shared_token_count']}",
                "   - Sample Shared Topics:\n",
                *[f"     • {token}" for token in pair['shared_tokens'][:50]],
                ""
            ])
    else:
        md_content.extend([
            "\n## Document Similarity Analysis",
            "No significant similarities found between documents.\n"
        ])

    # Write final report
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_content))
        print(f"\nReport successfully generated at: {report_file}")
    except Exception as e:
        print(f"Failed to write report: {str(e)}")

    return report_file
