import pandas as pd


def extract_table_as_dataframe(table_text: str) -> pd.DataFrame:
    """Convert a table into a DataFrame."""
    lines = table_text.strip().split('\n')
    rows = []
    for line in lines:
        if '|' in line:
            row = [cell.strip() for cell in line.split('|') if cell.strip()]
        else:
            row = [cell.strip() for cell in line.split('\t') if cell.strip()]
        if row:
            rows.append(row)
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows[1:], columns=rows[0])
    return df


def table_as_string(df: pd.DataFrame) -> str:
    """Create descriptive text for each row."""
    if df.empty:
        return ''
    descriptions = []
    for _, row in df.iterrows():
        desc = '. '.join([f'{col}: {row[col]}' for col in df.columns])
        descriptions.append(desc)
    return '\n'.join(descriptions)


table_example = """
| Product | Price | Quantity | Status |
| Laptop | 50000 | 5 | In stock |
| Monitor | 15000 | 3 | Limited |
| Keyboard | 5000 | 10 | In stock |
"""
df = extract_table_as_dataframe(table_example)

print('📊 Structured data:')
print(df.to_dict(orient='records'))
print('\n📝 Descriptive text:')
print(table_as_string(df))
