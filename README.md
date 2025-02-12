# ZettelTK: Knowledge Analysis Toolkit

ZettelTK analyzes personal notes to generate insights through automated analysis and comprehensive reports. This tool processes your notes to identify relationships between documents, extract key information, and provide detailed analytics about your knowledge base.

## Setup and Usage

Clone the repository to your local machine:

```bash
git clone https://github.com/yourusername/zetteltk.git
cd zetteltk
```

Create a directory for your notes:

```bash
mkdir -p ./zetteltk/data
```

Place your note files in the `./zetteltk/data` directory. The project includes example files to demonstrate the expected format and structure of notes.

To use ZettelTK, run the CLI script:

```bash
python main.py
```

The interactive menu will present two options:

1. Generate New Analysis: Processes your notes and creates cached analysis files
2. Generate Reports: Creates a markdown report using the cached analysis

You must first run an analysis before generating reports. The analysis process examines your notes and creates necessary cache files that the report generator uses to create the final markdown report.

## Analysis Output

When you run an analysis, ZettelTK provides immediate feedback on the processing results:
- Total number of files processed
- Total size of analyzed content
- Number of unique tokens identified

The generated report includes comprehensive insights such as document similarity analysis, keyword extraction, and sentiment analysis of your notes. Reports are saved in markdown format for easy viewing and sharing.

## Project Structure

```
zetteltk/
├── data/          # Place your notes here
├── cache/         # Analysis files (auto-generated)
└── reports/       # Generated markdown reports
```

## Development Status

We are currently developing a question generation feature that will create relevant questions based on the analysis results and note contents.

## Contributing

We welcome contributions to enhance ZettelTK's capabilities. Please feel free to submit issues and pull requests through our repository.

## License

[GNU](https://www.gnu.org/licenses/gpl-3.0.en.html)
