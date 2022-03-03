from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Set the option to display all columns we need
pd.set_option('display.max_columns', 30)

# This dictionary stores the unique player tags of players I commonly look up.
# Until I have a more robust way of verifying the number at the end of the unique player tag, this dictionary will have to do.
player_handle_dict = {
    'Steven Adams' : 'a/adamsst01',
    'Giannis' : 'a/antetgi01',
    'Lonzo Ball' : 'b/balllo01',
    'Devin Booker' : 'b/bookede01',
    'Jaylen Brown' : 'b/brownja02',
    'Steph Curry' : 'c/curryst01',
    'Anthony Davis' : 'd/davisan02',
    'DeMar DeRozan' : 'd/derozde01',
    'Luka Doncic' : 'd/doncilu01',
    'Kevin Durant' : 'd/duranke01',
    'Joel Embiid' : 'e/embiijo01',
    'Trent Forrest' : 'f/forretr01',
    'Darius Garland' : 'g/garlada01',
    'Rudy Gobert' : 'g/goberru01',
    'Aaron Gordon' : 'g/gordoaa01',
    'Jrue Holiday' : 'h/holidjr01',
    'LeBron James' : 'j/jamesle01',
    'Nikola Jokic' : 'j/jokicni01',
    'CJ McCollum' : 'm/mccolcj01',
    'Patty Mills' : 'm/millspa02',
    'Khris Middleton' : 'm/middlkh01',
    'Donovan Mitchell' : 'm/mitchdo01',
    'Ja Morant' : 'm/moranja01',
    'Dejounte Murray' : 'm/murrade01',
    'Chris Paul' : 'p/paulch01',
    'Julius Randle' : 'r/randlju01',
    'Mitchell Robinson' : 'r/robinmi01',
    'Domantas Sabonis' : 's/sabondo01',
    'Jayson Tatum' : 't/tatumja01',
    'Trae Young' : 'y/youngtr01',
    'Ivaca Zubac' : 'z/zubaciv01'
    
}    

# Converts the words of stats we need into the column names
stats_dict = {
    'Rebounds' : 'TRB',
    'Points' : 'PTS',
    'Assists' : 'AST',
    'Steals' : 'STL',
    'Blocks' : 'BLK',
    '3-PT Made' : '3P',
    'Pts+Reb+Ast' : None,
    'Free Throws Made' : 'FT'
}


# Simple concatenation function to construct a player's game log URL given the unique tag from player_handle_dict
def make_player_url(name, season):
    return 'https://www.basketball-reference.com/players/' + player_handle_dict.get(name) + '/gamelog/' + str(season)


