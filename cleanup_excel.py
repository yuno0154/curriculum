import pandas as pd
import os

xlsx_path = '성취기준_추출결과.xlsx'
if os.path.exists(xlsx_path):
    df = pd.read_excel(xlsx_path)
    
    exclude_combos = [
        ('디지털과 직업 생활', '공화'),
        ('디지털과 직업 생활', '기계'),
    ]
    
    initial_count = len(df)
    
    # Filter out using boolean mask
    mask = df.apply(lambda row: any(
        row['subject'] == target_subj and str(row['code']).strip('[]').startswith(prefix)
        for target_subj, prefix in exclude_combos
    ), axis=1)
    
    df_cleaned = df[~mask]
    
    df_cleaned.to_excel(xlsx_path, index=False)
    print(f"Excel cleanup: {initial_count} -> {len(df_cleaned)}")
else:
    print("Excel not found")
