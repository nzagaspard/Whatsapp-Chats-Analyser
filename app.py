#importing important libraries
import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')
import emoji
import numpy as np
from datetime import datetime, time, timedelta
from collections import Counter
from PIL import Image
import plotly.express as px
from faker import Faker
from  wordcloud import WordCloud, STOPWORDS

st.sidebar.title('NAVIGATION')
st.sidebar.header('Source')
use_file = st.sidebar.radio('Choose the file you want to use', ['Default', 'My File (Upload)'])
# date1 = st.sidebar.date_input('Choose Starting date')
# date2 = st.sidebar.date_input('Choose the Ending date')
st.sidebar.header('Analysis/Visualizations')
stats = st.sidebar.selectbox('Choose what you want to analysize/visualize', 
                             ['','Overall Summary', 'Conversation over time', 'Daily Distribution', 'Hourly Distribution',
                              'Messages/Links/Media', 'Emojis', 'Most used words (WordCloud)'])
    
hide_st_style = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)
#st.markdown("<footer style='text-align: center; color: red;'>Some title</footer>", unsafe_allow_html=True)
description = """WhatsApp has found many use cases beyond keeping us in touch such as marketing & customer support, education & research, ... 
This application analyses WhatsApp chats (a group chat or two-way conversation) and shows time series trends, most active hours/days/people, most common used words, emojis, ...

**To export a particular chat** 

1. Open the individual or group chat.
2. Tap on 3 vertical dots in top right corner > More > Export chat.
3. Choose export without media (this gives you around 40000 last messages) and where to store/send the exported chat file."""
#st.set_option('deprecation.showfileUploaderEncoding', False)   
def main():
    #photo = "C:\\DataScience\\Dashboards\\Whatsapp Chat Analyzer.jpg"
    #image = Image.open(photo)
    st.write('# Whatsapp Chats Analyser')
    
    data = loading_data()    
    
    if data is not None:
        
        if use_file == 'Default':
            messages_df = data
            messages_df.sort_values(by='Date', inplace=True)
            all_emojis = list([a for b in messages_df['Emojis'] for a in b])
            emojis = dict(Counter(all_emojis))
            emojis_df = pd.DataFrame({'Emoji': list(emojis.keys()), 'Total': list(emojis.values())})
            messages_df['Date'] = messages_df['Date'].astype('datetime64[ns]')
        else:
            messages_df, emojis_df = clean_data(data)
        
        media_messages = messages_df[messages_df['Message'] == '<Media omitted>']
        deleted_messages = messages_df[messages_df['Message'] == 'This message was deleted']
        messages = messages_df[(messages_df['Message'] != '<Media omitted>') & (messages_df['Message'] != 'This message was deleted')]

        
        first_date = messages_df['Date'].min()
        late_date = messages_df['Date'].max()
                    
        sd = messages_df['Date'].min()
        ed = messages_df['Date'].max()

        if stats == '':
            st.write('## Cleaned Dataframe')
            st.write(messages_df)
        
        if stats == 'Overall Summary':
                        
            dates_chooser = st.slider( "Choose the desired range", min_value = datetime(sd.year, sd.month, sd.day), 
                              max_value = datetime(ed.year, ed.month, ed.day), step = timedelta(days =1), format="DD/MM/YYYY",
                             value = (datetime(sd.year, sd.month, sd.day), datetime(ed.year, ed.month, ed.day)))
           
            messages_df = messages_df[(messages_df['Date'] >= dates_chooser[0]) & (messages_df['Date'] <= dates_chooser[1])]
            messages = messages[(messages['Date'] >= dates_chooser[0]) & (messages['Date'] <= dates_chooser[1])]
            deleted_messages = deleted_messages[(deleted_messages['Date'] >= dates_chooser[0]) & (deleted_messages['Date'] <= dates_chooser[1])]
           
            
            total_messages = messages_df.shape[0]
            text_messages = messages.shape[0]
            total_deleted = deleted_messages.shape[0]
            total_media = messages_df[messages_df['Message'] == '<Media omitted>'].shape[0]
            total_words = messages['Number of Words'].sum()
            unique_words = len(set(' '.join(messages['Message']).split()))
            total_participants = len(messages_df['Sender'].unique())
            total_links = messages_df['Number of Links'].sum()
            total_emojis = messages_df['Number of Emojis'].sum()
            unique_emojis = len(emojis_df['Emoji'].unique())
            statistics = {'Total Participants: ':total_participants, 'Unique Emojis: ': unique_emojis, 'Total Emojis: ':total_emojis,
            'Total Links: ':total_links,  'Unique Words: ': unique_words, 'Total Words: ': total_words, 
            'Deleted Messages: ':total_deleted,  'Medias Messages: ':total_media, 'Text Messages: ':text_messages,
            'Total Messages: ':total_messages}
 

            fig1 = plt.figure(figsize = (10,10))
            colors = ['orangered','slategray', 'gray','chocolate', 'green','darkgreen','royalblue','blue','mediumblue','navy']
            plt.barh(range(0,10), 1, color = colors)
            plt.text(0.5,0.85,'{:%d/%m/%Y} - {:%d/%m/%Y}: Overall Summary'.format(dates_chooser[0], dates_chooser[1]), weight = 'bold', fontsize = 25, alpha = .75,
                        transform=plt.gcf().transFigure, ha='center', fontname='Comic Sans MS');
            for i,key in enumerate(statistics):
                plt.text(0.03,i-0.25,'{}{:,}'.format(key,statistics[key]), fontsize = 30, color = 'white', weight = 'bold')
            plt.xticks([]);
            plt.yticks([]);
            plt.xlim(0,0.9);
            st.pyplot(fig1, bbox_inches = 'tight')

        if stats == 'Conversation over time':

            dates = st.slider( "Choose the desired range", min_value = datetime(sd.year, sd.month, sd.day), 
                              max_value = datetime(ed.year, ed.month, ed.day), step = timedelta(days =1), format="DD/MM/YYYY",
                             value = (datetime(sd.year, sd.month, sd.day), datetime(ed.year, ed.month, ed.day)))
           
            daily_data = messages_df[(messages_df['Date'] >= dates[0]) & (messages_df['Date'] <= dates[1])] 
            daily_total = daily_data['Date'].value_counts().sort_index()
            fig2 = plt.figure(figsize=(15,10))
            plt.plot(daily_total, marker = '.', markersize = 10, color = 'blue')
            plt.text(0.5,0.9,'{:%d/%m/%Y} - {:%d/%m/%Y}: Messages over time'.format(dates[0], dates[1]), weight = 'bold', 
                     fontsize = 25, alpha = .75, transform=plt.gcf().transFigure, ha='center', fontname='Comic Sans MS');
            plt.xlabel('Date', fontsize = 20)
            plt.ylabel("Total messages", fontsize = 20)
            #plt.xlim(dates[0], dates[1])
            #plt.ylim(0,1200)
            st.pyplot(fig2, bbox_inches = 'tight')


        if stats == 'Daily Distribution':
            iminsi = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            weekly_total = messages_df['Day Number'].value_counts(dropna=False).sort_index()
            indexes = np.linspace(0,len(weekly_total)-1,7).astype(int)
            ticks = weekly_total.index[indexes]
            fig3 = plt.figure(figsize = (15,10))
            plt.bar(weekly_total.index, weekly_total)
            plt.xticks(ticks, iminsi)
            #plt.ylim(0,6050)
            plt.text(0.5,0.9,'{:%d/%m/%Y} - {:%d/%m/%Y}: Daily messages/Day of week effect'.format(sd, ed), weight = 'bold', fontsize = 25, alpha = .75, transform=plt.gcf().transFigure, ha='center', fontname='Comic Sans MS');
            plt.xlabel("Day", fontsize = 20);
            plt.ylabel("Total messages", fontsize = 20);
            st.pyplot(fig3, bbox_inches = 'tight')

        if stats == 'Hourly Distribution':
            hours = st.slider("Choose the hours of interest:", value=(time(00, 00), time(23,59)))
            hourly_data = messages_df[(messages_df['Time'] >= str(hours[0])) & (messages_df['Time']<= str(hours[1]))]
            hourly_total = hourly_data['Time'].value_counts().sort_index()
            fig4 = plt.figure(figsize = (15,10))
            plt.plot(hourly_total)
            indexes = np.linspace(0,len(hourly_total)-1,12).astype(int)
            ticks = hourly_total.index[indexes]
            labels = hourly_total.index[indexes]
            plt.xticks(ticks,labels);
            plt.xlim(-2,len(hourly_total)+1);
            #plt.ylim(-1,71)
            plt.text(0.5,0.9,"{:%d/%m/%Y} - {:%d/%m/%Y}: Hourly Messages/Hour of day effect ({:%H:%M} - {:%H:%M})".format(sd, ed, hours[0], hours[1]), weight = 'bold', fontsize = 25, alpha = .75, transform=plt.gcf().transFigure, ha='center', fontname='Comic Sans MS');
            plt.xlabel("Time (Hour)", fontsize = 20);
            plt.ylabel("Total Messages", fontsize = 20);
            st.pyplot(fig4, bbox_inches = 'tight')
            #st.write("You're viewing the chats between {:%H:%M} and {:%H:%M}".format(hours[0], hours[1]))

        if stats == 'Messages/Links/Media':
            top_chooser = st.selectbox('Choose Top', range(5,55,5), index = 1)
            messages_chooser = st.sidebar.radio('Select below',['Top message senders','Top media senders', 'Top links senders', 'Top deleter'])
            if messages_chooser == 'Top message senders':
                top30 = messages_df['Sender'].value_counts()[:int(top_chooser)]
                fig5 = plt.figure(figsize = (15,15))
                plt.text(0.5,0.9, "{:%d/%m/%Y} - {:%d/%m/%Y}: Top {} Messages Senders".format(sd, ed, top_chooser), weight = 'bold', fontsize = 25, alpha = .75, transform=plt.gcf().transFigure, ha='center', fontname='Comic Sans MS');
                plt.barh(top30.sort_values().index, top30.sort_values().values)
                plt.ylabel("Name/Number", fontsize = 20);
                plt.xlabel("Total Messages", fontsize = 20);
                st.pyplot(fig5, bbox_inches = 'tight')
                                                
            if messages_chooser == 'Top links senders':
                #top_chooser = st.selectbox('Choose a number (Top 10 by Default)', range(5,55,5), index = 1)
                top30_links = messages_df.groupby('Sender').sum().sort_values(by='Number of Links', ascending = False)[:int(top_chooser)]
                top30_links = top30_links['Number of Links']
                fig6 = plt.figure(figsize = (15,15))
                plt.text(0.5,0.9, "{:%d/%m/%Y} - {:%d/%m/%Y}: Top {} Links Senders".format(sd, ed, top_chooser), weight = 'bold', fontsize = 25, alpha = .75, transform=plt.gcf().transFigure, ha='center', fontname='Comic Sans MS');
                plt.barh(top30_links.sort_values().index, top30_links.sort_values().values)
                plt.ylabel("Name/Number", fontsize = 20);
                plt.xlabel("Total Messages", fontsize = 20);
                st.pyplot(fig6, bbox_inches = 'tight')

            if messages_chooser == 'Top media senders':
                #top_chooser = st.selectbox('Choose a number (Top 10 by Default)', range(5,55,5), index = 1)
                top30_medias = media_messages['Sender'].value_counts()[:int(top_chooser)]
                fig7 = plt.figure(figsize = (15,15))
                plt.text(0.5,0.9, "{:%d/%m/%Y} - {:%d/%m/%Y}: Top {} Photos/Videos/Audios/Stickers Senders".format(sd, ed, top_chooser), weight = 'bold', fontsize = 25, alpha = .75,transform=plt.gcf().transFigure, ha='center', fontname='Comic Sans MS');
                plt.barh(top30_medias.sort_values().index, top30_medias.sort_values().values)
                plt.ylabel("Name/Number", fontsize = 20);
                plt.xlabel("Total media", fontsize = 20);
                st.pyplot(fig7,bbox_inches = 'tight')

            if messages_chooser == 'Top deleter':
                #top_chooser = st.selectbox('Choose a number (Top 10 by Default)', range(5,55,5), index = 1)
                top30_deleted = deleted_messages['Sender'].value_counts()[:int(top_chooser)]
                fig8 = plt.figure(figsize = (15,15))
                plt.text(0.5,0.9, "{:%d/%m/%Y} - {:%d/%m/%Y}: Top {} messages deleter".format(sd, ed, top_chooser), weight = 'bold', fontsize = 25, alpha = .75,
                            transform=plt.gcf().transFigure, ha='center', fontname='Comic Sans MS');
                plt.barh(top30_deleted.sort_values().index, top30_deleted.sort_values().values)
                plt.ylabel("Name/Number", fontsize = 20);
                plt.xlabel("Total messages", fontsize = 20);
                st.pyplot(fig8, bbox_inches = 'tight')
            

        if stats == 'Emojis':
            
            emojis_chooser = st.sidebar.radio('Choose',['Top emojis users', 'Top used emojis (distribution)'])
            #if st.sidebar.button('Top Emojis'):
            if emojis_chooser == 'Top emojis users':
                top_chooser = st.selectbox('Choose a number (Top 10 by Default)', range(5,55,5), index = 1)
                top30_emojis = messages_df.groupby('Sender').sum().sort_values(by='Number of Emojis', ascending = False)[:int(top_chooser)]
                top30_emojis = top30_emojis['Number of Emojis']
                fig9 = plt.figure(figsize = (15, 15))
                plt.text(0.5,0.9, "{:%d/%m/%Y} - {:%d/%m/%Y}: Top {} Emojis Users".format(sd, ed, top_chooser), weight = 'bold', fontsize = 25, alpha = .75, transform=plt.gcf().transFigure, ha='center', fontname='Comic Sans MS');
                plt.barh(top30_emojis.sort_values().index, top30_emojis.sort_values().values)
                plt.ylabel("Name/Number", fontsize = 20);
                plt.xlabel("Total emojis", fontsize = 20);
                st.pyplot(fig9,bbox_inches = 'tight')
                
           # if st.sidebar.button('Emojis usage distribution'):
            if emojis_chooser == 'Top used emojis (distribution)':
                fig10 = px.pie(emojis_df, values='Total', names='Emoji',
                title="{:%d/%m/%Y} - {:%d/%m/%Y}: Emojis' Usage Distribution".format(sd, ed), width = 800, height = 800)
                fig10.update_traces(textposition='inside', textinfo='percent+label')
                fig10.update_layout(showlegend=False, titlefont = {'family': 'Comic Sans MS','size':20, 'color':'black'})
                st.write(fig10)

        if stats == 'Most used words (WordCloud)':
            senders = list(messages_df['Sender'].unique())
            senders.insert(0,'All')
            person_chooser = st.selectbox('Choose the people',senders)
            if person_chooser == 'All':
                text_messages = ' '.join(messages['Message'])
            else:
                text_messages = ' '.join(messages[messages['Sender'] == person_chooser]['Message'])
            stopwords = set(STOPWORDS)
            stopwords.update(['code', 'changed', 'This message', 'Tap', 'for', 'changed', 'Tap for' 'was', 'deleted', 'message', 'was', 'security','code', 'more', 'info'])
            wordcloud = WordCloud(width=800, height=500, stopwords=stopwords, background_color="white").generate(text_messages)
            fig11 = plt.figure(figsize=(10,10), dpi = 300)
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis("off")
            plt.title('{:%d/%m/%Y} - {:%d/%m/%Y}: Most used words by {}'.format(sd, ed, person_chooser), fontname='Comic Sans MS')
            st.pyplot(fig11, bbox_inches = 'tight')
    
