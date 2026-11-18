import pandas as pd
import os

def create_guests_excel():
    data = {
        'GuestID': [1, 2, 3, 4, 5],
        'Name': ['Ahmed Ali', 'Sara Ahmed', 'Khaled Saad', 'Mohammed Omar', 'Noura Faisal'],
        'Nationality': ['Saudi', 'Egyptian', 'Saudi', 'Emirati', 'Kuwaiti'],
        'Phone': ['0501234567', '0549876543', '0591112233', '0555554444', '0533332222'],
        'Total_Spent': [1500, 300, 2500, 900, 1200]
    }
    
    df = pd.DataFrame(data)
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    excel_path = os.path.join('data', 'guests.xlsx')
    df.to_excel(excel_path, index=False)
    print(f"Excel file created at {excel_path}")

if __name__ == "__main__":
    create_guests_excel()
