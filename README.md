# OOS Data Processor

A lightweight Streamlit web application designed to process and filter order data (Data A) based on inventory availability (Data B).

## 🚀 Key Features

1. **Flexible Upload**: Supports both Excel (.xlsx) and CSV formats for Data A and Data B.
2. **Auto-Filtering (Data A)**:
   - Automatically excludes rows where **Column X** contains the keywords "PreSale" or "OnlineShip" (case-insensitive).
3. **Inventory Cross-Reference (Data B)**:
   - Matches **Column AQ** (from Data A) with **Column B** (from Data B).
   - Retains records only if **Column E** (in Data B) shows `0` (Zero Inventory).
4. **Clean Export**: Generates a downloadable Excel file containing only the required columns:
   - A, B, C, K, L, N, X, Z, AQ, CA, CB, CC.

## 🛠️ How to Run (Local)

1. Ensure Python is installed on your machine.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
