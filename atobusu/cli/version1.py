"""
Version 1 CLI implementation for Atobusu application.

Provides command-line interface for processing data files through templates
and generating HTML, PHP, and mixed content output files.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

from atobusu.core.config import AtobusuConfig
from atobusu.core.data_processor import DataProcessor
from atobusu.core.data_models import InputData, ProcessedData, TemplateData
from atobusu.templates.template_manager import TemplateManager
from atobusu.templates.placeholder_processor import PlaceholderProcessor
from atobusu.file_handlers.output_writer import OutputWriter
from atobusu.core.exceptions import AtobusuError, InputError, ProcessingError, OutputError


def validate_cli_arguments(args, logger) -> Dict[str, Any]:
    """
    Validate command-line arguments for Version 1.
    
    Args:
        args: Parsed command-line arguments
        logger: Logger instance
        
    Returns:
        Dictionary with validation results
        
    Raises:
        InputError: If validation fails
    """
    validation = {
        'input_file': None,
        'template_file': None,
        'output_file': None,
        'errors': []
    }
    
    try:
        # Validate input file
        if not args.input:
            validation['errors'].append("Input file is required for Version 1")
        else:
            input_path = Path(args.input)
            if not input_path.exists():
                validation['errors'].append(f"Input file does not exist: {args.input}")
            elif not input_path.is_file():
                validation['errors'].append(f"Input path is not a file: {args.input}")
            elif input_path.suffix.lower() not in ['.json', '.yaml', '.yml']:
                validation['errors'].append(f"Input file must be JSON or YAML: {args.input}")
            else:
                validation['input_file'] = str(input_path.resolve())
        
        # Validate template file (optional - can use default)
        if args.template:
            template_path = Path(args.template)
            if not template_path.exists():
                validation['errors'].append(f"Template file does not exist: {args.template}")
            elif not template_path.is_file():
                validation['errors'].append(f"Template path is not a file: {args.template}")
            else:
                # Store just the template name if it's in the templates directory
                if template_path.parent.name == 'templates':
                    validation['template_file'] = template_path.name
                else:
                    validation['template_file'] = str(template_path.resolve())
        
        # Set output file (optional - will generate default if not provided)
        if args.output:
            validation['output_file'] = args.output
        
        # Log validation results
        if validation['errors']:
            for error in validation['errors']:
                logger.error(f"Validation error: {error}")
        else:
            logger.info("CLI arguments validated successfully")
            logger.debug(f"Input file: {validation['input_file']}")
            logger.debug(f"Template file: {validation['template_file']}")
            logger.debug(f"Output file: {validation['output_file']}")
        
        return validation
        
    except Exception as e:
        raise InputError("Failed to validate CLI arguments", str(e))


def determine_template_and_output(input_data: TemplateData, template_file: Optional[str], 
                                output_file: Optional[str], logger) -> Dict[str, str]:
    """
    Determine template and output files based on input data and arguments.
    
    Args:
        input_data: Processed template data
        template_file: Specified template file (optional)
        output_file: Specified output file (optional)
        logger: Logger instance
        
    Returns:
        Dictionary with template and output file paths
    """
    result = {
        'template_file': template_file,
        'output_file': output_file
    }
    
    try:
        # Determine template file
        if not template_file:
            # Use default template based on template type
            template_type = getattr(input_data, 'template_type', 'page')
            template_mapping = {
                'page': 'base_page.html',
                'index': 'base_index.html',
                'php': 'base_php.php',
                'mixed': 'mixed_content.html'
            }
            
            default_template = template_mapping.get(template_type, 'base_page.html')
            
            # Check if default template exists
            if Path(f"templates/{default_template}").exists():
                result['template_file'] = default_template
                logger.info(f"Using default template: {default_template}")
            else:
                # Fallback to any available template
                for template_name in template_mapping.values():
                    if Path(f"templates/{template_name}").exists():
                        result['template_file'] = template_name
                        logger.info(f"Using fallback template: {template_name}")
                        break
        
        # Determine output file
        if not output_file:
            # Generate output filename based on input and template
            input_stem = Path(input_data.source_file).stem if hasattr(input_data, 'source_file') else 'output'
            
            # Determine extension based on template type
            template_type = getattr(input_data, 'template_type', 'page')
            extension_mapping = {
                'page': '.html',
                'index': '.html',
                'php': '.php',
                'mixed': '.html'
            }
            
            extension = extension_mapping.get(template_type, '.html')
            result['output_file'] = f"output/{input_stem}{extension}"
            logger.info(f"Generated output file: {result['output_file']}")
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to determine template and output files: {e}")
        # Return defaults
        return {
            'template_file': result['template_file'] or 'templates/base_page.html',
            'output_file': result['output_file'] or 'output/generated.html'
        }


def run_version1_cli(args, config: AtobusuConfig, logger):
    """
    Run Version 1 CLI processing workflow.
    
    Args:
        args: Parsed command-line arguments
        config: Application configuration
        logger: Logger instance
        
    Raises:
        AtobusuError: If processing fails
    """
    try:
        logger.info("Starting Version 1 CLI processing")
        
        # Validate arguments
        validation = validate_cli_arguments(args, logger)
        if validation['errors']:
            raise InputError("CLI argument validation failed", "; ".join(validation['errors']))
        
        # Initialize components
        logger.info("Initializing processing components")
        
        data_processor = DataProcessor()
        placeholder_processor = PlaceholderProcessor()
        template_manager = TemplateManager(template_dir="templates", placeholder_processor=placeholder_processor)
        output_writer = OutputWriter(output_dir="output", create_dirs=True)
        
        # Step 1: Load and process input data
        logger.info(f"Loading input data from: {validation['input_file']}")
        
        input_data = data_processor.parse_file(validation['input_file'])
        parsed_data = input_data.metadata.get('parsed_data', {})
        data_items = parsed_data.get('data', [])
        logger.info(f"Loaded input data with {len(data_items)} items")
        
        # Step 2: Process data through character conversion and validation
        logger.info("Processing data through character conversion")
        
        processed_data = data_processor.process_data(input_data)
        logger.info("Data processing completed successfully")
        
        # Step 3: Convert to template data
        logger.info("Converting to template data format")
        
        # Extract template data from processed data or create from parsed data
        if processed_data.template_data:
            template_data = processed_data.template_data
        else:
            # Create template data from the parsed data
            template_data = data_processor.create_template_data_from_dict(parsed_data)
        
        logger.info("Template data conversion completed")
        
        # Step 4: Determine template and output files
        file_config = determine_template_and_output(
            template_data, 
            validation['template_file'], 
            validation['output_file'], 
            logger
        )
        
        # Step 5: Load and process template
        template_name = file_config['template_file']
        
        # Handle both template names and full paths
        if template_name and Path(template_name).is_absolute():
            # Full path provided - extract just the name for template manager
            template_path = Path(template_name)
            if template_path.parent.name == 'templates':
                template_name = template_path.name
            else:
                raise ProcessingError(f"Template must be in templates directory: {template_name}")
        
        if not template_name or not Path(f"templates/{template_name}").exists():
            raise ProcessingError(f"Template file not found: templates/{template_name}")
        
        logger.info(f"Loading template: {template_name}")
        
        # Determine template type based on file extension and content
        if template_name.endswith('.php'):
            template_type = 'php'
        elif 'mixed' in template_name.lower():
            template_type = 'mixed'
        else:
            template_type = 'html'
        
        # Step 6: Prepare template variables
        logger.info("Preparing template variables")
        
        # Combine template data with parsed data for comprehensive variable access
        template_vars = {}
        
        # Add template data fields
        if template_data:
            template_vars.update(template_data.to_placeholder_dict())
        
        # Add all parsed data fields directly
        template_vars.update(parsed_data)
        
        # Ensure we have the converted content
        template_vars['content'] = processed_data.converted_content
        
        logger.info("Template variables prepared")
        
        # Step 7: Render template
        logger.info(f"Rendering {template_type} template")
        
        # Load template directly and render with Jinja2 only
        template = template_manager.load_template(template_name)
        rendered_content = template.render(**template_vars)
        
        logger.info("Template rendering completed")
        
        # Step 8: Write output file
        logger.info(f"Writing output to: {file_config['output_file']}")
        
        # Determine output format based on template type and file extension
        output_path = Path(file_config['output_file'])
        if template_type == 'php' or output_path.suffix.lower() == '.php':
            success = output_writer.write_php(rendered_content, file_config['output_file'])
        elif template_type == 'mixed':
            success = output_writer.write_mixed_template(
                rendered_content, 
                file_config['output_file'], 
                template_type
            )
        else:
            success = output_writer.write_html(rendered_content, file_config['output_file'])
        
        if not success:
            raise OutputError(f"Failed to write output file: {file_config['output_file']}")
        
        # Step 9: Report results
        stats = output_writer.get_write_stats()
        logger.info("Version 1 CLI processing completed successfully")
        logger.info(f"Output file: {file_config['output_file']}")
        logger.info(f"Files written: {stats['files_written']}")
        logger.info(f"Total bytes: {stats['total_bytes']}")
        
        # Print success message to console
        print(f"✅ Processing completed successfully!")
        print(f"📁 Input file: {validation['input_file']}")
        print(f"📄 Template: templates/{template_name}")
        print(f"📝 Output file: {file_config['output_file']}")
        print(f"📊 Data items processed: {len(data_items)}")
        
    except AtobusuError as e:
        logger.error(f"Version 1 CLI processing failed: {e}")
        print(f"❌ Processing failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error in Version 1 CLI: {e}")
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


def print_version1_help():
    """Print help information for Version 1 CLI."""
    help_text = """
