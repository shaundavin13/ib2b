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

    def load_data(self, file):
        self.open_tickets_df = self.load_open_tickets(file)
        self.closed_tickets_df = self.load_closed_tickets(file)
        self.links_df = self.load_links(file)
        self._initialized = True
        self.save_pkl_data()

    def refresh(self):
        if not self._initialized:
            raise Exception('Cannot refresh what is not initialized. Doing so risks corrupted data')
        self.load_pkl_data()


    def _clean_service_id(self, df):
        df[settings.COLUMN_NAMES['service_id']] = df[settings.COLUMN_NAMES['service_id']].astype('str').apply(
            replace_slash)

    def load_open_tickets(self, f):
        df = pd.read_excel(f, self.sheet_names['open_tickets_df'])
        self._clean_service_id(df)
        return df

    def load_closed_tickets(self, f):
        df = pd.read_excel(f, self.sheet_names['closed_tickets_df'])
        self._clean_service_id(df)
        return df

    def load_links(self, f):
        df = pd.read_excel(f, self.sheet_names['links_df'])
        self._clean_service_id(df)
        return df
