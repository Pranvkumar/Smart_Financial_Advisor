"""
LSTM-based Stock Price Predictor with GPU Support
"""
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import logging
from typing import Tuple, Dict, List
import os

logger = logging.getLogger(__name__)


class LSTMPredictor(nn.Module):
    """LSTM Neural Network for Stock Price Prediction"""
    
    def __init__(self, input_size: int = 20, hidden_size: int = 128, 
                 num_layers: int = 3, output_size: int = 1, dropout: float = 0.2):
        super(LSTMPredictor, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # LSTM layers
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout,
            batch_first=True
        )
        
        # Fully connected layers
        self.fc1 = nn.Linear(hidden_size, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, output_size)
        
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, x):
        # LSTM forward pass
        lstm_out, _ = self.lstm(x)
        
        # Take the last output
        out = lstm_out[:, -1, :]
        
        # Fully connected layers
        out = self.relu(self.fc1(out))
        out = self.dropout(out)
        out = self.relu(self.fc2(out))
        out = self.dropout(out)
        out = self.fc3(out)
        
        return out


class StockPricePredictor:
    """Stock Price Prediction Engine with GPU Acceleration"""
    
    def __init__(self, sequence_length: int = 60, prediction_days: int = 30):
        self.sequence_length = sequence_length
        self.prediction_days = prediction_days
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.feature_scaler = MinMaxScaler(feature_range=(0, 1))
        
        logger.info(f"Using device: {self.device}")
        if self.device.type == 'cuda':
            logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
            logger.info(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    
    def create_sequences(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Create sequences for LSTM training"""
        X, y = [], []
        
        for i in range(len(data) - self.sequence_length):
            X.append(data[i:i + self.sequence_length])
            y.append(data[i + self.sequence_length, 0])  # Predict close price
        
        return np.array(X), np.array(y)
    
    def prepare_data(self, df: pd.DataFrame, features: List[str]) -> Tuple:
        """Prepare data for training"""
        # Scale target (close price)
        close_prices = df['Close'].values.reshape(-1, 1)
        scaled_close = self.scaler.fit_transform(close_prices)
        
        # Scale features
        feature_data = df[features].values
        scaled_features = self.feature_scaler.fit_transform(feature_data)
        
        # Combine scaled close with features
        combined_data = np.column_stack([scaled_close, scaled_features])
        
        # Create sequences
        X, y = self.create_sequences(combined_data)
        
        # Split into train and test
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        return X_train, X_test, y_train, y_test
    
    def train(self, df: pd.DataFrame, features: List[str], 
              epochs: int = 50, batch_size: int = 32, learning_rate: float = 0.001):
        """Train the LSTM model"""
        logger.info(f"Training model with {len(df)} data points...")
        
        # Prepare data
        X_train, X_test, y_train, y_test = self.prepare_data(df, features)
        
        # Convert to PyTorch tensors
        X_train = torch.FloatTensor(X_train).to(self.device)
        y_train = torch.FloatTensor(y_train).reshape(-1, 1).to(self.device)
        X_test = torch.FloatTensor(X_test).to(self.device)
        y_test = torch.FloatTensor(y_test).reshape(-1, 1).to(self.device)
        
        # Initialize model
        input_size = X_train.shape[2]
        self.model = LSTMPredictor(input_size=input_size).to(self.device)
        
        # Loss and optimizer
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        
        # Training loop
        best_loss = float('inf')
        train_losses = []
        val_losses = []
        
        for epoch in range(epochs):
            self.model.train()
            epoch_loss = 0
            
            # Mini-batch training
            for i in range(0, len(X_train), batch_size):
                batch_X = X_train[i:i+batch_size]
                batch_y = y_train[i:i+batch_size]
                
                # Forward pass
                outputs = self.model(batch_X)
                loss = criterion(outputs, batch_y)
                
                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                epoch_loss += loss.item()
            
            # Validation
            self.model.eval()
            with torch.no_grad():
                val_outputs = self.model(X_test)
                val_loss = criterion(val_outputs, y_test).item()
            
            avg_train_loss = epoch_loss / (len(X_train) // batch_size)
            train_losses.append(avg_train_loss)
            val_losses.append(val_loss)
            
            if (epoch + 1) % 10 == 0:
                logger.info(f"Epoch [{epoch+1}/{epochs}] - "
                          f"Train Loss: {avg_train_loss:.6f}, "
                          f"Val Loss: {val_loss:.6f}")
            
            # Save best model
            if val_loss < best_loss:
                best_loss = val_loss
                self.save_model('models/best_model.pth')
        
        # Calculate metrics
        self.model.eval()
        with torch.no_grad():
            train_pred = self.model(X_train).cpu().numpy()
            test_pred = self.model(X_test).cpu().numpy()
        
        # Inverse transform predictions
        train_pred = self.scaler.inverse_transform(train_pred)
        test_pred = self.scaler.inverse_transform(test_pred)
        y_train_actual = self.scaler.inverse_transform(y_train.cpu().numpy())
        y_test_actual = self.scaler.inverse_transform(y_test.cpu().numpy())
        
        # Calculate metrics
        train_rmse = np.sqrt(mean_squared_error(y_train_actual, train_pred))
        test_rmse = np.sqrt(mean_squared_error(y_test_actual, test_pred))
        test_mae = mean_absolute_error(y_test_actual, test_pred)
        test_r2 = r2_score(y_test_actual, test_pred)
        
        metrics = {
            'train_rmse': float(train_rmse),
            'test_rmse': float(test_rmse),
            'test_mae': float(test_mae),
            'test_r2': float(test_r2),
            'train_losses': train_losses,
            'val_losses': val_losses
        }
        
        logger.info(f"Training completed!")
        logger.info(f"Test RMSE: {test_rmse:.2f}")
        logger.info(f"Test MAE: {test_mae:.2f}")
        logger.info(f"Test R²: {test_r2:.4f}")
        
        return metrics
    
    def predict(self, df: pd.DataFrame, features: List[str], days: int = 30) -> Dict:
        """Predict future stock prices"""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        self.model.eval()
        
        # Prepare last sequence
        close_prices = df['Close'].values[-self.sequence_length:].reshape(-1, 1)
        scaled_close = self.scaler.transform(close_prices)
        
        feature_data = df[features].values[-self.sequence_length:]
        scaled_features = self.feature_scaler.transform(feature_data)
        
        combined_data = np.column_stack([scaled_close, scaled_features])
        
        # Predict future prices
        predictions = []
        current_sequence = combined_data.copy()
        
        with torch.no_grad():
            for _ in range(days):
                # Prepare input
                X = torch.FloatTensor(current_sequence).unsqueeze(0).to(self.device)
                
                # Predict
                pred = self.model(X).cpu().numpy()[0, 0]
                predictions.append(pred)
                
                # Update sequence (simple approach - use last features)
                new_row = np.append(pred, scaled_features[-1])
                current_sequence = np.vstack([current_sequence[1:], new_row])
        
        # Inverse transform predictions
        predictions = np.array(predictions).reshape(-1, 1)
        predictions = self.scaler.inverse_transform(predictions)
        
        # Calculate confidence intervals (simple std-based)
        std_dev = predictions.std()
        lower_bound = predictions - 1.96 * std_dev
        upper_bound = predictions + 1.96 * std_dev
        
        return {
            'predictions': predictions.flatten().tolist(),
            'lower_bound': lower_bound.flatten().tolist(),
            'upper_bound': upper_bound.flatten().tolist(),
            'confidence': 0.95
        }
    
    def save_model(self, path: str):
        """Save model to disk"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'scaler': self.scaler,
            'feature_scaler': self.feature_scaler,
            'sequence_length': self.sequence_length
        }, path)
        logger.info(f"Model saved to {path}")
    
    def load_model(self, path: str, input_size: int):
        """Load model from disk"""
        checkpoint = torch.load(path, map_location=self.device)
        self.model = LSTMPredictor(input_size=input_size).to(self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.scaler = checkpoint['scaler']
        self.feature_scaler = checkpoint['feature_scaler']
        self.sequence_length = checkpoint['sequence_length']
        self.model.eval()
        logger.info(f"Model loaded from {path}")


if __name__ == "__main__":
    # Example usage
    print("LSTM Stock Predictor initialized")
    print(f"Device: {'CUDA' if torch.cuda.is_available() else 'CPU'}")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
