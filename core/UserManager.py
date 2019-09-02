import re

import pandas as pd
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class UserManager(object):
    def load_users(self, f):
        self.create_models(self.parse_file(f))

    def parse_file(self, f):
        df = pd.read_excel(f, settings.HIERARCHY_SHEET_NAME).dropna(axis=1, how='all')
        for column in df.columns:
            df[column] = df[column].apply(lambda cell: re.sub('[^0-9a-zA-Z ]+', '', cell) if not pd.isnull(cell) else cell)
        return df

    def _create_user_dict(self, row, level):
        hierarchy = settings.HIERARCHY_LEVEL_NAMES

        return dict(
            username=row[hierarchy[level - 1]],
            level=level,
            level_2_superior=getattr(row, hierarchy[1], None) if level < 2 else None,
            level_3_superior=getattr(row, hierarchy[2], None) if level < 3 else None,
            level_4_superior=getattr(row, hierarchy[3], None) if level < 4 else None,
            level_5_superior=getattr(row, hierarchy[4], None) if level < 5 else None,
            level_6_superior=getattr(row, hierarchy[5], None) if level < 6 else None,
        )





    def create_models(self, df):
        hierarchy = settings.HIERARCHY_LEVEL_NAMES

        created_names = set()
        new_user_data = list()

        for level in range(6, 0, -1):
            level_name = hierarchy[level - 1]
            if getattr(df, level_name, None) is None:
                continue

            for i, row in df.iterrows():
                uname = getattr(row, level_name)
                if uname in created_names:
                    continue
                new_user_data.append(self._create_user_dict(row, level))
                created_names.add(uname)









        updated_usernames = {u['username'] for u in new_user_data}

        for user in User.objects.filter(is_staff=False).all():
            if user.username not in updated_usernames:
                user.delete()

        users = User.objects.all()

        uname_map = {user.username: user for user in users}

        for user_data in new_user_data:
            try:
                existing_user = uname_map[user_data['username']]
            except KeyError:
                level_2_superior = uname_map.get(user_data['level_2_superior'])
                level_3_superior = uname_map.get(user_data['level_3_superior'])
                level_4_superior = uname_map.get(user_data['level_4_superior'])
                level_5_superior = uname_map.get(user_data['level_5_superior'])
                level_6_superior = uname_map.get(user_data['level_6_superior'])

                User.objects.create(
                    username=user_data['username'],
                    level=user_data['level'],
                    level_2_superior=level_2_superior,
                    level_3_superior=level_3_superior,
                    level_4_superior=level_4_superior,
                    level_5_superior=level_5_superior,
                    level_6_superior=level_6_superior,
                )
            else:
                existing_user.level_2_superior = uname_map.get(user_data['level_2_superior'])
                existing_user.level_3_superior = uname_map.get(user_data['level_3_superior'])
                existing_user.level_4_superior = uname_map.get(user_data['level_4_superior'])
                existing_user.level_5_superior = uname_map.get(user_data['level_5_superior'])
                existing_user.level_6_superior = uname_map.get(user_data['level_6_superior'])
                existing_user.level = user_data['level']
                existing_user.save()
