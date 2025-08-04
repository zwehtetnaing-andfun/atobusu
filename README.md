# Atobusu - Auto HTML Generator

Atobusu is a Python-based auto HTML program designed to generate HTML and PHP content from structured data inputs. The program supports three progressive versions with enhanced functionality and user interface capabilities.

## Features

- **Version 1**: File-based data processing (JSON/YAML → HTML/PHP)
- **Version 2**: GUI interface for data input
- **Version 3**: GUI + Word document integration

### Character Conversion
- Automatic quote conversion (" → ")
- Circled numbers to HTML entities (① → &#9312;)
- Special symbol conversion (◎ → &#9678;, ハート → &#9825;, ♪ → &#9834;)
- Japanese character encoding support

### Template Processing
- Multiple template types (page, index, content)
- PHP function preservation
- Date placeholder processing
- Product code handling

## Installation

```bash
pip install -r requirements.txt
```

For PyQt5 GUI support:
```bash
pip install -r requirements.txt[pyqt5]
```

## Usage

### Version 1 (Command Line)
```bash
python -m atobusu --version 1 --input data.json --template page.html --output result.html
```

### Version 2 (GUI)
```bash
python -m atobusu --version 2 --gui
```

### Version 3 (GUI + Word Document)
```bash
python -m atobusu --version 3 --gui --word-doc document.docx
```

## Configuration

Configuration can be customized via YAML or JSON files. See `config/default.yaml` for available options.

## Project Structure

```
atobusu/
├── atobusu/
│   ├── core/           # Data processing engine
│   ├── templates/      # Template management
│   ├── gui/           # GUI components
│   ├── file_handlers/ # File I/O operations
│   └── main.py        # Main entry point
├── config/            # Configuration files
├── templates/         # Template files
├── output/           # Generated output
└── requirements.txt  # Dependencies
```

## Development Status

This project is currently under development. Implementation progress:

- [x] Project structure and configuration
- [ ] Character conversion system
- [ ] Data processing engine
- [ ] Template management
- [ ] File I/O operations
- [ ] Version 1 CLI interface
- [ ] GUI framework
- [ ] Version 2 GUI
- [ ] Word document processing
- [ ] Version 3 integrated application

## License

MIT License - see LICENSE file for details.