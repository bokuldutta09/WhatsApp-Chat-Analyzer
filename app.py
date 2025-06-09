import streamlit as st
import preprocessor, helper
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from helper import most_common_words
from datetime import timedelta

st.set_page_config(
    page_title="Chat Analysis",
    page_icon="🚀"
)

st.sidebar.title("Whatsapp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file", type=["txt"])
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    # st.text(data)
    df = preprocessor.preprocess(data)

    min_date = df['only_date'].min()
    max_date = df['only_date'].max()
    date_range_days = (max_date - min_date).days + 1


    # Remove group notification
    def is_group_notification(msg):
        patterns = [
            "added", "removed", "changed the subject to",
            "joined", "left", "created group", "encryption",
            "changed this group's icon", "changed the group description",
            "deleted this message", "removed this message"
        ]
        return any(p in msg.lower() for p in patterns)
    df = df[df['user'].notnull() & ~df['message'].apply(is_group_notification)]
    # st.dataframe(df)

    # Fetch unique user
    df = df[df['user'] != 'group_notification']
    if 'messages and calls are end-to-end encrypted' in df.iloc[0]['message'].lower():
        df = df.drop(df.index[0]).reset_index(drop=True)
    user_list = df['user'].unique().tolist()
    user_list.sort()
    user_list.insert(0, 'Overall')
    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

    if st.sidebar.button("Show Analysis"):

        # Stats Area
        num_messages, words, num_media_message, num_links = helper.fetch_stats(selected_user, df)

        st.title("Top Statistics")
        col1, col2, col3, col4 =  st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Total Media Shared")
            st.title(num_media_message)
        with col4:
            st.header("links Shared")
            st.title(num_links)

        # Monthly timeline
        if date_range_days > 60:
            st.title("Monthly Timeline")
            timeline = helper.monthly_timeline(selected_user, df)
            fig, ax = plt.subplots()
            ax.plot(timeline['time'], timeline['message'], color='green')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

            st.title("Daily Timeline")
            daily_timeline = helper.daily_timeline(selected_user, df)
            fig, ax = plt.subplots()
            ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        elif date_range_days > 7:
            st.info("Short dataset detected (less than 2 months). Showing Daily Timeline only.")
            st.title("Daily Timeline")
            daily_timeline = helper.daily_timeline(selected_user, df)
            fig, ax = plt.subplots()
            ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='blue')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        else:
            st.info("Very short dataset (≤ 1 week). Skipping timeline charts.")

        # Activity week map
        if date_range_days > 60:
            st.title("Activity Map")
            col1, col2 = st.columns(2)

            with col1:
                st.header("Most Busy Day")
                busy_day  = helper.week_activity_map(selected_user, df)
                fig, ax = plt.subplots()
                ax.bar(busy_day.index, busy_day.values)
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            with col2:
                st.header("Most Busy Month")
                busy_month = helper.month_activity_map(selected_user, df)
                fig, ax = plt.subplots()
                ax.bar(busy_month.index, busy_month.values, color = 'orange')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
        else:
            st.warning("Very short dataset (≤ 1 week). Skipping Activity map charts.")

        # Heatmap
        if date_range_days > 7:
            st.title("Weekly activity map")
            user_heatmap = helper.activity_heatmap(selected_user, df)
            fig, ax = plt.subplots()
            ax = sns.heatmap(user_heatmap)
            st.pyplot(fig)
        else:
            st.info("Not enough data for weekly heatmap (≤ 1 week).")

        # Finding the busiest users in the group(Group level)
        if selected_user == 'Overall':
            st.title("Most Busy User")

            x, percent_df = helper.most_busy_user(df)
            fig, ax = plt.subplots()

            col1, col2 = st.columns(2)
            with col1:
                ax.bar(x.index, x.values, color = 'red')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(percent_df)

        #WordCloud
        st.title("WordCloud")
        df_wc = helper.create_word_cloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        ax.axis('off')
        st.pyplot(fig)

        #Most Common words
        st.title("Most Common Words")
        most_common_df = helper.most_common_words(selected_user, df)
        fig, ax = plt.subplots()
        ax.barh(most_common_df['word'], most_common_df['count'], color='purple')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Emoji analysis
        st.title("Emoji Analysis")
        emoji_df = helper.emoji_helper(selected_user, df)

        col1, col2 = st.columns(2)
        with col1:
            st.header('List')
            st.dataframe(emoji_df)
        with col2:
            st.header('Pie Chart')
            fig, ax = plt.subplots()
            ax.pie(emoji_df['count'].head(), labels=emoji_df['emoji'].head(), autopct='%0.2f', shadow=False, startangle=90)
            ax.axis('equal')
            st.pyplot(fig)
