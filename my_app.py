import streamlit as st
import pandas as pd
from datetime import datetime
import numpy as np
from babel.numbers import format_currency
import io

percents_df = pd.read_excel('gamma.xlsx', sheet_name= 'betta')



def generate_lease_table(main_value, start_date_str, end_date_str):
    
    start_date = datetime.strptime(start_date_str, '%Y.%m.%d')
    end_date = datetime.strptime(end_date_str, '%Y.%m.%d')
    
    
    number_of_months = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month
    date_range = pd.date_range(start=start_date, periods=number_of_months, freq='M')
    
    df = pd.DataFrame({'date': date_range})
    df['main'] = main_value
    
    per = percents_df[percents_df['month'] == len(df['main'])]['percent'].iloc[0]
    df['percent'] = per
    df['month_count'] = df.index
    df['monthly_percent'] = df['percent'] / 12
    df['month_count'] = df['month_count'].astype('int')
    df['rent_pv'] = np.round(df['main'] / ((1 + df['monthly_percent']) ** df['month_count']))

    origin_list = []
    percen_list = []

    for i in df.index:
        if i == 0:
            origin = np.sum(df['rent_pv']) - df.loc[i, 'main']
            percen = origin * df.loc[i, 'monthly_percent']
        elif i > 0:
            origin = origin + percen - df.loc[i, 'main']
            percen = origin * df.loc[i, 'monthly_percent']
        origin_list.append(origin)
        percen_list.append(percen)

    df['main_amount'] = origin_list
    df['main_amount'] = df['main_amount'].astype(int)
    df['percentage_amount'] = percen_list
    df['percentage_amount'] = df['percentage_amount'].astype(int)
    
    df['amortization'] = np.round(np.sum(df['rent_pv']) / len(df['main']))
    df['amortization'] = df['amortization'].astype(int)
    df['accumulated_depr'] = np.cumsum(df['amortization'])
    
    currency_columns = ['main', 'rent_pv', 'main_amount', 'percentage_amount', 'amortization', 'accumulated_depr']
    for col in currency_columns:
        df[col] = df[col].apply(lambda x: format_currency(x, 'KRW', locale='ko_KR'))

    df.columns = ["Date",	"Initial Lease Liability",	"Annual Interest Rate",	"Month Count", "Monthly Interest",	"PV of Lease",	"Remaining Lease Liability",	"Interest Expense",	"Amortization",	"Accumulated Depreciation"]
    
    return df

def streamlit_app():
    st.title("Lease Table Generator")

    main_value = st.number_input("Enter the monthly main value:", min_value=0)
    start_date = st.text_input("Enter the start date (YYYY.MM.DD):", "2024.01.01")
    end_date = st.text_input("Enter the end date (YYYY.MM.DD):", "2030.12.31")

    if st.button("Generate Table"):
        try:
            df = generate_lease_table(main_value, start_date, end_date)
            st.write(df)

            towrite = io.BytesIO()
            df.to_excel(towrite, index=False) 
            towrite.seek(0)  
            link = st.download_button(label="Download Excel file", data=towrite, file_name="lease_table.xlsx", mime="application/vnd.ms-excel")
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    streamlit_app()
    
