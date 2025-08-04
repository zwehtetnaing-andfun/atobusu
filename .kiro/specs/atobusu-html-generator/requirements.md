# Requirements Document

## Introduction

Atobusu is a Python-based auto HTML program designed to generate HTML and PHP content from structured data inputs. The program will be developed in three progressive versions, each adding enhanced functionality and user interface capabilities. Version 1 focuses on file-based data processing, Version 2 introduces a GUI for data input, and Version 3 adds Word document integration with advanced file selection capabilities.

## Requirements

### Requirement 1

**User Story:** As a developer, I want to process JSON or YAML files to generate HTML and PHP content from multiple template types, so that I can automate content generation from structured data.

#### Acceptance Criteria

1. WHEN a JSON file is provided THEN the system SHALL parse the file and extract data for HTML generation
2. WHEN a YAML file is provided THEN the system SHALL parse the file and extract data for HTML generation
3. WHEN data is processed THEN the system SHALL generate HTML output using Jinja templating
4. WHEN data is processed THEN the system SHALL generate PHP output using Jinja templating
5. WHEN processing templates THEN the system SHALL handle multiple template types (page templates, index templates, content templates)
6. WHEN processing PHP templates THEN the system SHALL preserve PHP function calls and syntax while replacing template variables
7. IF the input file format is unsupported THEN the system SHALL display an appropriate error message

### Requirement 2

**User Story:** As a content creator, I want the system to automatically correct text formatting and convert special characters, so that my output is properly formatted for web display.

#### Acceptance Criteria

1. WHEN processing text content THEN the system SHALL convert straight quotes (") to curly quotes (")
2. WHEN encountering the symbol ※ THEN the system SHALL keep it unchanged
3. WHEN encountering circled numbers (①②③) THEN the system SHALL convert them to HTML entities (&#9312;&#9313;&#9314;)
4. WHEN encountering ◎ symbol THEN the system SHALL convert it to HTML entity &#9678;
5. WHEN encountering ハート symbol THEN the system SHALL convert it to HTML entity &#9825;
6. WHEN encountering ♪ symbol THEN the system SHALL convert it to HTML entity &#9834;
7. WHEN processing Japanese text THEN the system SHALL properly handle character encoding and conversion
8. WHEN processing date placeholders THEN the system SHALL replace them with actual date values from input data

### Requirement 3

**User Story:** As a user, I want a graphical interface to input data directly, so that I can generate content without manually creating JSON or YAML files.

#### Acceptance Criteria

1. WHEN Version 2 is launched THEN the system SHALL display a GUI using Tkinter or PyQt5
2. WHEN user inputs data through the GUI THEN the system SHALL convert the input to JSON format
3. WHEN JSON is generated from GUI input THEN the system SHALL process it using Version 1 logic
4. WHEN processing is complete THEN the system SHALL generate HTML and PHP files based on user input
5. IF user input is invalid THEN the system SHALL display validation error messages in the GUI

### Requirement 4

**User Story:** As a content manager, I want to select Word documents through the GUI and have them processed along with my input data, so that I can integrate existing document content into my generated output.

#### Acceptance Criteria

1. WHEN Version 3 is launched THEN the system SHALL provide a file selection dialog for Word documents
2. WHEN a Word file is selected THEN the system SHALL read and extract content from the document
3. WHEN Word content is extracted THEN the system SHALL combine it with GUI input data
4. WHEN combined data is processed THEN the system SHALL generate YAML or JSON output
5. WHEN YAML or JSON is generated THEN the system SHALL process it using established Version 1 logic
6. IF the selected Word file cannot be read THEN the system SHALL display an appropriate error message

### Requirement 5

**User Story:** As a developer, I want the system to have a modular architecture across all versions, so that functionality can be reused and maintained efficiently.

#### Acceptance Criteria

1. WHEN implementing any version THEN the system SHALL use Jinja for all templating operations
2. WHEN handling data formats THEN the system SHALL use appropriate YAML and JSON libraries
3. WHEN implementing text processing THEN the system SHALL use a centralized character conversion module
4. WHEN building the GUI THEN the system SHALL choose between Tkinter or PyQt5 based on requirements
5. WHEN reading Word files THEN the system SHALL use a dedicated Word file reader library
6. WHEN processing templates THEN the system SHALL support multiple template formats (HTML, PHP, mixed content)
7. WHEN handling PHP templates THEN the system SHALL preserve PHP syntax while enabling Jinja variable replacement

### Requirement 6

**User Story:** As a template designer, I want the system to handle various placeholder patterns and variable substitutions, so that I can create flexible templates with dynamic content.

#### Acceptance Criteria

1. WHEN processing templates with product code placeholders THEN the system SHALL replace them with actual product codes from input data
2. WHEN encountering date placeholders (2025/00/00, '25/00/00) THEN the system SHALL replace them with formatted dates from input data
3. WHEN processing PHP function calls with placeholders THEN the system SHALL replace placeholder parameters while preserving PHP syntax
4. WHEN handling mixed PHP and HTML templates THEN the system SHALL process both template languages correctly
5. WHEN template variables are missing from input data THEN the system SHALL provide default values or clear error messages

### Requirement 7

**User Story:** As a user, I want clear feedback and error handling throughout the application, so that I can understand what's happening and resolve any issues.

#### Acceptance Criteria

1. WHEN any error occurs THEN the system SHALL provide clear, user-friendly error messages
2. WHEN processing files THEN the system SHALL show progress indicators where appropriate
3. WHEN generation is complete THEN the system SHALL confirm successful output creation
4. WHEN invalid input is detected THEN the system SHALL highlight the specific issue and suggest corrections
5. IF system resources are insufficient THEN the system SHALL gracefully handle the situation and inform the user