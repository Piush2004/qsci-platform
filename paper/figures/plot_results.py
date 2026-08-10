import matplotlib.pyplot as plt
import numpy as np
import os

def generate_benchmark_plot():
    """
    Generates high-quality IEEE-formatted plots for the paper.
    """
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # Mock data
    models = ['LightGBM', 'TFT', 'VQR (Sim)', 'VQR (Heron)']
    rmse = [15.2, 12.4, 13.8, 18.5]
    
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(models, rmse, color=['#3b82f6', '#10b981', '#8b5cf6', '#d946ef'])
    
    ax.set_ylabel('RMSE (Lower is Better)')
    ax.set_title('Demand Forecasting Performance (M5 Dataset)')
    
    # Add values on top of bars
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')
                    
    plt.tight_layout()
    
    os.makedirs(os.path.dirname(__file__), exist_ok=True)
    out_path = os.path.join(os.path.dirname(__file__), "benchmark_rmse.pdf")
    plt.savefig(out_path, format='pdf', dpi=300)
    print(f"Plot saved to {out_path}")

if __name__ == "__main__":
    generate_benchmark_plot()
