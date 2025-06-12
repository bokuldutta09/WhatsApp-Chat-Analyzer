from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
from datetime import datetime
import re
import emoji

extract = URLExtract()

def clean_messages(df):
    media_pattern = re.compile(r"<media omitted>|image omitted|video omitted|audio omitted|document omitted|message deleted|message edited|This message was deleted", re.I)
    df_clean = df[~df['message'].str.contains(media_pattern)]
    df_clean = df_clean[~df_clean['message'].str.contains("This message was deleted|deleted message", case=False)]
    df_clean = df_clean[df_clean['message'].str.contains(r'[a-zA-Z]', regex=True)]
    df_clean = df_clean.reset_index(drop=True)
    return df_clean

# Fetch chat statistics
def fetch_stats(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    num_messages = df.shape[0]
    words = []
    for message in df['message']:
        words.extend(message.split())
    media_patterns = r'(<media omitted>|image omitted|video omitted|audio omitted|document omitted|sticker omitted|message deleted|message edited|This message was deleted)'
    num_media_message = df[df['message'].str.lower().str.contains(media_patterns, na=False)].shape[0]
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))
    return num_messages, len(words), num_media_message, len(links)

# Most busy users
def most_busy_user(df):
    df = df[df['user'] != 'group_notification']
    if 'messages and calls are end-to-end encrypted' in df.iloc[0]['message'].lower():
        df = df.drop(df.index[0])
    x = df['user'].value_counts().head()
    percent_df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index()
    percent_df.columns = ['name', 'percent']
    return x, percent_df

# Create WordCloud
def create_word_cloud(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    df = df[df['user'] != "group_notification"]
    media_patterns = r'<media omitted>|image omitted|video omitted|audio omitted|document omitted|sticker omitted|sticker|deleted message|message deleted|message deleted|message edited|This message was deleted'
    df = df[~df['message'].str.lower().str.strip().str.contains(media_patterns, regex=True)]
    with open('stop_hinglish.txt', 'r') as f:
        stop_words = set(f.read().splitlines())
    user_list = set(u.lower() for u in df['user'].unique())
    cleaned_words = []
    for message in df['message']:
        message = re.sub(r'[^\w\s]', '', message)
        for word in message.lower().split():
            if word not in stop_words and word not in user_list:
                cleaned_words.append(word)
    cleaned_text = ' '.join(cleaned_words)
    wc = WordCloud(width=500, height=500, background_color='white').generate(cleaned_text)
    return wc


def most_common_words(selected_user, df):
    with open('stop_hinglish.txt', 'r') as f:
        stop_words = set(f.read().splitlines())
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    temp = df[df['user'] != "group_notification"]
    media_patterns = r'<media omitted>|image omitted|video omitted|audio omitted|document omitted|sticker omitted|sticker|deleted message|message deleted|message deleted|message edited|This message was deleted'
    temp = temp[~temp['message'].str.lower().str.strip().str.contains(media_patterns, regex=True)]
    user_list = set(u.lower() for u in df['user'].unique())
    words = []
    for message in temp['message']:
        # Remove punctuation
        message = re.sub(r'[^\w\s]', '', message)
        for word in message.lower().split():
            if word not in stop_words and word not in user_list:
                words.append(word)
    most_common_df = pd.DataFrame(Counter(words).most_common(20), columns=['word', 'count'])
    return most_common_df

# Emoji Analysis
def emoji_helper(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if emoji.is_emoji(c)])
    emoji_df = pd.DataFrame(Counter(emojis).most_common(), columns=['emoji', 'count'])
    return emoji_df

# Monthly timeline
def monthly_timeline(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    if df.empty:
        return pd.DataFrame()
    today = datetime.today()
    df = df[df['date'] <= today]
        
    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    timeline['time'] = timeline['month'] + "-" + timeline['year'].astype(str)
    return timeline

# Daily timeline
def daily_timeline(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    today = datetime.today()
    df = df[df['date'] <= today]
    return df.groupby('only_date').count()['message'].reset_index()

# Activity maps
def week_activity_map(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    return df['day_name'].value_counts()

def month_activity_map(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    return df['month'].value_counts()

def activity_heatmap(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    return df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)