#     st.subheader('Gaspard Nzasabimfura')
#     st.write('Data Analyst | Data Scientist | Data Engineer')
    st.info("""Info/Feedback: nzagaspard@gmail.com | +250722882193 (Whatsapp)""")

#@st.cache(suppress_st_warning=True)   
def loading_data():
    if stats == '':
        st.write(description)
    
    if use_file == 'Default':
        d = pd.read_csv('https://raw.githubusercontent.com/nzagaspard/Datasets3/master/Whatsapp%20Chats%20Samples.csv',encoding='utf-8')
        return d   
    else:
        st.write('Sometimes when no file uploaded the commands are run on the recent uploaded file', color = 'red')
        file = st.file_uploader('Drop or Browse the extracted chat file (.txt)', encoding= 'utf-8', type = 'txt')
        
        if file:
            return file.readlines()
        else:
            st.write('## Upload File!')
    
def clean_data(raw_messages):  
    #Combining Rows
    combined_rows = []
    condition1 = r'.*,\s.*\s-\s.*:{1}' #Pattern to match the line starting with date, time and author.
    condition2 = r'.*,\s.*\s-\s\w' #Pattern for matching the line with date, time and without authors.
    for line in raw_messages:
        if re.match(condition1, line):
            combined_rows.append(line)
        elif re.match(condition2, line):
            continue
        else:
            combined_rows[-1] = combined_rows[-1].replace('\n','') + ' ' + line
    
    #Extracting the Data    
    extracting_pattern = r"""(?P<Date>\d{1,2}/\d{1,2}/\d{2}),\s(?P<Time>\d{1,2}:\d{1,2} [AP]M)\s-\s(?P<Sender>[\w\s\d+@&#%]*):\s(?P<Message>.*)"""
    messages_series = pd.Series(combined_rows)
    messages_df = messages_series.str.extract(extracting_pattern)
    messages_df.dropna(inplace = True)
    
    #Converting or adding additional features
    messages_df['Date'] = messages_df['Date'].apply(lambda x: datetime.strptime(x,'%m/%d/%y'))
    messages_df['ddmm'] = messages_df['Date'].apply(lambda x: datetime.strftime(x,'%d/%m'))
    messages_df['Weekday'] = messages_df['Date'].apply(lambda x: datetime.strftime(x, '%A'))
    days = {"Monday" : 1, "Tuesday" : 2, "Wednesday" : 3, "Thursday" : 4, "Friday" : 5, "Saturday" : 6, "Sunday" : 7}
    messages_df['Day Number'] = messages_df['Weekday'].replace(days)
    messages_df['Time'] = messages_df['Time'].apply(lambda x: datetime.strptime(x, '%I:%M %p').strftime('%H:%M'))
    messages_df['Number of Words'] = messages_df['Message'].apply(lambda x: len(str(x).split()))
    messages_df['Number of Characters'] = messages_df['Message'].apply(lambda x: len(str(x)))
    
    #Finding links
    def count_links(message):
        link_finder = r"(.*)?://([\w\.-]+)/?(.*)"
        links_count = 0
        words = message.split()
        for word in words:
            if re.match(link_finder, word):
                links_count += 1
        return links_count

    messages_df['Number of Links'] = messages_df['Message'].apply(count_links)
    
    #Finding Emojis
    def find_emojis(message):
        emojis = []
        words = message.split()
        for word in words:
            for character in word:
                if character in emoji.UNICODE_EMOJI:
                    emojis.append(character)                
        return emojis
    
    messages_df['Emojis'] = messages_df['Message'].apply(find_emojis)
    messages_df['Number of Emojis'] = messages_df['Emojis'].apply(lambda x: len(x))
    all_emojis = list([a for b in messages_df['Emojis'] for a in b])
    emojis = dict(Counter(all_emojis))
    emojis_df = pd.DataFrame({'Emoji': list(emojis.keys()), 'Total': list(emojis.values())})      
    
    return messages_df, emojis_df

if __name__ == '__main__':
    main()

#     https://gilberttanner.com/blog/turn-your-data-science-script-into-websites-with-streamlit
# https://gilberttanner.com/blog/deploying-your-streamlit-dashboard-with-heroku
#http://dataset-explorer-beta.herokuapp.com/
