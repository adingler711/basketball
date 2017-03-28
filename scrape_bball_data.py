from urllib import urlopen
import pandas as pd
from bs4 import BeautifulSoup


def assign_homeaway(data_df):
    if data_df['HomeAway'] == '':
        return 'Home'
    else:
        return 'Away'

def compile_player_stats(player):

    url_advanced = 'http://www.basketball-reference.com/players/' + player + '/gamelog-advanced/2017/'
    url_basic = 'http://www.basketball-reference.com/players/' + player + '/gamelog/2017/'

    html_advanced = urlopen(url_advanced)
    soup_advanced = BeautifulSoup(html_advanced, 'lxml')
    html_basic = urlopen(url_basic)
    soup_basic = BeautifulSoup(html_basic, 'lxml')

    table_advanced = soup_advanced.find_all('tr')

    row_start = 0
    row_start_cols = 0

    while row_start_cols < 23:

        temp = [th.text for th in table_advanced[row_start]]
        row_start_cols = len(temp)
        row_start = row_start + 1

    headers_advanced = [th.text for th in table_advanced[row_start - 1]]

    data = []

    for row in range(1, len(table_advanced)):

        temp_data = [th.text for th in table_advanced[row]]
        data.append(temp_data)

    player_advanced_df = pd.DataFrame(data, columns=headers_advanced)
    player_advanced_df = player_advanced_df[player_advanced_df['Rk'] != 'Rk']
    cols_advance = list(player_advanced_df.columns)
    cols_advance = cols_advance[0:5] + ['HomeAway', 'Opp', 'Streak'] + cols_advance[8:]
    player_advanced_df.columns = cols_advance

    table_basic = soup_basic.find_all('tr')

    row_start = 0
    row_start_cols = 0

    while row_start_cols < 30:
        temp = [th.text for th in table_basic[row_start]]
        row_start_cols = len(temp)
        row_start = row_start + 1

    headers_basic = [th.text for th in table_basic[row_start - 1]]

    data_basic = []

    for row in range((row_start - 1), len(table_basic)):
        temp_basic_data = [th.text for th in table_basic[row]]
        data_basic.append(temp_basic_data)

    player_basic_df = pd.DataFrame(data_basic, columns=headers_basic)
    player_basic_df = player_basic_df[player_basic_df['Rk'] != 'Rk']
    cols_basic = list(player_basic_df.columns)
    cols_basic = cols_basic[0:5] + ['HomeAway', 'Opp', 'Streak'] + cols_basic[8:]
    player_basic_df.columns = cols_basic
    player_basic_df = player_basic_df.drop(['GmSc'], axis=1)

    player_advanced_df['HomeAway'] = (player_advanced_df.apply(assign_homeaway, axis=1)).values
    player_basic_df['HomeAway'] = (player_basic_df.apply(assign_homeaway, axis=1)).values

    player_total = pd.merge(player_basic_df, player_advanced_df,
                            on=['Rk', 'G', 'Date', 'Age', 'Tm', 'HomeAway', 'Opp', 'Streak', 'GS', 'MP'],
                            how='left')

    player_total = player_total.drop(['Rk'], axis=1)

    return player_total


def aggregate_player_keys(players):
    player_list = []

    for player in list(players.index):
        player_name = players.loc[player]['Name']
        temp_name = player_name.split(" ")
        player_stringKey = str.lower(temp_name[0][0]) + '/' + str.lower(temp_name[1][:5]) + str.lower(
            temp_name[0][:2]) + '01'
        player_list.append([player_stringKey, player_name])

    return player_list


def aggregate_player_data(player_keypair_list):

    player_df = pd.DataFrame()

    for pkey, name in player_keypair_list:
        print pkey
        player_data = compile_player_stats(pkey)
        player_data['player'] = name
        player_df = pd.concat((player_df, player_data))

    # need to do nene seperate since he does not have a first name on the team roster
    player = 'h/hilarne01'
    player_total = compile_player_stats(player)
    player_total['player'] = player
    player_df = pd.concat((player_df, player_total), axis=0)

    return player_df