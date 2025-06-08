from streamlit import columns
from urlextract import URLExtract
extract = URLExtract()

from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import re
import emoji


def fetch_stats(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    # Number of messages
    num_messages = df.shape[0]

    # Number of words
    words = []
    for message in df['message']:
        words.extend(message.split())

    # Number of media messages
    media_keywords = ['image omitted', 'video omitted', 'audio omitted']
    num_media_message = df[df['message'].str.lower().isin(media_keywords)].shape[0]

    # Number of links shared
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    return num_messages, len(words), num_media_message, len(links)



def most_busy_user(df):
    x = df['user'].value_counts().head()
    percent_df = round((df['user'].value_counts()/df.shape[0])*100, 2).reset_index()
    percent_df.columns = ['name', 'percent']
    return x, percent_df



def create_word_cloud( selected_user ,df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    df = df[df['user'] != "group_notification"]
    media_omitted = ['image omitted', 'video omitted', 'audio omitted', 'document omitted', 'sticker omitted']
    df = df[~df['message'].str.lower().str.strip().isin(media_omitted)]
    with open('stop_hinglish.txt', 'r') as f:
        stop_words = set(f.read().splitlines())

    def clean_message(msg):
        msg = re.sub(r'[^\w\s]', '', msg)  # remove punctuation
        msg = msg.lower().strip()
        return ' '.join([word for word in msg.split() if word not in stop_words])

    cleaned_text = df['message'].apply(clean_message).str.cat(sep=' ')



    wc = WordCloud(width=500, height=500, background_color='white')
    df_wc = wc.generate(df['message'].str.cat(sep=" "))
    return df_wc



def most_common_words(selected_user, df):
    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()

    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != "group_notification"]

    def clean_text(msg):
        msg = re.sub(r'[^\w\s]', '', msg)  # remove punctuation
        return msg.strip().lower()

    media_omitted = ['image omitted', 'video omitted', 'audio omitted', 'document omitted', 'sticker omitted']
    temp = temp[~temp['message'].str.lower().str.strip().isin(media_omitted)]


    words = []
    for message in temp['message']:
        message = clean_text(message)
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_df




def emoji_helper(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if emoji.is_emoji(c)])
    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    return emoji_df



def monthly_timeline(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))
    timeline['time']  = time

    return timeline



def daily_timeline(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby(['only_date']).count()['message'].reset_index()

    return daily_timeline




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

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap













    # if selected_user == "Overall":
    #     # 1. Number of messages
    #     num_messages = df.shape[0]
    #
    #     # 2. number of words
    #     words = []
    #     for message in df['message']:
    #         words.extend(message.split())
    #
    #     return num_messages, len(words)
    #
    # else:
    #     new_df = df[df['user'] == selected_user]
    #     num_messages = new_df.shape[0]
    #     words = []
    #     for message in new_df['message']:
    #         words.extend(message.split())
    #     return num_messages, len(words)