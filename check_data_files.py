"""
check_data_files.py
Check all datasets and provide detailed information
"""

import os
import pandas as pd
import json
import jsonlines
from pathlib import Path
from colorama import init, Fore, Style
from tabulate import tabulate

# Initialize colorama
init()


class DataChecker:
    def __init__(self):
        self.data_root = Path("data")
        self.stats = {}

    def check_all_datasets(self):
        """Check all datasets in the data directory"""

        print(Fore.CYAN + "=" * 70)
        print("COMPREHENSIVE DATA FILE CHECK")
        print("=" * 70 + Style.RESET_ALL)

        if not self.data_root.exists():
            print(Fore.RED + f"❌ Data directory '{self.data_root}' not found!" + Style.RESET_ALL)
            return

        # Check each dataset
        self.check_amazon_products()
        self.check_behavior_data()
        self.check_customer_behavior()
        self.check_uci_retail()
        self.check_transactions()
        self.check_amazon_reviews()
        self.check_sales_data()

        # Print summary
        self.print_summary()

    def check_amazon_products(self):
        """Check Amazon Product Data (JSONL files)"""
        print("\n" + Fore.YELLOW + "1. AMAZON PRODUCT DATA (UCSD)" + Style.RESET_ALL)
        print("-" * 50)

        path = self.data_root / "1. Amazon Product Data (UCSD)"
        if not path.exists():
            print(Fore.RED + "  ✗ Directory not found" + Style.RESET_ALL)
            return

        files = list(path.glob("*.jsonl"))
        if not files:
            print("  No JSONL files found")
            return

        for file in files:
            print(f"\n  📄 {file.name}")
            size_mb = file.stat().st_size / (1024 * 1024)
            print(f"     Size: {size_mb:.2f} MB")

            # Sample the file
            try:
                with jsonlines.open(file) as reader:
                    sample = []
                    for i, obj in enumerate(reader):
                        sample.append(obj)
                        if i >= 2:  # Just read 3 records
                            break

                    if sample:
                        # Detect type (review or metadata)
                        if 'overall' in sample[0]:
                            print(f"     Type: Review data")
                            print(f"     Sample fields: {list(sample[0].keys())[:5]}")
                            self.stats[file.name] = {'type': 'review', 'sample': sample[0]}
                        elif 'title' in sample[0] or 'price' in sample[0]:
                            print(f"     Type: Product metadata")
                            print(f"     Sample fields: {list(sample[0].keys())[:5]}")
                            self.stats[file.name] = {'type': 'metadata', 'sample': sample[0]}

                        # Count total records (quick estimate)
                        with open(file, 'r', encoding='utf-8') as f:
                            line_count = sum(1 for line in f)
                        print(f"     Estimated records: {line_count:,}")

            except Exception as e:
                print(f"     Error reading file: {e}")

    def check_behavior_data(self):
        """Check E-Commerce Behavior Data"""
        print("\n" + Fore.YELLOW + "2. E-COMMERCE BEHAVIOR DATA" + Style.RESET_ALL)
        print("-" * 50)

        path = self.data_root / "2. E-Commerce Behavior Data (Multi-Category Store)"
        if not path.exists():
            print(Fore.RED + "  ✗ Directory not found" + Style.RESET_ALL)
            return

        csv_file = path / "2019-Oct.csv"
        if csv_file.exists():
            print(f"\n  📄 {csv_file.name}")
            size_mb = csv_file.stat().st_size / (1024 * 1024)
            print(f"     Size: {size_mb:.2f} MB")

            try:
                # Read sample
                df = pd.read_csv(csv_file, nrows=1000)
                print(f"     Columns: {', '.join(df.columns)}")
                print(f"     Sample rows: {len(df)}")

                # Get unique values
                if 'event_type' in df.columns:
                    event_types = df['event_type'].value_counts()
                    print(f"     Event types: {dict(event_types)}")

                # Estimate total rows
                with open(csv_file, 'r', encoding='utf-8') as f:
                    line_count = sum(1 for line in f) - 1  # Subtract header
                print(f"     Estimated total rows: {line_count:,}")

                self.stats['behavior_data'] = {
                    'rows': line_count,
                    'columns': list(df.columns),
                    'event_types': dict(event_types) if 'event_type' in df.columns else {}
                }

            except Exception as e:
                print(f"     Error reading file: {e}")
        else:
            print(Fore.RED + f"  ✗ 2019-Oct.csv not found" + Style.RESET_ALL)

    def check_customer_behavior(self):
        """Check Customer Behavior Dataset"""
        print("\n" + Fore.YELLOW + "3. CUSTOMER BEHAVIOR DATASET" + Style.RESET_ALL)
        print("-" * 50)

        path = self.data_root / "3. E-Commerce Customer Behavior Dataset"
        if not path.exists():
            print(Fore.RED + "  ✗ Directory not found" + Style.RESET_ALL)
            return

        csv_file = path / "E-commerce Customer Behavior - Sheet1.csv"
        if csv_file.exists():
            print(f"\n  📄 {csv_file.name}")
            size_mb = csv_file.stat().st_size / (1024 * 1024)
            print(f"     Size: {size_mb:.2f} MB")

            try:
                df = pd.read_csv(csv_file)
                print(f"     Shape: {df.shape[0]} rows × {df.shape[1]} columns")
                print(f"     Columns: {', '.join(df.columns[:5])}...")

                # Show data types
                print(f"     Data types: {df.dtypes.value_counts().to_dict()}")

                self.stats['customer_behavior'] = {
                    'rows': df.shape[0],
                    'columns': list(df.columns)
                }

            except Exception as e:
                print(f"     Error reading file: {e}")

    def check_uci_retail(self):
        """Check UCI Online Retail Dataset"""
        print("\n" + Fore.YELLOW + "4. UCI ONLINE RETAIL DATASET" + Style.RESET_ALL)
        print("-" * 50)

        path = self.data_root / "4. UCI Online Retail Dataset"
        if not path.exists():
            print(Fore.RED + "  ✗ Directory not found" + Style.RESET_ALL)
            return

        excel_file = path / "Online Retail.xlsx"
        if excel_file.exists():
            print(f"\n  📄 {excel_file.name}")
            size_mb = excel_file.stat().st_size / (1024 * 1024)
            print(f"     Size: {size_mb:.2f} MB")

            try:
                df = pd.read_excel(excel_file, nrows=1000)
                total_df = pd.read_excel(excel_file)

                print(f"     Shape: {total_df.shape[0]} rows × {total_df.shape[1]} columns")
                print(f"     Columns: {', '.join(df.columns)}")
                print(f"     Date range: {total_df['InvoiceDate'].min()} to {total_df['InvoiceDate'].max()}")
                print(f"     Unique customers: {total_df['CustomerID'].nunique():,}")
                print(f"     Unique products: {total_df['StockCode'].nunique():,}")
                print(f"     Countries: {total_df['Country'].nunique()}")

                self.stats['uci_retail'] = {
                    'rows': total_df.shape[0],
                    'customers': total_df['CustomerID'].nunique(),
                    'products': total_df['StockCode'].nunique()
                }

            except Exception as e:
                print(f"     Error reading file: {e}")

    def check_transactions(self):
        """Check E-Commerce Transactions (Synthetic)"""
        print("\n" + Fore.YELLOW + "5. E-COMMERCE TRANSACTIONS (SYNTHETIC)" + Style.RESET_ALL)
        print("-" * 50)

        path = self.data_root / "5. E-Commerce Transactions Dataset (Synthetic) - odd out"
        if not path.exists():
            print(Fore.RED + "  ✗ Directory not found" + Style.RESET_ALL)
            return

        csv_file = path / "ecommerce_transactions.csv"
        if csv_file.exists():
            print(f"\n  📄 {csv_file.name}")
            size_mb = csv_file.stat().st_size / (1024 * 1024)
            print(f"     Size: {size_mb:.2f} MB")

            try:
                df = pd.read_csv(csv_file, nrows=1000)
                print(f"     Columns: {', '.join(df.columns)}")

                # Full read for stats
                full_df = pd.read_csv(csv_file)
                print(f"     Total transactions: {len(full_df):,}")

                if 'TransactionID' in full_df.columns:
                    print(f"     Unique transactions: {full_df['TransactionID'].nunique():,}")
                if 'CustomerID' in full_df.columns:
                    print(f"     Unique customers: {full_df['CustomerID'].nunique():,}")

                self.stats['transactions'] = {
                    'rows': len(full_df),
                    'columns': list(df.columns)
                }

            except Exception as e:
                print(f"     Error reading file: {e}")

    def check_amazon_reviews(self):
        """Check Amazon Reviews for Sentiment Analysis"""
        print("\n" + Fore.YELLOW + "6. AMAZON REVIEWS FOR SENTIMENT ANALYSIS" + Style.RESET_ALL)
        print("-" * 50)

        path = self.data_root / "6. Amazon Reviews for Sentiment Analysis"
        if not path.exists():
            print(Fore.RED + "  ✗ Directory not found" + Style.RESET_ALL)
            return

        for txt_file in ['train.ft.txt', 'test.ft.txt']:
            file_path = path / txt_file
            if file_path.exists():
                print(f"\n  📄 {txt_file}")
                size_mb = file_path.stat().st_size / (1024 * 1024)
                print(f"     Size: {size_mb:.2f} MB")

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()[:5]

                    print(f"     Total lines: {len(open(file_path, encoding='utf-8').readlines()):,}")

                    # Check format (FastText format)
                    if lines:
                        if lines[0].startswith('__label__'):
                            labels = set()
                            for line in lines[:100]:
                                if line.startswith('__label__'):
                                    label = line.split(' ')[0]
                                    labels.add(label)
                            print(f"     Format: FastText")
                            print(f"     Labels found: {labels}")

                except Exception as e:
                    print(f"     Error reading file: {e}")

    def check_sales_data(self):
        """Check E-Commerce Sales Dataset"""
        print("\n" + Fore.YELLOW + "7. E-COMMERCE SALES DATASET" + Style.RESET_ALL)
        print("-" * 50)

        path = self.data_root / "7. E-Commerce Sales Dataset"
        if not path.exists():
            print(Fore.RED + "  ✗ Directory not found" + Style.RESET_ALL)
            return

        csv_files = list(path.glob("*.csv"))
        if not csv_files:
            print("  No CSV files found")
            return

        for csv_file in csv_files:
            print(f"\n  📄 {csv_file.name}")
            size_mb = csv_file.stat().st_size / (1024 * 1024)
            print(f"     Size: {size_mb:.2f} MB")

            try:
                df = pd.read_csv(csv_file, nrows=100)
                print(f"     Columns ({len(df.columns)}): {', '.join(df.columns[:5])}...")
                print(f"     Sample rows: {len(df)}")

            except Exception as e:
                print(f"     Error reading file: {e}")

    def print_summary(self):
        """Print summary statistics"""
        print("\n" + Fore.CYAN + "=" * 70)
        print("SUMMARY")
        print("=" * 70 + Style.RESET_ALL)

        summary_data = []

        # UCI Retail
        if 'uci_retail' in self.stats:
            summary_data.append([
                "UCI Retail",
                f"{self.stats['uci_retail']['rows']:,}",
                f"{self.stats['uci_retail']['customers']:,}",
                f"{self.stats['uci_retail']['products']:,}"
            ])

        # Behavior Data
        if 'behavior_data' in self.stats:
            summary_data.append([
                "Behavior Data",
                f"{self.stats['behavior_data']['rows']:,}",
                "TBD",
                "TBD"
            ])

        # Customer Behavior
        if 'customer_behavior' in self.stats:
            summary_data.append([
                "Customer Behavior",
                f"{self.stats['customer_behavior']['rows']:,}",
                "TBD",
                "N/A"
            ])

        # Transactions
        if 'transactions' in self.stats:
            summary_data.append([
                "Transactions",
                f"{self.stats['transactions']['rows']:,}",
                "TBD",
                "TBD"
            ])

        if summary_data:
            print(tabulate(summary_data,
                           headers=["Dataset", "Rows", "Customers", "Products"],
                           tablefmt="grid"))

        # Save statistics to file
        with open("data_statistics.txt", "w") as f:
            f.write("DATA STATISTICS REPORT\n")
            f.write("=" * 70 + "\n")
            f.write(f"Generated: {pd.Timestamp.now()}\n\n")

            for key, value in self.stats.items():
                f.write(f"\n{key}:\n")
                f.write(f"{json.dumps(value, indent=2, default=str)}\n")

        print("\n" + Fore.GREEN + "✅ Statistics saved to data_statistics.txt" + Style.RESET_ALL)
        print("\n" + Fore.YELLOW + "Ready to load data! Run: python load_first_data.py" + Style.RESET_ALL)


if __name__ == "__main__":
    checker = DataChecker()
    checker.check_all_datasets()