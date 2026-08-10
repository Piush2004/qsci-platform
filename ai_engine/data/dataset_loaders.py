import os
import pandas as pd
import numpy as np
from pathlib import Path

class DatasetManager:
    """Manages dataset loading with graceful fallback strategy."""
    
    DATA_DIR = Path('d:/Projects/QML project/data')
    
    def __init__(self):
        # Create dirs: data/raw/m5, data/raw/walmart, data/processed, data/synthetic
        for sub in ['raw/m5', 'raw/walmart', 'processed', 'synthetic']:
            (self.DATA_DIR / sub).mkdir(parents=True, exist_ok=True)
    
    def load_m5(self) -> pd.DataFrame:
        """Try data/raw/m5/sales_train_evaluation.csv, fallback to synthetic."""
        real_path = self.DATA_DIR / 'raw/m5/sales_train_evaluation.csv'
        if real_path.exists():
            print('Loading real M5 dataset...')
            return pd.read_csv(real_path)
        print(self.get_setup_instructions())
        print('Falling back to synthetic M5 data...')
        return self.generate_synthetic_m5()
    
    def load_walmart(self) -> pd.DataFrame:
        """Try data/raw/walmart/train.csv, fallback to synthetic."""
        real_path = self.DATA_DIR / 'raw/walmart/train.csv'
        if real_path.exists():
            print('Loading real Walmart dataset...')
            return pd.read_csv(real_path)
        print(self.get_setup_instructions())
        print('Falling back to synthetic Walmart data...')
        return self.generate_synthetic_walmart()
    
    def generate_synthetic_m5(self, num_items=200, days=100) -> pd.DataFrame:
        """Generate realistic synthetic data matching M5 schema with proper seasonality patterns"""
        print(f"Generating synthetic M5 data: {num_items} items over {days} days")
        np.random.seed(42)
        
        # Schema: id, item_id, dept_id, cat_id, store_id, state_id, d_1..d_N
        categories = ['HOBBIES', 'HOUSEHOLD', 'FOODS']
        depts = [f"{c}_{i}" for c in categories for i in range(1, 3)]
        states = ['CA', 'TX', 'WI']
        stores = [f"{s}_{i}" for s in states for i in range(1, 4)]
        
        data = []
        for i in range(num_items):
            cat = np.random.choice(categories)
            dept = np.random.choice([d for d in depts if d.startswith(cat)])
            state = np.random.choice(states)
            store = np.random.choice([s for s in stores if s.startswith(state)])
            item_id = f"{dept}_{np.random.randint(1, 100):03d}"
            row_id = f"{item_id}_{store}_evaluation"
            
            # Base sales level
            base_sales = np.random.uniform(5, 50)
            
            # Daily sales generation with seasonality and trend
            sales = []
            for d in range(days):
                # Weekly seasonality (higher on weekends)
                weekly_effect = np.sin(2 * np.pi * d / 7) * 0.5 + 1.0
                
                # Monthly seasonality
                monthly_effect = np.sin(2 * np.pi * d / 30.4) * 0.2 + 1.0
                
                # Slight trend
                trend = 1.0 + (d / days) * 0.1
                
                # Random promotions (spike in demand)
                promo = 2.0 if np.random.random() < 0.05 else 1.0
                
                # Noise
                noise = np.random.normal(0, 0.2 * base_sales)
                
                daily_sale = int(max(0, base_sales * weekly_effect * monthly_effect * trend * promo + noise))
                sales.append(daily_sale)
                
            row = [row_id, item_id, dept, cat, store, state] + sales
            data.append(row)
            
        columns = ['id', 'item_id', 'dept_id', 'cat_id', 'store_id', 'state_id'] + [f'd_{i+1}' for i in range(days)]
        return pd.DataFrame(data, columns=columns)
    
    def generate_synthetic_walmart(self, num_rows=5000) -> pd.DataFrame:
        """Generate realistic synthetic data matching Walmart schema"""
        print(f"Generating synthetic Walmart data: {num_rows} rows")
        np.random.seed(42)
        
        # Schema: Store, Dept, Date, Weekly_Sales, IsHoliday, Temperature, Fuel_Price, CPI, Unemployment
        dates = pd.date_range(start='2010-02-05', periods=143, freq='W-FRI')
        stores = list(range(1, 46))
        depts = list(range(1, 100))
        
        data = []
        for _ in range(num_rows):
            store = np.random.choice(stores)
            dept = np.random.choice(depts)
            date = np.random.choice(dates)
            
            # Seasonal temperature (proxy based on day of year)
            day_of_year = pd.Timestamp(date).dayofyear
            temp = 60 + 30 * np.sin(2 * np.pi * (day_of_year - 120) / 365) + np.random.normal(0, 5)
            
            # Holidays
            month = pd.Timestamp(date).month
            is_holiday = True if month in [11, 12] and np.random.random() < 0.2 else False
            
            # Correlate sales with temperature and holidays
            base_sales = np.random.uniform(1000, 50000)
            temp_effect = 1.0 + (temp - 60) / 200.0  # slight positive correlation
            holiday_effect = 1.5 if is_holiday else 1.0
            noise = np.random.normal(0, 0.1 * base_sales)
            
            weekly_sales = max(0, base_sales * temp_effect * holiday_effect + noise)
            
            fuel_price = np.random.uniform(2.5, 4.0)
            cpi = np.random.uniform(126.0, 228.0)
            unemployment = np.random.uniform(4.0, 14.0)
            
            data.append([store, dept, date, weekly_sales, is_holiday, temp, fuel_price, cpi, unemployment])
            
        columns = ['Store', 'Dept', 'Date', 'Weekly_Sales', 'IsHoliday', 'Temperature', 'Fuel_Price', 'CPI', 'Unemployment']
        df = pd.DataFrame(data, columns=columns)
        return df.sort_values(by=['Store', 'Dept', 'Date']).reset_index(drop=True)
    
    def get_setup_instructions(self) -> str:
        """Returns instructions for downloading real datasets"""
        return '''
==========================================================
  DATASET SETUP INSTRUCTIONS                              
==========================================================
  M5 Dataset:                                             
  Download: kaggle.com/competitions/m5-forecasting-accuracy
  Place: data/raw/m5/sales_train_evaluation.csv           
                                                          
  Walmart Dataset:                                        
  Download: kaggle.com/competitions/walmart-recruiting-... 
  Place: data/raw/walmart/train.csv                       
==========================================================
        '''
