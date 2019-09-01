import re

import pandas as pd
import numpy as np


fname = 'CHURN DASHBOARD 2019.xlsx'

hierarchy_sheet_name = 'SALES HIERARCHY'
links_sheet_name = 'ASSET MIDI LINKS'
sla_sheet_name = 'TICKET PERFORMANCE SLA'
closed_ticket_sheet_name = 'CLOSED TICKET'
open_ticket_sheet_name = 'IN PROGRESS TICKET'

def read_excel(sheet_name):
    return pd.read_excel(fname, sheet_name)

def lowercase_column(col):
    return col.apply(lambda x: x.lower())

def load_hierarchy():
    df = read_excel(hierarchy_sheet_name).dropna(axis=1)
    for column in df.columns:
        df[column] = df[column].apply(lambda cell: re.sub('[^0-9a-zA-Z ]+', '', cell))
    return df

def load_links():
    df = read_excel(links_sheet_name)
    # Get rid of rows with null salespeople for now
    return  df[pd.notnull(df.SALES_NAME)]

def load_open_tickets():
    return read_excel(open_ticket_sheet_name)

def load_closed_tickets():
    return read_excel(closed_ticket_sheet_name)


links_df = read_excel(links_sheet_name)

links_df = links_df[links_df.SALES_NAME == links_df.SALES_NAME]

open_tickets = load_open_tickets()