Atobusu Version 1 - Command Line Interface

USAGE:
    atobusu --version 1 --input <data_file> [OPTIONS]

REQUIRED ARGUMENTS:
    --input, -i <file>      Input data file (JSON or YAML format)

OPTIONAL ARGUMENTS:
    --template, -t <file>   Template file to use (HTML, PHP, or mixed)
                           If not specified, uses default template based on data
    
    --output, -o <file>     Output file path
                           If not specified, generates based on input filename
    
    --config, -c <file>     Configuration file (default: config/default.yaml)
    
    --log-level <level>     Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

EXAMPLES:
    # Basic usage with JSON input
    atobusu --version 1 --input data.json
    
    # Specify template and output
    atobusu --version 1 --input data.yaml --template custom.html --output result.html
    
    # Use PHP template
    atobusu --version 1 --input data.json --template page.php --output page.php
    
    # Enable debug logging
    atobusu --version 1 --input data.json --log-level DEBUG

SUPPORTED INPUT FORMATS:
    - JSON (.json)
    - YAML (.yaml, .yml)

SUPPORTED TEMPLATE TYPES:
    - HTML templates (.html, .htm)
    - PHP templates (.php)
    - Mixed content templates (HTML with PHP)

OUTPUT FORMATS:
    - HTML files (.html)
    - PHP files (.php)
    - Mixed content files

For more information, see the documentation or run with --help.
"""
    print(help_text)