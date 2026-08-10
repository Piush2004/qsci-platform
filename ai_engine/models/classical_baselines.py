import time
import tracemalloc
import sys
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from xgboost import XGBRegressor, XGBClassifier
from sklearn.metrics import mean_squared_error, mean_absolute_error, mean_absolute_percentage_error, r2_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def track_metrics(func):
    """Decorator to track time and memory."""
    def wrapper(*args, **kwargs):
        tracemalloc.start()
        start_time = time.time()
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        _, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        duration = end_time - start_time
        peak_memory_mb = peak_memory / (1024 * 1024)
        
        return result, duration, peak_memory_mb
    return wrapper

class BaseModelWrapper:
    def __init__(self, model_type='regression'):
        self.model_type = model_type
        self.model = None
        
    @track_metrics
    def fit(self, X, y):
        self.model.fit(X, y)
        
    @track_metrics
    def predict(self, X):
        return self.model.predict(X)
        
    def evaluate(self, X_train, y_train, X_test, y_test):
        _, train_time, train_mem = self.fit(X_train, y_train)
        predictions, infer_time, infer_mem = self.predict(X_test)
        
        try:
            model_size_kb = len(pickle.dumps(self.model)) / 1024
        except:
            model_size_kb = sys.getsizeof(self.model) / 1024
            
        metrics = {
            'Training Time (s)': train_time,
            'Inference Time (s)': infer_time,
            'Memory Usage (MB)': max(train_mem, infer_mem),
            'Model Size (KB)': model_size_kb,
            'model_type': self.model_type,
            'model_obj': self.model
        }
        
        if self.model_type == 'regression':
            metrics.update({
                'RMSE': np.sqrt(mean_squared_error(y_test, predictions)),
                'MAE': mean_absolute_error(y_test, predictions),
                'MAPE': mean_absolute_percentage_error(y_test, predictions),
                'R2': r2_score(y_test, predictions)
            })
        else:
            # Classification
            metrics.update({
                'Accuracy': accuracy_score(y_test, predictions),
                'Precision': precision_score(y_test, predictions, average='weighted', zero_division=0),
                'Recall': recall_score(y_test, predictions, average='weighted', zero_division=0),
                'F1': f1_score(y_test, predictions, average='weighted', zero_division=0)
            })
            
        return metrics

class XGBoostWrapper(BaseModelWrapper):
    def __init__(self, task_type='regression', **kwargs):
        super().__init__(model_type=task_type)
        if task_type == 'regression':
            self.model = XGBRegressor(**kwargs)
        else:
            self.model = XGBClassifier(**kwargs)

class RandomForestWrapper(BaseModelWrapper):
    def __init__(self, task_type='regression', **kwargs):
        super().__init__(model_type=task_type)
        if task_type == 'regression':
            self.model = RandomForestRegressor(**kwargs)
        else:
            self.model = RandomForestClassifier(**kwargs)

class ARIMAWrapper(BaseModelWrapper):
    def __init__(self, order=(1,1,1)):
        super().__init__(model_type='regression')
        self.order = order
        
    @track_metrics
    def fit(self, X, y):
        try:
            from statsmodels.tsa.arima.model import ARIMA
            self.model = ARIMA(endog=y, order=self.order).fit()
        except ImportError:
            print("statsmodels not installed, ARIMA not available.")
            self.model = None

    @track_metrics
    def predict(self, X):
        if self.model is None:
            return np.zeros(len(X))
        return self.model.forecast(steps=len(X))

class ProphetWrapper(BaseModelWrapper):
    def __init__(self):
        super().__init__(model_type='regression')
        
    @track_metrics
    def fit(self, X, y):
        try:
            from prophet import Prophet
            self.model = Prophet()
            # X must be a dataframe or have a date proxy
            # For simplicity, we create fake dates if needed
            df = pd.DataFrame()
            if isinstance(X, pd.DataFrame) and 'Date' in X.columns:
                df['ds'] = pd.to_datetime(X['Date'])
            else:
                df['ds'] = pd.date_range(start='2020-01-01', periods=len(y))
            df['y'] = np.array(y)
            self.model.fit(df)
        except ImportError:
            print("prophet not installed, Prophet not available.")
            self.model = None

    @track_metrics
    def predict(self, X):
        if self.model is None:
            return np.zeros(len(X))
        df = pd.DataFrame()
        if isinstance(X, pd.DataFrame) and 'Date' in X.columns:
            df['ds'] = pd.to_datetime(X['Date'])
        else:
            df['ds'] = pd.date_range(start='2025-01-01', periods=len(X))
        forecast = self.model.predict(df)
        return forecast['yhat'].values

class LSTMWrapper(BaseModelWrapper):
    def __init__(self, epochs=10, batch_size=32):
        super().__init__(model_type='regression')
        self.epochs = epochs
        self.batch_size = batch_size
        
    @track_metrics
    def fit(self, X, y):
        try:
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import LSTM, Dense
            import tensorflow as tf
            
            # tf.random.set_seed(42)
            
            # reshape X to (samples, time steps, features)
            # Assuming X is 2D (samples, features), we treat it as time_steps=1
            X_reshaped = np.array(X).reshape((X.shape[0], 1, X.shape[1])) if len(np.array(X).shape) == 2 else np.array(X)
            
            self.model = Sequential()
            self.model.add(LSTM(50, activation='relu', input_shape=(X_reshaped.shape[1], X_reshaped.shape[2])))
            self.model.add(Dense(1))
            self.model.compile(optimizer='adam', loss='mse')
            
            self.model.fit(X_reshaped, np.array(y), epochs=self.epochs, batch_size=self.batch_size, verbose=0)
        except ImportError:
            print("tensorflow not installed, LSTM not available.")
            self.model = None

    @track_metrics
    def predict(self, X):
        if self.model is None:
            return np.zeros(len(X))
        X_reshaped = np.array(X).reshape((X.shape[0], 1, X.shape[1])) if len(np.array(X).shape) == 2 else np.array(X)
        preds = self.model.predict(X_reshaped, verbose=0)
        return preds.flatten()
