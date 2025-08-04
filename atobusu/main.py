"""
Main entry point for Atobusu application.
"""

import argparse
import sys
from pathlib import Path

from atobusu.core.config import AtobusuConfig
from atobusu.core.logging_config import setup_logging, get_logger
from atobusu.core.exceptions import AtobusuError, ConfigurationError


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description="Atobusu - Auto HTML Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  atobusu --version 1 --input data.json --template page.html
  atobusu --version 2 --gui
  atobusu --version 3 --gui --word-doc document.docx
        """
    )
    
    parser.add_argument(
        "--version", "-v",
        type=int,
        choices=[1, 2, 3],
        default=1,
        help="Atobusu version to run (1: CLI, 2: GUI, 3: GUI+Word)"
    )
    
    parser.add_argument(
        "--config", "-c",
        type=str,
        default="config/default.yaml",
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--input", "-i",
        type=str,
        help="Input data file (JSON or YAML)"
    )
    
    parser.add_argument(
        "--template", "-t",
        type=str,
        help="Template file to use"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file path"
    )
    
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch GUI interface (versions 2 and 3)"
    )
    
    parser.add_argument(
        "--word-doc",
        type=str,
        help="Word document to process (version 3 only)"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level"
    )
    
    return parser


def load_configuration(config_path: str) -> AtobusuConfig:
    """Load and validate configuration."""
    try:
        if Path(config_path).exists():
            config = AtobusuConfig.load_from_file(config_path)
        else:
            # Use default configuration
            config = AtobusuConfig()
        
        config.validate()
        return config
        
    except Exception as e:
        raise ConfigurationError(f"Failed to load configuration", str(e))


def main():
    """Main entry point."""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = load_configuration(args.config)
        
        # Override log level if specified
        if args.log_level:
            config.log_level = args.log_level
        
        # Setup logging
        logger = setup_logging(
            log_level=config.log_level,
            log_file=config.log_file
        )
        
        logger.info(f"Starting Atobusu version {args.version}")
        logger.info(f"Configuration loaded from: {args.config}")
        
        # Version-specific logic
        if args.version == 1:
            from atobusu.cli.version1 import run_version1_cli
            run_version1_cli(args, config, logger)
        elif args.version == 2:
            logger.info("Version 2 (GUI) - Implementation pending")
        elif args.version == 3:
            logger.info("Version 3 (GUI + Word) - Implementation pending")
        
        logger.info("Atobusu completed successfully")
        
    except AtobusuError as e:
        logger = get_logger()
        logger.error(f"Atobusu error: {e}")
        sys.exit(1)
    except Exception as e:
        logger = get_logger()
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()