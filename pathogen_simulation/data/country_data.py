# Country statistics and indices

import pandas as pd
import os
from pathlib import Path

class CountryDataHandler:
    def __init__(self):
        # Get the absolute path to the data directory
        self.data_dir = Path(__file__).parent.parent / 'data'
        self.ensure_data_directory()
        
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        os.makedirs(self.data_dir, exist_ok=True)
        
    def save_country_data(self, df, filename='country_data.csv'):
        """Save country data to CSV file"""
        file_path = self.data_dir / filename
        df.to_csv(file_path, index=False)
        print(f"Data saved to {file_path}")
        
    def load_country_data(self, filename='country_data.csv'):
        """Load country data from CSV file"""
        file_path = self.data_dir / filename
        try:
            return pd.read_csv(file_path)
        except FileNotFoundError:
            print(f"No data file found at {file_path}")
            return None
            
    def update_country_data(self, new_data, filename='country_data.csv'):
        """Update existing country data"""
        existing_data = self.load_country_data(filename)
        if existing_data is not None:
            # Merge or update logic here
            updated_data = pd.concat([existing_data, new_data]).drop_duplicates()
            self.save_country_data(updated_data, filename)
        else:
            self.save_country_data(new_data, filename)
            
    def get_country_statistics(self, filename='country_data.csv'):
        """Get basic statistics about the country data"""
        data = self.load_country_data(filename)
        if data is not None:
            stats = {
                'total_countries': len(data),
                'columns': list(data.columns),
                'missing_values': data.isnull().sum().to_dict()
            }
            return stats
        return None

# Example usage:
if __name__ == "__main__":
    # Sample country data
    sample_data = pd.DataFrame({
        'country': ['USA', 'Canada', 'UK', 'France', 'Germany'],
        'population': [331002651, 37742154, 67886011, 65273511, 83783942],
        'continent': ['North America', 'North America', 'Europe', 'Europe', 'Europe'],
        'capital': ['Washington, D.C.', 'Ottawa', 'London', 'Paris', 'Berlin']
    })
    
    # Initialize handler
    handler = CountryDataHandler()
    
    # Save data
    handler.save_country_data(sample_data)
    
    # Load and display statistics
    stats = handler.get_country_statistics()
    print("Country Data Statistics:", stats)