"""
Phase 1.1: Kaggle Dataset Discovery & Analysis
==============================================

This script downloads and explores the Kaggle car dataset.
We'll learn about the data structure, columns, and quality.

Learning Goals:
- How to download Kaggle datasets
- Exploring data with pandas
- Understanding data quality
- Identifying useful columns for our project
"""

# ============================================================================
# STEP 1: Import Required Libraries
# ============================================================================

import kagglehub  # For downloading Kaggle datasets
import pandas as pd  # For data analysis and manipulation
from pathlib import Path  # For working with file paths
import os  # For file system operations

# ============================================================================
# STEP 2: Download the Dataset
# ============================================================================

print("=" * 70)
print("🚗 PHASE 1.1: KAGGLE DATASET DISCOVERY")
print("=" * 70)
print()

# What does this do?
# ------------------
# kagglehub.dataset_download() connects to Kaggle's API and downloads
# the entire dataset to your local machine. It returns the path where
# the files were saved.
#
# The dataset identifier format is: "username/dataset-name"
# In this case: "abdulmalik1518/cars-datasets-2025"

print("📥 Step 1: Downloading dataset from Kaggle...")
print("   (This may take a minute on first run)")
print()

try:
    # Download the dataset
    dataset_path = kagglehub.dataset_download("abdulmalik1518/cars-datasets-2025")
    
    # Convert to Path object for easier manipulation
    # Path() is from pathlib - it makes working with file paths easier
    dataset_path = Path(dataset_path)
    
    print(f"✅ Dataset downloaded successfully!")
    print(f"📁 Location: {dataset_path}")
    print()
    
except Exception as e:
    # If download fails (no API key, network error, etc.), show the error
    print(f"❌ Error downloading dataset: {e}")
    print()
    print("💡 Tip: Make sure you have Kaggle API credentials set up:")
    print("   1. Go to https://www.kaggle.com/account")
    print("   2. Scroll to 'API' section")
    print("   3. Click 'Create New API Token'")
    print("   4. Save kaggle.json to ~/.kaggle/ (or C:\\Users\\YourName\\.kaggle\\)")
    exit(1)

# ============================================================================
# STEP 3: Explore What Files Are in the Dataset
# ============================================================================

print("=" * 70)
print("📂 Step 2: Exploring dataset files...")
print("=" * 70)
print()

# What does this do?
# ------------------
# list(dataset_path.glob("*")) finds all files in the directory
# We want to see what files are available before we try to load them

files = list(dataset_path.glob("*"))

print(f"Found {len(files)} file(s) in the dataset:")
print()

for file in files:
    # Get file size in a readable format
    size_bytes = file.stat().st_size
    size_mb = size_bytes / (1024 * 1024)  # Convert bytes to megabytes
    
    print(f"  📄 {file.name}")
    print(f"     Size: {size_mb:.2f} MB")
    print(f"     Type: {file.suffix}")
    print()

# ============================================================================
# STEP 4: Load the CSV File(s) into Pandas
# ============================================================================

print("=" * 70)
print("📊 Step 3: Loading data with pandas...")
print("=" * 70)
print()

# What is pandas?
# ---------------
# Pandas is Python's main library for data analysis. It provides:
# - DataFrame: Like an Excel spreadsheet in Python
# - Tools for cleaning, transforming, and analyzing data
# - Easy CSV/Excel reading and writing

# Find CSV files (most common format for datasets)
csv_files = list(dataset_path.glob("*.csv"))

if not csv_files:
    print("⚠️  No CSV files found. Looking for other formats...")
    # Could also look for .parquet, .xlsx, etc.
    exit(1)

# Use the first CSV file (or we can ask user to choose if multiple)
csv_file = csv_files[0]
print(f"📖 Loading: {csv_file.name}")
print()

# What does pd.read_csv() do?
# ---------------------------
# - Reads the CSV file into a DataFrame
# - nrows=5 means "only load first 5 rows" (for quick preview)
# - This is useful for large datasets - we peek before loading everything

# First, let's peek at just 5 rows
print("👀 Loading first 5 rows for preview...")
df_preview = pd.read_csv(csv_file, nrows=5)

print(f"✅ Preview loaded! Shape: {df_preview.shape}")
print(f"   (That's {df_preview.shape[0]} rows × {df_preview.shape[1]} columns)")
print()

# ============================================================================
# STEP 5: Explore the Data Structure
# ============================================================================

print("=" * 70)
print("🔍 Step 4: Understanding the data structure...")
print("=" * 70)
print()

# 5.1: Column Names and Types
# ----------------------------
print("📋 Column Information:")
print("-" * 70)

# What does .info() show?
# -----------------------
# - Column names
# - Data types (int, float, object/string, etc.)
# - Non-null count (how many values are present)
# - Memory usage
df_preview.info()

print()

# 5.2: First Few Rows
# -------------------
print("=" * 70)
print("👁️  First 5 Rows of Data:")
print("=" * 70)
print()

# What does .head() do?
# ---------------------
# Shows the first few rows so you can see what the data looks like
# Default is 5 rows, but you can do .head(10) for more
print(df_preview.head())
print()

# 5.3: Statistical Summary
# ------------------------
print("=" * 70)
print("📈 Statistical Summary (for numeric columns):")
print("=" * 70)
print()

