import re
import pandas as pd
import unicodedata

def clean_message(msg):
    if isinstance(msg, str):
        msg = unicodedata.normalize('NFKD', msg)
        msg = re.sub(r'[\u200e\u202a\u202c\u2066\u2069]', '', msg)
        return msg.strip()
    return msg


def preprocess(data):
    android_pattern = r'(\d{2}/\d{2}/\d{2,4}), (\d{2}:\d{2}) - (.*?): (.*)'
    iphone_pattern = r'\[*(\d{2}/\d{2}/\d{2,4}), (\d{2}:\d{2}:\d{2})\]\s?(.*?): (.+)'

    android_matches = re.findall(android_pattern, data)
    iphone_matches = re.findall(iphone_pattern, data)

    if iphone_matches:
        format_type = 'iphone'
        matches = iphone_matches
    elif android_matches:
        format_type = 'android'
        matches = android_matches
    else:
        raise ValueError("Chat format not recognized")

    datetime_list = []
    name_message_list = []


    for match in matches:
        date, time, name, message = match
        datetime = f"{date} {time}"
        name_message = f"{name}: {message}"

        datetime_list.append(datetime)
        name_message_list.append(name_message)

    df = pd.DataFrame({'user_message': name_message_list, 'message_date': datetime_list})

    date_format = '%d/%m/%y %H:%M:%S' if format_type == 'iphone' else '%d/%m/%y %H:%M'
    df['message_date'] = pd.to_datetime(df['message_date'], format=date_format, errors='coerce')
    df.rename(columns={'message_date': 'date'}, inplace=True)

    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df['message'] = df['message'].apply(clean_message)
    df.drop(columns=['user_message'], inplace=True)
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute
    df['day_name'] = df['date'].dt.day_name()


    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append("23-00")
        elif hour == 0:
            period.append("00-01")
        else:
            period.append(f"{hour:02d}-{(hour + 1) % 24:02d}")
    df['period'] = period


    return df
