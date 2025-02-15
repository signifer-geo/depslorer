# Python Unused Dependencies Finder

Scans your Python virtual environment to find and optionally remove unused packages.

## Installation
```bash
git clone [repository-url]
cd unused-deps
pip install -r requirements.txt
```

## Usage
Run inside your virtual environment:
```bash
# List unused packages
python cli.py

# Detailed output
python cli.py -v

# Remove unused packages
python cli.py --uninstall

# Check specific locations
python cli.py -f src/main.py src/utils/
```

## Options
- `-v, --verbose`: Show detailed output
- `-f, --files`: Specify files/directories to analyze
- `-r, --recursive`: Search directories recursively (default: True)
- `-u, --uninstall`: Remove unused packages

## Example Output
```
Found unused packages:
  - beautifulsoup4
  - numpy
  - pandas
  - yfinance
```

## Limitations
- Reports indirect dependencies
- Doesn't detect dynamic imports
- Some packages may be needed without imports
- May not detect editable installs

## License
MIT License
