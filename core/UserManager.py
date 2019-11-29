import re

import pandas as pd
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

class UserManager(object):
    def load_users(self, dfs):
        self.create_models(self.parse_dfs(dfs))

    def parse_dfs(self, dfs):
        df = dfs[settings.HIERARCHY_SHEET_NAME].dropna(axis=1, how='all')
        for column in df.columns:
            df[column] = df[column].apply(lambda cell: re.sub('[^0-9a-zA-Z ]+', '', str(cell)) if not pd.isnull(cell) else cell)
        return df

    def _create_user_dict(self, uname, row, level):
        hierarchy = settings.HIERARCHY_LEVEL_NAMES
        nik_columns = settings.NIK_COLUMN_NAMES

        return dict(
            username=uname,
            name=row[hierarchy[level - 1]],
            level=level,
            level_2_superior=getattr(row, nik_columns[1], None) if level < 2 else None,
            level_3_superior=getattr(row, nik_columns[2], None) if level < 3 else None,
            level_4_superior=getattr(row, nik_columns[3], None) if level < 4 else None,
            level_5_superior=getattr(row, nik_columns[4], None) if level < 5 else None,
            level_6_superior=getattr(row, nik_columns[5], None) if level < 6 else None,
        )

    def create_models(self, df):
        hierarchy = settings.HIERARCHY_LEVEL_NAMES
        nik_columns = settings.NIK_COLUMN_NAMES

        created_names = set()
        new_user_data = list()

        for level in range(6, 0, -1):
            level_name = hierarchy[level - 1]
            nik_column_name = nik_columns[level - 1]
            if getattr(df, level_name, None) is None:
                continue

            for i, row in df.iterrows():
                uname = getattr(row, nik_column_name)
                if uname in created_names:
                    continue

                if str(uname) == 'nan':
                    continue

                new_user_data.append(self._create_user_dict(uname, row, level))
                created_names.add(uname)

        updated_usernames = {u['username'] for u in new_user_data}

        users = User.objects.filter(is_staff=False).all()
        for user in users:
            # if user.username not in updated_usernames:
            if user.username != 'shaundavin13':
                user.delete()

        uname_map = {user.username: user for user in users}


        with transaction.atomic():

            for user_data in new_user_data:
                try:
                    existing_user = uname_map[user_data['username']]
                except KeyError:
                    level_2_superior = uname_map[user_data['level_2_superior']] if not pd.isnull(user_data['level_2_superior']) else None
                    level_3_superior = uname_map[user_data['level_3_superior']] if not pd.isnull(user_data['level_3_superior']) else None
                    level_4_superior = uname_map[user_data['level_4_superior']] if not pd.isnull(user_data['level_4_superior']) else None
                    level_5_superior = uname_map[user_data['level_5_superior']] if not pd.isnull(user_data['level_5_superior']) else None
                    level_6_superior = uname_map[user_data['level_6_superior']] if not pd.isnull(user_data['level_6_superior']) else None

                    user = User.objects.create(
                        name=user_data['name'],
                        username=user_data['username'],
                        level=user_data['level'],
                        level_2_superior=level_2_superior,
                        level_3_superior=level_3_superior,
                        level_4_superior=level_4_superior,
                        level_5_superior=level_5_superior,
                        level_6_superior=level_6_superior,
                    )

                    user.set_password(settings.DEFAULT_PASSWORD)
                    user.save()

                    uname_map[user_data['username']] = user
                else:
                    existing_user.level_2_superior = uname_map.get(user_data['level_2_superior'])
                    existing_user.level_3_superior = uname_map.get(user_data['level_3_superior'])
                    existing_user.level_4_superior = uname_map.get(user_data['level_4_superior'])
                    existing_user.level_5_superior = uname_map.get(user_data['level_5_superior'])
                    existing_user.level_6_superior = uname_map.get(user_data['level_6_superior'])
                    existing_user.level = user_data['level']
                    existing_user.save()
