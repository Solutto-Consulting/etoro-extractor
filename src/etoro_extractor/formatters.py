"""
Output formatters for eToro Extractor.
"""

from typing import Dict, Any, List
import json


def format_portfolio_table(portfolio_data: Dict[str, Any]) -> str:
    """
    Format portfolio data as a readable table.
    
    Args:
        portfolio_data: Dictionary containing portfolio information
        
    Returns:
        Formatted table string
    """
    if not portfolio_data:
        return "No portfolio data available."
    
    output = []
    
    # Header information
    user = portfolio_data.get('user', 'Unknown')
    total_assets = portfolio_data.get('total_assets', 0)
    last_updated = portfolio_data.get('last_updated', 'Unknown')
    
    output.append(f"Portfolio for: {user}")
    output.append(f"Total Assets: {total_assets}")
    if last_updated != 'Unknown':
        output.append(f"Last Updated: {last_updated}")
    output.append("-" * 80)
    
    # Assets table
    assets = portfolio_data.get('assets', [])
    if not assets:
        output.append("No assets found in portfolio.")
        return '\n'.join(output)
    
    # Determine available columns
    all_keys = set()
    for asset in assets:
        all_keys.update(asset.keys())
    
    # Define column order and headers
    column_mapping = {
        'name': 'Asset Name',
        'percentage': 'Allocation %',
        'value': 'Value',
        'profit_loss': 'P&L',
        'extracted_from': 'Source'
    }
    
    # Filter to available columns
    columns = []
    headers = []
    for key, header in column_mapping.items():
        if key in all_keys:
            columns.append(key)
            headers.append(header)
    
    # Calculate column widths
    col_widths = []
    for i, col in enumerate(columns):
        max_width = len(headers[i])
        for asset in assets:
            value = str(asset.get(col, ''))
            max_width = max(max_width, len(value))
        col_widths.append(min(max_width + 2, 30))  # Cap at 30 chars
    
    # Format header
    header_row = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    output.append(header_row)
    output.append("-" * len(header_row))
    
    # Format asset rows
    for asset in assets:
        row_data = []
        for i, col in enumerate(columns):
            value = str(asset.get(col, ''))
            # Truncate if too long
            if len(value) > col_widths[i]:
                value = value[:col_widths[i]-3] + "..."
            row_data.append(value.ljust(col_widths[i]))
        
        output.append(" | ".join(row_data))
    
    return '\n'.join(output)


def format_portfolio_json(portfolio_data: Dict[str, Any]) -> str:
    """
    Format portfolio data as JSON.
    
    Args:
        portfolio_data: Dictionary containing portfolio information
        
    Returns:
        JSON formatted string
    """
    return json.dumps(portfolio_data, indent=2, ensure_ascii=False)


def format_portfolio_csv(portfolio_data: Dict[str, Any]) -> str:
    """
    Format portfolio data as CSV.
    
    Args:
        portfolio_data: Dictionary containing portfolio information
        
    Returns:
        CSV formatted string
    """
    import csv
    import io
    
    assets = portfolio_data.get('assets', [])
    if not assets:
        return "name,percentage,value,profit_loss\n"
    
    # Get all unique keys from assets
    fieldnames = set()
    for asset in assets:
        fieldnames.update(asset.keys())
    fieldnames = sorted(list(fieldnames))
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(assets)
    
    return output.getvalue()
