# src/data_handler.py
import pandas as pd
import numpy as np
from pathlib import Path

def create_top_50_countries():
    """Create comprehensive data for top 50 countries"""
    # Create a dictionary with lists of equal length
    data = {
        'country': [
            'China', 'India', 'United States', 'Indonesia', 'Pakistan', 
            'Brazil', 'Nigeria', 'Bangladesh', 'Russia', 'Mexico',
            'Japan', 'Ethiopia', 'Philippines', 'Egypt', 'Vietnam',
            'DR Congo', 'Turkey', 'Iran', 'Germany', 'Thailand',
            'United Kingdom', 'France', 'Italy', 'South Africa', 'Tanzania',
            'Myanmar', 'South Korea', 'Colombia', 'Kenya', 'Spain',
            'Argentina', 'Algeria', 'Sudan', 'Uganda', 'Iraq',
            'Poland', 'Canada', 'Morocco', 'Saudi Arabia', 'Uzbekistan',
            'Malaysia', 'Peru', 'Afghanistan', 'Venezuela', 'Ghana',
            'Angola', 'Nepal', 'Yemen', 'North Korea', 'Australia'
        ]
    }
    
    # Create DataFrame first
    df = pd.DataFrame(data)
    
    # Add continent data
    continent_map = {
        'China': 'Asia', 'India': 'Asia', 'United States': 'North America',
        'Indonesia': 'Asia', 'Pakistan': 'Asia', 'Brazil': 'South America',
        'Nigeria': 'Africa', 'Bangladesh': 'Asia', 'Russia': 'Europe/Asia',
        'Mexico': 'North America', 'Japan': 'Asia', 'Ethiopia': 'Africa',
        'Philippines': 'Asia', 'Egypt': 'Africa', 'Vietnam': 'Asia',
        'DR Congo': 'Africa', 'Turkey': 'Asia', 'Iran': 'Asia',
        'Germany': 'Europe', 'Thailand': 'Asia', 'United Kingdom': 'Europe',
        'France': 'Europe', 'Italy': 'Europe', 'South Africa': 'Africa',
        'Tanzania': 'Africa', 'Myanmar': 'Asia', 'South Korea': 'Asia',
        'Colombia': 'South America', 'Kenya': 'Africa', 'Spain': 'Europe',
        'Argentina': 'South America', 'Algeria': 'Africa', 'Sudan': 'Africa',
        'Uganda': 'Africa', 'Iraq': 'Asia', 'Poland': 'Europe',
        'Canada': 'North America', 'Morocco': 'Africa', 'Saudi Arabia': 'Asia',
        'Uzbekistan': 'Asia', 'Malaysia': 'Asia', 'Peru': 'South America',
        'Afghanistan': 'Asia', 'Venezuela': 'South America', 'Ghana': 'Africa',
        'Angola': 'Africa', 'Nepal': 'Asia', 'Yemen': 'Asia',
        'North Korea': 'Asia', 'Australia': 'Oceania'
    }
    df['continent'] = df['country'].map(continent_map)
    
    # Add population data (2021 estimates)
    df['population'] = [1439323776, 1380004385, 331002651, 273523615, 220892340,
                       212559417, 206139589, 164689383, 145912025, 128932753,
                       126476461, 114963588, 109581078, 102334404, 97338579,
                       89561403, 84339067, 83992949, 83783942, 69799978,
                       67886011, 65273511, 60461826, 59308690, 59734218,
                       54409800, 51269185, 50882891, 53771296, 46754778,
                       45195774, 44616624, 43849260, 45741007, 40462701,
                       37846611, 37742154, 36910560, 34813871, 33469203,
                       32365999, 32971854, 38928346, 28435943, 31072940,
                       32866272, 29136808, 29825964, 25778816, 25499884]
    
    # Generate semi-realistic data for other metrics
    np.random.seed(42)  # For reproducibility
    
    # Population density (people per sq km)
    df['population_density'] = np.random.uniform(3, 1300, len(df)).round(1)
    
    # Air Quality Index (0-500, lower is better)
    df['air_quality_index'] = np.random.uniform(30, 180, len(df)).round(1)
    
    # Water Quality Index (0-100, higher is better)
    df['water_quality_index'] = np.random.uniform(40, 95, len(df)).round(1)
    
    # Age distribution
    df['age_distribution_young'] = np.random.uniform(15, 45, len(df)).round(1)
    df['age_distribution_adult'] = np.random.uniform(40, 65, len(df)).round(1)
    df['age_distribution_elderly'] = (100 - df['age_distribution_young'] - df['age_distribution_adult']).round(1)
    
    # Gender ratio (males per 100 females)
    df['gender_ratio'] = np.random.uniform(95, 105, len(df)).round(1)
    
    # Health conditions percentage
    df['health_conditions_percentage'] = np.random.uniform(15, 35, len(df)).round(1)
    
    return df

class CountryDataHandler:
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / 'data'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def initialize_default_data(self):
        """Initialize with top 50 countries data"""
        df = create_top_50_countries()
        self.save_country_data(df)
        return df
    
    def save_country_data(self, df, filename='country_data.csv'):
        """Save country data to CSV file"""
        file_path = self.data_dir / filename
        df.to_csv(file_path, index=False)
        print(f"Data saved to {file_path}")
    
    def load_country_data(self, filename='country_data.csv'):
        """Load country data from CSV file"""
        file_path = self.data_dir / filename
        try:
            df = pd.read_csv(file_path)
            # Verify all required columns are present
            required_columns = ['country', 'continent', 'population', 'population_density', 
                              'air_quality_index', 'water_quality_index', 'age_distribution_young',
                              'age_distribution_adult', 'age_distribution_elderly', 
                              'gender_ratio', 'health_conditions_percentage']
            
            if not all(col in df.columns for col in required_columns):
                print("Missing columns in existing data. Reinitializing...")
                return self.initialize_default_data()
            return df
        except FileNotFoundError:
            print("No existing data found. Initializing with default data...")
            return self.initialize_default_data()
        
    def get_country_stats(self):
        """Get basic statistics about the countries"""
        df = self.load_country_data()
        stats = {
            'total_countries': len(df),
            'continents': df['continent'].unique().tolist(),
            'avg_population': df['population'].mean(),
            'avg_air_quality': df['air_quality_index'].mean(),
            'avg_water_quality': df['water_quality_index'].mean()
        }
        return stats

# Test the data handler
if __name__ == "__main__":
    handler = CountryDataHandler()
    data = handler.load_country_data()
    print(f"Loaded data for {len(data)} countries")
    print("\nColumns in dataset:", data.columns.tolist())
    print("\nSample statistics:")
    print(handler.get_country_stats())