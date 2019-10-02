import os
import pickle as pkl

import pandas as pd
from django.conf import settings

def replace_slash(s):
    return s.replace('/', '%2F')

class DataManager(object):

    sheet_names = settings.SHEET_NAMES
    def __init__(self):
        self.links_df = None
        self.open_tickets_df = None
        self.closed_tickets_df = None

        self.load_pkl_data()

        self._initialized = all(df is not None for df in (self.links_df, self.open_tickets_df, self.closed_tickets_df))

    def load_pkl_data(self):
        for name, fname in settings.PKL_FILENAMES.items():
            full_path = os.path.join(settings.BASE_DIR, settings.PKL_CACHE_DIR, fname)
            if os.path.exists(full_path):
                with open(full_path, 'rb') as f:
                    setattr(self, name, pkl.load(f))

    def save_pkl_data(self):
        for name, fname in settings.PKL_FILENAMES.items():
            with open(os.path.join(settings.BASE_DIR, settings.PKL_CACHE_DIR, fname), 'wb') as f:
                d = getattr(self, name)
                pkl.dump(d, f)

    def load_data(self, dfs):
        self.open_tickets_df = self.load_open_tickets(dfs)
        self.closed_tickets_df = self.load_closed_tickets(dfs)
        self.links_df = self.load_links(dfs)
        self._initialized = True
        self.save_pkl_data()

    def refresh(self):
        if not self._initialized:
            raise Exception('Cannot refresh what is not initialized. Doing so risks corrupted data')
        self.load_pkl_data()


    def _clean_service_id(self, df):
        df[settings.COLUMN_NAMES['service_id']] = df[settings.COLUMN_NAMES['service_id']].astype('str').apply(
            replace_slash)

    def load_open_tickets(self, dfs):
        df = dfs[self.sheet_names['open_tickets_df']]
        self._clean_service_id(df)
        return df

    def load_closed_tickets(self, dfs):
        df = dfs[self.sheet_names['closed_tickets_df']]
        self._clean_service_id(df)
        return df

    def load_links(self, dfs):
        df = dfs[self.sheet_names['links_df']]
        self._clean_service_id(df)
        df['BA_NUMBER'] = df['BA_NUMBER'].apply(lambda x: str(x)).astype('str')

        return df
