# def save_csv(df, filename):
#     """Save DataFrame to processed CSV"""
#     output_path = f"../data/processed/{filename}"
#     df.to_csv(output_path, index=False)
#     print(f"Saved {filename} to processed folder")

from pathlib import Path

PROCESSED_DIR = Path("../data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def load_csv(df, filename):
    output_file = PROCESSED_DIR / filename
    df.to_csv(output_file, index=False)
    print(f"Saved {filename} to {output_file}")
