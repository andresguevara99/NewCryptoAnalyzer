import streamlit as st
from PIL import Image
import base64
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests
import pandas as pd
import json
import time

st.set_page_config(layout= "wide")
title_pic = Image.open(r'C:\Users\Andres\Desktop\Python_Playground\Crypto_App\cryptosite.png')
st.image(title_pic, width = 500)
st.title('New CMC-Listed Cryptos Tool')
st.markdown("""
This app retrieves live data from the newest CMC-listed cryptos and provides analysis on them

""")

##Dividing our page into 3 columns (col1 = sidebar; col2 & col3 = our data graphs)
col1 = st.sidebar
col2, col3 = st.beta_columns((2,1))

col1.header('Currency of Choice (for price)')

#curr_price_unit = col1.selectbox('Select Currency for Price', ('USD', 'BTC', 'ETH'))





@st.cache
def load_crypto_data():
    cmc = requests.get('https://coinmarketcap.com/new/')
    soup = BeautifulSoup(cmc.content, 'html.parser')

    data = soup.find('script', id='__NEXT_DATA__', type='application/json')
    coins = {}
    coin_data = json.loads(data.contents[0])
    token_listings = coin_data['props']['initialState']['cryptocurrency']['new']['data']
    for i in token_listings:
      coins[str(i['id'])] = i['slug']

    for k, v in coins.items():
        print(k,v)

    #print(token_listings)
    coin_name = []
    coin_symbol = []
    priceChange1h = []
    priceChange24h = []
    price = []
    volume24h = []
    #platforms = []

    for i in token_listings:
        coin_name.append(i['slug'])
        coin_symbol.append(i['symbol'])
        price.append(i['priceChange']['price'])
        priceChange1h.append(i['priceChange']['priceChange1h'])
        priceChange24h.append(i['priceChange']['priceChange24h'])
        volume24h.append(i['priceChange']['volume24h'])
        #platforms.append(i['platforms']['name'])


    df = pd.DataFrame(columns=['coin_name', 'coin_symbol', 'priceChange1h', 'priceChange24h',  'price', 'volume24h'])
    df['coin_name'] = coin_name
    df['coin_symbol'] = coin_symbol
    df['price'] = price
    df['priceChange1h'] = priceChange1h
    df['priceChange24h'] = priceChange24h
    df['volume24h'] = volume24h
    #df['platforms'] = platforms
    return df

df = load_crypto_data()

#print(df.head())
## Sidebar for different pct_change (1h // 24h)
pct_change_time = col1.selectbox('Percent Change Time Frame',
                                    ['24h','1h'])
pct_change_dict = {'24h':"priceChange24h", '1h': "priceChange1h"}
selected_pct_change_time = pct_change_dict[pct_change_time]


col2.subheader('Data Table of Newest Cryptocurrencies')
col2.dataframe(df)

new_df = pd.concat([df.coin_name, df.coin_symbol, df.priceChange1h, df.priceChange24h], axis= 1)
#print(new_df.head())
new_df = new_df.set_index('coin_symbol')
new_df['positive_priceChange1h'] = new_df['priceChange1h'] > 0
new_df['positive_priceChange24h'] = new_df['priceChange24h'] > 0
col2.dataframe(new_df)


col3.subheader('Bar Plot : % Change')


if pct_change_time == '24h':
    new_df = new_df.sort_values(by=['priceChange24h'])
    col3.write('24 HR Period')
    plt.figure(figsize=(5,10))
    plt.subplots_adjust(top = 1, bottom = 0)
    new_df['priceChange24h'].plot(kind='barh' , color = new_df.positive_priceChange24h.map({True: 'g', False: 'r'}))
    col3.pyplot(plt)
    
else:
    new_df = new_df.sort_values(by=['priceChange1h'])
    col3.write('1 HR Period')
    plt.figure(figsize=(5,10))
    plt.subplots_adjust(top = 1, bottom = 0)
    new_df['priceChange1h'].plot(kind='barh' , color = new_df.positive_priceChange1h.map({True: 'g', False: 'r'}))
    col3.pyplot(plt)
    