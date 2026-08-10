import os
import matplotlib.pyplot as plt
import seaborn as sns

def generate_all_figures(results_df, inventory_df, output_dir):
    """
    Generates publication-quality figures for the IEEE paper.
    """
    # Set publication style
    plt.style.use('seaborn-v0_8-paper')
    sns.set_context("paper", font_scale=1.2)
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. RMSE Comparison
    plt.figure(figsize=(8, 5))
    sns.barplot(data=results_df, x='model', y='rmse', hue='sku')
    plt.title('Forecast RMSE by Model and SKU')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "rmse_comparison.pdf"))
    plt.close()
    
    # 2. Total Time (Execution + Overhead)
    plt.figure(figsize=(8, 5))
    sns.barplot(data=results_df, x='model', y='total_time_sec')
    plt.title('Total Pipeline Execution Time (w/ QRAM Overhead)')
    plt.ylabel('Seconds')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "runtime_comparison.pdf"))
    plt.close()
    
    # 3. Expected Savings
    plt.figure(figsize=(8, 5))
    sns.barplot(data=inventory_df, x='model', y='expected_savings_vs_naive', hue='sku')
    plt.title('Expected Financial Savings vs Naive Baseline')
    plt.ylabel('Dollars ($)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "expected_savings.pdf"))
    plt.close()
    
    print("  -> Figures saved to paper/experiments/results/")