# Given the name of a player, I want to collect the game log for that player for the season specified. 2022 is the current season.
# If the 'clean' parameter is set to True, we automatically filter out games they didn't play. This avoids errors with data treatments.
def get_game_log(name, clean, season):
    
    # Check to make sure this player is available
    if name in player_handle_dict.keys():
        # Get player's url
        url = make_player_url(name, season=season)

        # collect HTML data
        html = urlopen(url)

        # create beautiful soup object from HTML
        soup = BeautifulSoup(html, features="lxml")
        # use getText()to extract the headers into a list
        potential_indexes = soup.findAll('tr')
        for i in potential_indexes:
            if 'Rk' in [th.getText() for th in i.findAll('th')]:
                headers = [th.getText() for th in i.findAll('th')]
        headers = headers[1:]
        rows = soup.findAll('tr')[32:]
        rows_data = [[td.getText() for td in rows[i].findAll('td')]
                        for i in range(len(rows))]

        game_log = pd.DataFrame(rows_data, columns = headers)

        # Remove games where the player was not available
        game_log = game_log[game_log['GS'] != 'None']

        if clean:
            # Remove games the player did not play
            game_log = game_log[game_log['GS'].isin(['0', '1'])]
            # Convert the string data to numeric data
            game_log[['FG','FGA','FG%','3P','3PA','3P%','FT','FTA','FT%','ORB','DRB','TRB','AST','STL','BLK','TOV','PF','PTS','GmSc','+/-']] = game_log[['FG','FGA','FG%','3P','3PA','3P%','FT','FTA','FT%','ORB','DRB','TRB','AST','STL','BLK','TOV','PF','PTS','GmSc','+/-']].apply(pd.to_numeric)

            # Convert minutes from string to float
            game_log.insert(game_log.columns.get_loc('MP'), 'Min', [int(mp[:mp.find(':')]) + int(mp[-2:])/60 for mp in game_log['MP']])
            game_log.drop(columns=['MP'], inplace=True)
            
    else:
        print(name + " is not yet available for analysis.")
        game_log = pd.DataFrame(columns=['G', 'Date', 'Age', 'Tm', ' ', 'Opp', ' ', 'GS', 'Min', 'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'GmSc', '+/-'])
        

    return game_log



class Player:
    
    def __init__(self, name, clean=True, season=2022):
        self.player_name = name
        self.game_log = get_game_log(name, clean=clean, season=season)
        
        # For use only if the game log gets reset
        self.default_clean = clean
        self.season = season
            
    # Resets the game log to its original state
    def reset_filters(self):
        self.game_log = get_game_log(name=self.player_name, clean=self.default_clean, season=self.season)


    # Select only games played against a specified list of opponents
    def filter_by_opponent(self, teams):
        self.game_log = self.game_log[self.game_log['Opp'].isin(teams)]
    # Select only games played for a specified team
    def filter_by_team(self, team):
        self.game_log = self.game_log[self.game_log['Tm'] == team]
    
    # Select home games
    def home_games(self):
        self.game_log = self.game_log[self.game_log.iloc[:,4] == '']
    # Select away games
    def away_games(self):
        self.game_log = self.game_log[self.game_log.iloc[:,4] == '@']
        
    # Select the last five games
    def last_5(self):
        self.game_log = self.game_log.iloc[-5:, :]
    # Select the last ten games
    def last_10(self):
        self.game_log = self.game_log.iloc[-10:, :]
    # Select the last n games
    def last_n(self, n):
        self.game_log = self.game_log.iloc[-n:, :]

    # Look at the selected game log
    def display_log(self):
        display(self.game_log)

        
# This houses player propositions to evaluate.
class PropositionLog:
    
    def __init__(self, player_list=None, stat_list=None, line_list=None):
        self.reset()
        if player_list != None:
            self.make_prop_log(player_list=player_list, stat_list=stat_list, line_list=line_list)
        
    def reset(self):
        self.prop_df = pd.DataFrame(columns=['Player Name', 'Statistic', 'Line'])
        self.player_object_list = []
        
    def make_prop_log(self, player_list, stat_list, line_list):
        # Clear any previous entries
        self.reset()
        # Checks to see if there are equal numbers of players, stats, and lines. The three lists should have consistent indexing
        # For example, the entries at index k should all be about the same proposition.        
        if len(player_list) == len(stat_list) and len(player_list) == len(line_list):
            prop_dict = {
                'Player Name' : [player.player_name for player in player_list],
                'Statistic' : stat_list,
                'Line' : line_list
            }
            self.prop_df = pd.DataFrame(prop_dict)
            self.player_object_list = player_list
        else:
            print('Mismatched lengths in the arguments provided. Unable to create a PropositionLog.')
    
    # Add a proposition to the existing log
    def add_prop(self, player, stat, line):
        if stat in stats_dict.keys():
            d = {
                'Player Name' : [player.player_name],
                'Statistic' : [stat],
                'Line' : [line]
            }
            new_prop = pd.DataFrame(d)
            self.prop_df = pd.concat([self.prop_df, new_prop], ignore_index=True)
            self.player_object_list.append(player)
        else:
            print('The statistic specified is not available. Call stats_dict.keys() for a list of available statistics.')
            
    def remove_prop(self, index):
        if index in self.prop_df.index:
            self.prop_df.drop(index=index, inplace=True)
            self.prop_df.reset_index(inplace=True)
            self.player_object_list.pop(index)

    def display_props(self):
        display(self.prop_df)
        
    def histogram(self, prop, bins=None):
        game_log = self.player_object_list[prop].game_log
        statistic = self.prop_df.loc[prop][1]
        line = self.prop_df.loc[prop][2]
        if statistic == 'Pts + Reb + Ast':
            data = game_log['PTS'] + game_log['TRB'] + game_log['AST']
        else:
            # Get the column name for the statistic in the proposition
            stat = stats_dict.get(statistic)
            data = game_log[stat]
        if bins==None:
            bins=data.nunique()
        plt.hist(data, bins=bins)
        plt.axvline(x=np.mean(data), c='lightgreen')
        plt.axvline(x=line, c='r')
        plt.xlabel(statistic)
        plt.ylabel('Freq')
        plt.title(self.player_object_list[prop].player_name)
        plt.legend(['Mean', 'Prop Line'])
        
    def evaluate(self):
        over_under = []
        percentage = []
        
        for prop in range(self.prop_df.shape[0]):
            # Pull off relevant information
            game_log = self.player_object_list[prop].game_log
            statistic = self.prop_df.iloc[prop,1]
            line = self.prop_df.iloc[prop,2]
            if statistic == 'Pts+Reb+Ast':
                p = np.mean(game_log['PTS'] + game_log['TRB'] + game_log['AST'] > line)
            else:
                # Get the column name for the statistic in the proposition
                stat = stats_dict.get(statistic)
                p = np.mean(game_log[stat] > line)
            # Calculate the compliment of the over
            c = 1 - p
            if p >= c:
                # The over is more (or as) likely
                over_under.append('Over')
                percentage.append(p)
            else:
                over_under.append('Under')
                percentage.append(c)
                
        # Add the new information to the dataframe
        self.prop_df['Over/Under'] = over_under
        self.prop_df['Percentage'] = percentage
        
        

















