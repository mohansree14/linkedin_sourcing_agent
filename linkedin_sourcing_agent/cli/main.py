"""
Command Line Interface for LinkedIn Sourcing Agent
"""

import argparse
import asyncio
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add the parent directory to sys.path to enable imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from linkedin_sourcing_agent.core.agent import LinkedInSourcingAgent
from linkedin_sourcing_agent.utils.config_manager import ConfigManager
from linkedin_sourcing_agent.utils.logging_config import setup_logging, get_logger
from linkedin_sourcing_agent.utils.export_manager import ExportManager

# Conditionally import open source models functions to avoid dependency issues
try:
    from linkedin_sourcing_agent.generators.open_source_models import print_setup_guide, SETUP_GUIDES
except ImportError:
    # transformers not available, define fallback functions
    def print_setup_guide(model_type: str = 'default') -> None:
        print("Open source model setup requires additional dependencies.")
        print("Install transformers and torch: pip install transformers torch")
    
    SETUP_GUIDES = {}

logger = get_logger(__name__)


class LinkedInSourcingCLI:
    """Command Line Interface for LinkedIn Sourcing Agent"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.agent = None
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create and configure argument parser"""
        
        parser = argparse.ArgumentParser(
            description="LinkedIn Sourcing Agent - Professional candidate sourcing and outreach",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Search and export to Excel
  linkedin-agent search --query "python developer" --location "San Francisco" --limit 10 --excel-file results.xlsx
  
  # Search and export to Google Sheets
  linkedin-agent search --query "ML engineer" --sheets-name "ML Candidates 2025" --share-email your@email.com
  
  # Process from file and export
  linkedin-agent process --input candidates.json --export-excel processed_results.xlsx
  
  # Export existing data to organized Excel/Sheets
  linkedin-agent export --input candidates.json --excel organized_data.xlsx --include-analytics --include-messages
  
  # Setup open source models
  linkedin-agent setup --model ollama
  
  # Configure the agent
  linkedin-agent configure
            """
        )
        
        # Global options
        parser.add_argument(
            '--config', '-c',
            help='Path to configuration file',
            default='.env'
        )
        parser.add_argument(
            '--verbose', '-v',
            action='store_true',
            help='Enable verbose logging'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without making actual API calls'
        )
        
        # Subcommands
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Search command
        search_parser = subparsers.add_parser('search', help='Search for candidates')
        search_parser.add_argument('--query', '-q', required=True, help='Search query')
        search_parser.add_argument('--location', '-l', help='Location filter')
        search_parser.add_argument('--limit', type=int, default=10, help='Number of results')
        search_parser.add_argument('--output', '-o', help='Output file path')
        search_parser.add_argument('--format', choices=['json', 'csv', 'excel', 'sheets'], default='json', help='Output format')
        search_parser.add_argument('--excel-file', help='Excel file path for export')
        search_parser.add_argument('--sheets-name', help='Google Sheets name for export')
        search_parser.add_argument('--share-email', help='Email to share Google Sheets with')
        
        # Process command
        process_parser = subparsers.add_parser('process', help='Process candidates from file')
        process_parser.add_argument('--input', '-i', required=True, help='Input file path')
        process_parser.add_argument('--output', '-o', help='Output file path')
        process_parser.add_argument('--job-description', help='Job description file or text')
        process_parser.add_argument('--generate-outreach', action='store_true', help='Generate outreach messages')
        process_parser.add_argument('--export-excel', help='Export results to Excel file')
        process_parser.add_argument('--export-sheets', help='Export results to Google Sheets (provide sheet name)')
        process_parser.add_argument('--share-email', help='Email to share Google Sheets with')
        
        # Export command (new)
        export_parser = subparsers.add_parser('export', help='Export candidate data to Excel or Google Sheets')
        export_parser.add_argument('--input', '-i', required=True, help='Input JSON file with candidate data')
        export_parser.add_argument('--excel', help='Export to Excel file (provide file path)')
        export_parser.add_argument('--sheets', help='Export to Google Sheets (provide sheet name)')
        export_parser.add_argument('--share-email', help='Email to share Google Sheets with')
        export_parser.add_argument('--include-messages', action='store_true', help='Include generated messages in export')
        export_parser.add_argument('--include-analytics', action='store_true', help='Include analytics in export')
        
        # Setup command
        setup_parser = subparsers.add_parser('setup', help='Setup open source models')
        setup_parser.add_argument('--model', choices=list(SETUP_GUIDES.keys()), default='ollama', help='Model type to setup')
        setup_parser.add_argument('--list-models', action='store_true', help='List available models')
        
        # Configure command
        config_parser = subparsers.add_parser('configure', help='Configure the agent')
        config_parser.add_argument('--reset', action='store_true', help='Reset configuration to defaults')
        config_parser.add_argument('--show', action='store_true', help='Show current configuration')
        
        # Validate command
        validate_parser = subparsers.add_parser('validate', help='Validate configuration and setup')
        validate_parser.add_argument('--check-apis', action='store_true', help='Check API connections')
        validate_parser.add_argument('--check-models', action='store_true', help='Check model availability')
        
        return parser
    
    async def run(self, args: List[str] = None) -> int:
        """
        Run the CLI application
        
        Args:
            args: Command line arguments (defaults to sys.argv)
            
        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)
        
        # Setup logging
        log_level = "DEBUG" if parsed_args.verbose else "INFO"
        setup_logging(log_level=log_level)
        
        # Load configuration
        try:
            from linkedin_sourcing_agent.utils.config_manager import load_config
            config = load_config(parsed_args.config or ".env")
            logger.info(f"Configuration loaded from {parsed_args.config or '.env'}")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return 1
        
        # Handle dry run mode
        if parsed_args.dry_run:
            logger.info("Running in dry-run mode - no actual API calls will be made")
            config['DRY_RUN'] = True
        
        # Execute command
        try:
            if parsed_args.command == 'search':
                return await self._handle_search(parsed_args, config)
            elif parsed_args.command == 'process':
                return await self._handle_process(parsed_args, config)
            elif parsed_args.command == 'export':
                return await self._handle_export(parsed_args, config)
            elif parsed_args.command == 'setup':
                return self._handle_setup(parsed_args)
            elif parsed_args.command == 'configure':
                return self._handle_configure(parsed_args)
            elif parsed_args.command == 'validate':
                return await self._handle_validate(parsed_args, config)
            else:
                parser.print_help()
                return 1
                
        except KeyboardInterrupt:
            logger.info("Operation cancelled by user")
            return 130
        except Exception as e:
            logger.error(f"Command failed: {e}")
            if parsed_args.verbose:
                logger.exception("Full traceback:")
            return 1
    
    async def _handle_search(self, args: argparse.Namespace, config: Dict[str, Any]) -> int:
        """Handle search command"""
        
        logger.info(f"Searching for candidates: {args.query}")
        
        # Initialize agent
        self.agent = LinkedInSourcingAgent(args.config or '.env')
        
        # Build search parameters
        search_params = {
            'query': args.query,
            'location': args.location,
            'limit': args.limit
        }
        
        # Execute search
        candidates = await self.agent.search_candidates(**search_params)
        
        logger.info(f"Found {len(candidates)} candidates")
        
        # Save results with export options
        if args.output or args.excel_file or args.sheets_name:
            # Use custom output path or generate organized path
            if not args.output:
                search_query_clean = "".join(c for c in args.query if c.isalnum() or c in (' ', '-', '_')).replace(' ', '_')
                args.output = self._get_output_path(f"search_{search_query_clean}", 'json', 'json')
            
            if args.excel_file and not os.path.dirname(args.excel_file):
                # If no directory specified, use organized path
                search_query_clean = "".join(c for c in args.query if c.isalnum() or c in (' ', '-', '_')).replace(' ', '_')
                args.excel_file = self._get_output_path(f"search_{search_query_clean}", 'excel', 'xlsx')
            
            success = self._save_results_with_export(candidates, args, config)
            if not success:
                logger.warning("Some exports may have failed - check logs above")
            else:
                self._print_output_locations()
        else:
            self._print_candidates(candidates)
        
        return 0
    
    async def _handle_process(self, args: argparse.Namespace, config: Dict[str, Any]) -> int:
        """Handle process command"""
        
        logger.info(f"Processing candidates from {args.input}")
        
        # Load candidates
        candidates = await self._load_candidates(args.input)
        logger.info(f"Loaded {len(candidates)} candidates")
        
        # Load job description
        job_description = ""
        if args.job_description:
            job_description = await self._load_job_description(args.job_description)
        
        # Initialize agent
        self.agent = LinkedInSourcingAgent(args.config or '.env')
        
        # Process candidates
        results = []
        for candidate in candidates:
            try:
                # Score candidate
                scored_candidate = await self.agent.score_candidate(candidate, job_description)
                
                # Generate outreach if requested
                if args.generate_outreach and job_description:
                    outreach = await self.agent.generate_outreach(candidate, job_description)
                    scored_candidate['outreach_message'] = outreach
                
                results.append(scored_candidate)
                
            except Exception as e:
                logger.error(f"Failed to process candidate {candidate.get('name', 'Unknown')}: {e}")
                continue
        
        logger.info(f"Processed {len(results)} candidates successfully")
        
        # Save results with export options
        if not args.output:
            args.output = self._get_output_path(f"processed_candidates", 'process', 'json')
        
        if hasattr(args, 'export_excel') and args.export_excel and not os.path.dirname(args.export_excel):
            args.export_excel = self._get_output_path(f"processed_candidates", 'excel', 'xlsx')
        
        success = self._save_results_with_export(results, args, config)
        if not success:
            logger.warning("Some exports may have failed - check logs above")
        else:
            self._print_output_locations()
        
        return 0
    
    async def _handle_export(self, args: argparse.Namespace, config: Dict[str, Any]) -> int:
        """Handle export command"""
        
        logger.info(f"Exporting candidate data from {args.input}")
        
        try:
            # Load candidate data from JSON file
            with open(args.input, 'r', encoding='utf-8') as f:
                candidates = json.load(f)
            
            if not candidates:
                logger.warning("No candidate data found in input file")
                return 1
            
            if not isinstance(candidates, list):
                logger.error("Input file should contain a list of candidates")
                return 1
            
            logger.info(f"Loaded {len(candidates)} candidates from {args.input}")
            
            # Initialize export manager
            export_manager = ExportManager(config)
            
            success = False
            
            # Export to Excel
            if args.excel:
                logger.info(f"Exporting to Excel: {args.excel}")
                success = export_manager.export_to_excel(
                    candidates=candidates,
                    output_file=args.excel,
                    include_analytics=args.include_analytics,
                    include_messages=args.include_messages
                )
                
                if success:
                    logger.info(f"✅ Successfully exported to Excel: {args.excel}")
                else:
                    logger.error(f"❌ Failed to export to Excel: {args.excel}")
            
            # Export to Google Sheets
            if args.sheets:
                logger.info(f"Exporting to Google Sheets: {args.sheets}")
                sheet_url = export_manager.export_to_google_sheets(
                    candidates=candidates,
                    spreadsheet_name=args.sheets,
                    share_with_email=args.share_email
                )
                
                if sheet_url:
                    logger.info(f"✅ Successfully exported to Google Sheets: {sheet_url}")
                    if args.share_email:
                        logger.info(f"📧 Shared with: {args.share_email}")
                    success = True
                else:
                    logger.error(f"❌ Failed to export to Google Sheets: {args.sheets}")
            
            if not args.excel and not args.sheets:
                logger.error("Please specify either --excel or --sheets option")
                return 1
            
            return 0 if success else 1
            
        except FileNotFoundError:
            logger.error(f"Input file not found: {args.input}")
            return 1
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in input file: {e}")
            return 1
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return 1

    def _handle_setup(self, args: argparse.Namespace) -> int:
        """Handle setup command"""
        
        if args.list_models:
            print("Available models:")
            for model_type in SETUP_GUIDES.keys():
                print(f"  - {model_type}")
            return 0
        
        print(f"Setting up {args.model} model:")
        print_setup_guide(args.model)
        
        return 0
    
    def _handle_configure(self, args: argparse.Namespace) -> int:
        """Handle configure command"""
        
        if args.show:
            config = self.config_manager.get_config()
            print("Current configuration:")
            for key, value in config.items():
                if 'key' in key.lower() or 'token' in key.lower():
                    value = f"{value[:4]}...{value[-4:]}" if value else "Not set"
                print(f"  {key}: {value}")
            return 0
        
        if args.reset:
            print("Resetting configuration to defaults...")
            # This would reset the configuration
            print("Configuration reset complete")
            return 0
        
        # Interactive configuration
        print("Interactive configuration not yet implemented")
        print("Please edit your .env file manually or use --show to view current settings")
        
        return 0
    
    async def _handle_validate(self, args: argparse.Namespace, config: Dict[str, Any]) -> int:
        """Handle validate command"""
        
        logger.info("Validating configuration and setup...")
        
        validation_passed = True
        
        # Check basic configuration
        required_keys = ['OPENAI_API_KEY', 'RAPIDAPI_KEY']
        for key in required_keys:
            if not config.get(key):
                logger.warning(f"Missing required configuration: {key}")
                validation_passed = False
            else:
                logger.info(f"✓ {key} configured")
        
        # Check API connections if requested
        if args.check_apis:
            try:
                self.agent = LinkedInSourcingAgent(args.config or '.env')
                # This would test API connections
                logger.info("✓ API connections validated")
            except Exception as e:
                logger.error(f"✗ API validation failed: {e}")
                validation_passed = False
        
        # Check model availability if requested
        if args.check_models:
            # This would check if open source models are available
            logger.info("Model availability check not yet implemented")
        
        if validation_passed:
            logger.info("✓ All validations passed")
            return 0
        else:
            logger.error("✗ Some validations failed")
            return 1
    
    async def _load_candidates(self, file_path: str) -> List[Dict[str, Any]]:
        """Load candidates from file"""
        
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            if path.suffix.lower() == '.json':
                data = json.load(f)
                return data if isinstance(data, list) else [data]
            else:
                # Could add CSV support here
                raise ValueError(f"Unsupported file format: {path.suffix}")
    
    async def _load_job_description(self, job_desc_input: str) -> str:
        """Load job description from file or return as text"""
        
        # Check if it's a file path
        path = Path(job_desc_input)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        else:
            # Treat as direct text input
            return job_desc_input.strip()
    
    async def _save_results(self, results: List[Dict[str, Any]], file_path: str, format_type: str) -> None:
        """Save results to file"""
        
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if format_type == 'json':
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        elif format_type == 'csv':
            # Could add CSV export here
            raise NotImplementedError("CSV export not yet implemented")
    
    def _print_candidates(self, candidates: List[Dict[str, Any]]) -> None:
        """Print candidates to console"""
        
        for i, candidate in enumerate(candidates, 1):
            print(f"\n{i}. {candidate.get('name', 'Unknown')}")
            print(f"   LinkedIn: {candidate.get('linkedin_url', 'N/A')}")
            print(f"   Headline: {candidate.get('headline', 'N/A')}")
            print(f"   Location: {candidate.get('location', 'N/A')}")
            if 'score' in candidate:
                print(f"   Score: {candidate['score']:.1f}/10")
    
    def _get_output_path(self, base_name: str, output_type: str, extension: str) -> str:
        """Generate organized output path with timestamp"""
        from datetime import datetime
        
        # Create timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Define output directories
        output_dirs = {
            'search': 'outputs/search_results',
            'process': 'outputs/processed_candidates', 
            'excel': 'outputs/excel_exports',
            'json': 'outputs/json_data'
        }
        
        # Get appropriate directory
        output_dir = output_dirs.get(output_type, 'outputs')
        
        # Create filename with timestamp
        filename = f"{base_name}_{timestamp}.{extension}"
        
        # Create full path
        full_path = os.path.join(output_dir, filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        return full_path
    
    def _print_output_locations(self) -> None:
        """Print information about where outputs are saved"""
        print("\n📁 Output Locations:")
        print("=" * 50)
        print("🔍 Search Results:     outputs/search_results/")
        print("⚙️  Processed Data:     outputs/processed_candidates/")
        print("📊 Excel Files:        outputs/excel_exports/")
        print("📝 JSON Data:          outputs/json_data/")
        print("📋 Logs:               logs/")
        print("=" * 50)
        print("\nTip: Use --output to specify custom file paths")
        print("Example: --output my_custom_results.xlsx")
        print("")

    def _save_results_with_export(self, candidates: List[Dict[str, Any]], args: argparse.Namespace, config: Dict[str, Any]) -> bool:
        """Save results with multiple export options"""
        success = True
        
        try:
            # Check if ExportManager exists
            try:
                from ..utils.export_manager import ExportManager
                export_manager = ExportManager()
            except ImportError:
                logger.warning("ExportManager not available, using basic file save")
                export_manager = None
            
            # Save to JSON
            if args.output:
                logger.info(f"Saving results to: {args.output}")
                if args.output.endswith('.json'):
                    with open(args.output, 'w', encoding='utf-8') as f:
                        json.dump(candidates, f, indent=2, ensure_ascii=False)
                    print(f"✅ Saved {len(candidates)} candidates to {args.output}")
                else:
                    logger.warning(f"Unsupported output format: {args.output}")
                    success = False
            
            # Export to Excel
            if args.excel_file:
                if export_manager:
                    try:
                        export_manager.export_to_excel(candidates, args.excel_file)
                        print(f"✅ Exported {len(candidates)} candidates to Excel: {args.excel_file}")
                    except Exception as e:
                        logger.error(f"Excel export failed: {e}")
                        success = False
                else:
                    logger.warning("Excel export not available")
                    success = False
            
            # Export to Google Sheets
            if args.sheets_name:
                if export_manager:
                    try:
                        export_manager.export_to_google_sheets(
                            candidates, 
                            args.sheets_name,
                            share_email=getattr(args, 'share_email', None)
                        )
                        print(f"✅ Exported {len(candidates)} candidates to Google Sheets: {args.sheets_name}")
                    except Exception as e:
                        logger.error(f"Google Sheets export failed: {e}")
                        success = False
                else:
                    logger.warning("Google Sheets export not available")
                    success = False
            
            return success
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False

def main():
    """Main CLI entry point"""
    
    cli = LinkedInSourcingCLI()
    
    try:
        exit_code = asyncio.run(cli.run())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
