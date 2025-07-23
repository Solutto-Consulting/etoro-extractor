"""
Main CLI module for eToro Extractor.
"""

import sys
import os
import click
from dotenv import load_dotenv

from .portfolio import get_portfolio
from .config import Config


@click.group()
@click.version_option(version="0.1.0")
@click.option('--debug', is_flag=True, help='Enable debug mode')
def cli(debug):
    """eToro Extractor - Extract data from eToro public profiles."""
    load_dotenv()
    
    if debug or os.getenv('DEBUG', 'False').lower() == 'true':
        click.echo("Debug mode enabled")
        os.environ['DEBUG'] = 'True'
        
        # Configure logging for debug mode
        import logging
        logging.basicConfig(level=logging.DEBUG)


@cli.command()
@click.option('--user', '-u', help='eToro username to extract portfolio from')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'csv']), 
              default='table', help='Output format')
@click.option('--save', '-s', help='Save results to file')
def portfolio(user, output, save):
    """Extract portfolio information from an eToro user's public profile."""
    
    config = Config()
    
    # Use provided user or default from config
    username = user or config.default_username
    
    if not username:
        click.echo(click.style("Error: No username provided. Use --user parameter or set ETORO_DEFAULT_USERNAME in .env", 
                              fg='red'), err=True)
        sys.exit(1)
    
    click.echo(f"Extracting portfolio for user: {click.style(username, fg='green')}")
    
    try:
        portfolio_data = get_portfolio(username, config)
        
        if not portfolio_data:
            click.echo(click.style("No portfolio data found or user profile is private", fg='yellow'))
            return
        
        # Display results based on output format
        if output == 'json':
            from .formatters import format_portfolio_json
            result = format_portfolio_json(portfolio_data)
            click.echo(result)
        elif output == 'csv':
            from .formatters import format_portfolio_csv
            result = format_portfolio_csv(portfolio_data)
            click.echo(result)
        else:  # table format (default)
            from .formatters import format_portfolio_table
            result = format_portfolio_table(portfolio_data)
            click.echo(result)
        
        # Save to file if requested
        if save:
            with open(save, 'w') as f:
                f.write(result)
            click.echo(f"Results saved to {click.style(save, fg='green')}")
            
    except Exception as e:
        click.echo(click.style(f"Error extracting portfolio: {str(e)}", fg='red'), err=True)
        if os.getenv('DEBUG') == 'True':
            import traceback
            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)
