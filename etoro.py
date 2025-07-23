#!/usr/bin/env python3
"""
eToro Extractor CLI - Command Line Interface

A Python CLI application for extracting data from eToro public profiles.
"""

import sys
import os
import click
from dotenv import load_dotenv

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from etoro_extractor.portfolio import get_portfolio
from etoro_extractor.config import Config


@click.group()
@click.version_option(version="0.1.0")
@click.option('--debug', is_flag=True, help='Enable debug mode')
def cli(debug):
    """eToro Extractor - Extract data from eToro public profiles."""
    load_dotenv()
    
    if debug or os.getenv('DEBUG', 'False').lower() == 'true':
        click.echo("Debug mode enabled")
        os.environ['DEBUG'] = 'True'


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
            import json
            result = json.dumps(portfolio_data, indent=2)
            click.echo(result)
        elif output == 'csv':
            import csv
            import io
            
            if portfolio_data.get('assets'):
                output_buffer = io.StringIO()
                writer = csv.DictWriter(output_buffer, fieldnames=portfolio_data['assets'][0].keys())
                writer.writeheader()
                writer.writerows(portfolio_data['assets'])
                result = output_buffer.getvalue()
                click.echo(result)
        else:  # table format (default)
            from etoro_extractor.formatters import format_portfolio_table
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


if __name__ == '__main__':
    cli()
