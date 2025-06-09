import re
import pandas as pd
import unicodedata
from datetime import datetime

def clean_message(msg):
    if isinstance(msg, str):
        msg = unicodedata.normalize('NFKD', msg)
        msg = re.sub(r'[\u200e\u202a\u202c\u2066\u2069]', '', msg)
        return msg.strip()
    return msg

def preprocess(data):
    android_pattern = re.compile(
        r'^(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)?)\s*-\s+(.*?):\s(.*)$'
    )

    ios_pattern = re.compile(
        r'\[(\d{2}/\d{2}/\d{2,4}), (\d{2}:\d{2}:\d{2})\] (.*?): (.+)'
    )

    messages = []
    current_message = None
    for line in data.split('\n'):
        line = line.strip()
        if ios_pattern.match(line) or android_pattern.match(line):
            if current_message:
                messages.append(current_message)
            current_message = line
        else:
            if current_message:
                current_message += ' ' + line 
            else:
                continue

    if current_message:
        messages.append(current_message)
        
    dates, users, texts = [], [], []
    
    for message in messages:
        ios_match = ios_pattern.match(message)
        android_match = android_pattern.match(message)
        if ios_match:
            date_str, time_str, user, text = ios_match.groups()
            datetime_str = f"{date_str} {time_str}"
            dates.append(datetime_str)
            users.append(user)
            texts.append(text)
        elif android_match:
            date_str, time_str, user, text = android_match.groups()
            datetime_str = f"{date_str} {time_str}"
            dates.append(datetime_str)
            users.append(user)
            texts.append(text)
        else:
            dates.append(None)
            users.append('group_notification')
            texts.append(message)

    df = pd.DataFrame({'datetime': dates, 'user': users, 'message': texts})
    
    def try_parsing_datetime(s):
        for fmt in ("%d/%m/%Y %I:%M:%S %p", "%d/%m/%Y %H:%M:%S", "%d/%m/%y %H:%M:%S", "%d/%m/%Y %I:%M %p",
                    "%d/%m/%Y %H:%M"):
            try:
                return pd.to_datetime(s, format=fmt, dayfirst=True)
            except:
                pass
        return pd.to_datetime(s, dayfirst=True, errors='coerce', infer_datetime_format=True)

    df['date'] = df['datetime'].apply(try_parsing_datetime)
    df = df.dropna(subset=['date'])
    df['message'] = df['message'].apply(clean_message)
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
        if pd.isna(hour):
            period.append("Unknown")
        else:
            hour = int(hour)
            period.append(f"{hour:02d}-{(hour + 1) % 24:02d}")
    df['period'] = period
    df.drop(columns=['datetime'], inplace=True)
    return df