# What does .describe() show?
# ---------------------------
# - count: how many non-null values
# - mean: average value
# - std: standard deviation (how spread out the data is)
# - min/max: smallest and largest values
# - 25%/50%/75%: quartiles (distribution)
print(df_preview.describe())
print()

# 5.4: Column Names (for easy reference)
# ---------------------------------------
print("=" * 70)
print("📝 All Column Names:")
print("=" * 70)
print()

for i, col in enumerate(df_preview.columns, 1):
    print(f"  {i:2d}. {col}")

print()

# ============================================================================
# STEP 6: Now Load the FULL Dataset
# ============================================================================

print("=" * 70)
print("💾 Step 5: Loading FULL dataset...")
print("=" * 70)
print()

print("⏳ This might take a moment for large datasets...")

# Now load everything (no nrows limit)
df_full = pd.read_csv(csv_file)

print(f"✅ Full dataset loaded!")
print(f"   Shape: {df_full.shape[0]:,} rows × {df_full.shape[1]} columns")
print(f"   Memory: {df_full.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
print()

# ============================================================================
# STEP 7: Data Quality Check
# ============================================================================

print("=" * 70)
print("🔍 Step 6: Checking data quality...")
print("=" * 70)
print()

# 7.1: Missing Values
# -------------------
print("❓ Missing Values Analysis:")
print("-" * 70)

# What does .isnull().sum() do?
# -----------------------------
# - .isnull() creates True/False for each cell (True = missing)
# - .sum() counts the True values per column
# - Helps identify which columns need cleaning

missing = df_full.isnull().sum()
missing_pct = (missing / len(df_full)) * 100

# Combine into a nice table
missing_df = pd.DataFrame({
    'Missing Count': missing,
    'Percentage': missing_pct
})

# Only show columns with missing data
missing_df = missing_df[missing_df['Missing Count'] > 0].sort_values(
    'Missing Count', ascending=False
)

if len(missing_df) > 0:
    print(missing_df)
    print()
    print(f"⚠️  {len(missing_df)} columns have missing data")
else:
    print("✅ No missing values! Perfect!")

print()

# 7.2: Duplicate Rows
# -------------------
print("🔁 Duplicate Rows Check:")
print("-" * 70)

duplicates = df_full.duplicated().sum()
print(f"Found {duplicates} duplicate rows")

if duplicates > 0:
    print(f"⚠️  That's {(duplicates/len(df_full)*100):.2f}% of the data")
else:
    print("✅ No duplicates!")

print()

# 7.3: Unique Values in Key Columns
# ---------------------------------
print("🔢 Unique Value Counts (for key columns):")
print("-" * 70)

# We'll check columns that might be make, model, year, etc.
# This helps us understand the data variety

key_columns = [col for col in df_full.columns if any(
    keyword in col.lower() 
    for keyword in ['make', 'model', 'year', 'brand', 'manufacturer']
)]

for col in key_columns:
    unique_count = df_full[col].nunique()
    print(f"  {col}: {unique_count:,} unique values")

print()

# ============================================================================
# STEP 8: Save Exploration Summary
# ============================================================================

print("=" * 70)
print("💾 Step 7: Saving exploration results...")
print("=" * 70)
print()

# Create output directory
output_dir = Path(__file__).parent.parent / "app" / "data" / "kaggle_raw"
output_dir.mkdir(parents=True, exist_ok=True)

# Save a summary report
summary_file = output_dir / "exploration_summary.txt"

with open(summary_file, 'w') as f:
    f.write("=" * 70 + "\n")
    f.write("KAGGLE DATASET EXPLORATION SUMMARY\n")
    f.write("=" * 70 + "\n\n")
    
    f.write(f"Dataset: abdulmalik1518/cars-datasets-2025\n")
    f.write(f"Location: {dataset_path}\n")
    f.write(f"File: {csv_file.name}\n\n")
    
    f.write(f"Shape: {df_full.shape[0]:,} rows × {df_full.shape[1]} columns\n\n")
    
    f.write("Columns:\n")
    f.write("-" * 70 + "\n")
    for i, col in enumerate(df_full.columns, 1):
        f.write(f"{i:2d}. {col}\n")
    
    f.write("\n")
    f.write("Missing Values:\n")
    f.write("-" * 70 + "\n")
    f.write(str(missing_df))
    
    f.write(f"\n\nDuplicates: {duplicates}\n")

print(f"✅ Summary saved to: {summary_file}")
print()

# ============================================================================
# STEP 9: Display Next Steps
# ============================================================================

print("=" * 70)
print("✅ PHASE 1.1 COMPLETE!")
print("=" * 70)
print()

print("📊 What we learned:")
print(f"  • Dataset has {df_full.shape[0]:,} vehicles")
print(f"  • {df_full.shape[1]} columns of data")
print(f"  • {len(missing_df)} columns with missing values")
print(f"  • {duplicates} duplicate rows")
print()

print("🔜 Next Steps (Phase 1.2):")
print("  1. Review the columns and decide which ones we need")
print("  2. Clean the data (handle missing values, duplicates)")
print("  3. Map columns to our catalog schema")
print("  4. Export as clean JSON")
print()

print(f"💡 The full dataset is available at:")
print(f"   df_full variable in this script")
print(f"   Original file: {csv_file}")
print()

# Return the dataframe for further use
print("🎓 Ready to move to Phase 1.2? Run the next script!")
