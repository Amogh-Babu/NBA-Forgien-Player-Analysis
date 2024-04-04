'''
This code is intended to scrape data from a variety of websites and then merge them to create plottable datasets. It uses BeautifulSoup and Selenium .
Not all of the data was webscraped
'''

import time
import pandas as pd
import geopandas as gpd

from selenium import webdriver
from bs4 import BeautifulSoup

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


def main():
    
    # Scraping Setup
    driver = setup()

    # Web Scraping
    player_scrape(driver)
    draft_scrape(driver)
    stats_scrape(driver)
    all_star_scrape(driver)
    mvps_scrape(driver)
    rating_scrape(driver)
    playoff_points_scrape(driver)

    # Data Preparation
    origins_geospatial()
    forgien_percent()
    rating_scatter()
    net_rating_line()
    champs_status_line()
    forgien_mvp_prop()
    popularity_overtime()
    franchise_growth()
    all_star_frequency()
    jersey_sales_overtime()
    playoff_point_distribtion()
    

    
def setup():
    '''
    Sets up the WebDriver with the following specifications
    '''
    options = Options()
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36")
    options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    options.add_argument("start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    webdriver_service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=webdriver_service, options = options)
    
    return driver


def player_scrape(driver):
    '''
    Creates the players.csv dataset
    '''
    def name_find(player):
        n = player.find('div', class_='RosterRow_playerName__G28lg').find_all('p')
        return n[0].text + ' ' + n[1].text

    def team_find(player):
        t = player.find('a', class_='Anchor_anchor__cSc3P RosterRow_team__AunTP')
        return t.text if t is not None else 'NONE'

    def coi_find(player):
        return player.find_all('td', class_='text')[5].text

    # Open players website
    url = 'https://www.nba.com/players'
    driver.get(url)
    driver.refresh()
    time.sleep(2)

    # Click switch to display historical data   
    history_btn = driver.find_elements(By.CLASS_NAME, "Toggle_slider__ln3dZ")
    history_btn[1].click()
    time.sleep(2)

    data = []


    for i in range(100):
        # Scrape Data
        doc = BeautifulSoup(driver.page_source, "html.parser")
        players = doc.find("tbody").find_all('tr')
        data.extend([{'Name': name_find(p), 'Team': team_find(p), 'CoI': coi_find(p)} for p in players])

        # Go to next page
        next_slide = driver.find_elements(By.CLASS_NAME, "Pagination_button__sqGoH")[1]
        next_slide.click()


    # Create dataframe
    data = pd.DataFrame(data)
    print(data)
    data.to_csv('raw_data/players.csv', index=False)


def draft_scrape(driver):
    '''
    Creates the draft.csv dataset
    '''
    # Open players website
    url = 'https://www.nba.com/stats/draft/history'
    driver.get(url)
    time.sleep(2)


    row_select = driver.find_elements(By.CLASS_NAME, 'DropDown_select__4pIg9')[3]
    dropdown = Select(row_select)
    dropdown.select_by_visible_text("All")



    players = driver.find_element(By.CLASS_NAME, 'Crom_body__UYOcU').find_elements(By.TAG_NAME, 'tr')
    players = [p.find_elements(By.TAG_NAME, 'td') for p in players]

    data = [{'Name': p[0].text, 'Team': p[1].text, 'Year': p[3].text, 'Overall Pick': p[6].text} for p in players]

    data = pd.DataFrame(data)
    data.to_csv('raw_data/draft.csv', index=False)

    print(data)



def stats_scrape(driver):
    '''
    Creates the stats.csv dataset
    '''
    # Open players website
    url = 'https://www.nba.com/stats/players/traditional'
    driver.get(url)
    time.sleep(2)

    years = [f'{i}-{((i+1)%100):02}' for i in range(1996, 2024)]
    #years = ['2022-23']


    data = []


    for year in years:


        yr_select = driver.find_elements(By.CLASS_NAME, 'DropDown_select__4pIg9')[0]
        yr_dropdown = Select(yr_select)
        yr_dropdown.select_by_visible_text(year)

        time.sleep(3)

        row_select = driver.find_elements(By.CLASS_NAME, 'DropDown_select__4pIg9')[25]
        dropdown = Select(row_select)
        dropdown.select_by_visible_text("All")

        time.sleep(3)

        players = driver.find_element(By.CLASS_NAME, 'Crom_body__UYOcU').find_elements(By.TAG_NAME, 'tr')
        players = [p.find_elements(By.TAG_NAME, 'td') for p in players]
        data.extend([{'Year': year, 'Rank': p[0].text, 'Name': p[1].text, 'Team': p[2].text, 'Win Loss Ratio': (int(p[5].text)/int(p[6].text)) if int(p[6].text) != 0 else 1.0, 'Minutes Played PG': p[7].text,
                'Points PG': p[8].text, 'FG Percentage': p[11].text, '3P Percentage': p[14].text, 'FT Percentage': p[17].text, 'Rebounds PG': p[20].text,
                'Assists PG': p[21].text, 'Steals PG': p[22].text, 'Blocks PG': p[23].text, '+/-': p[29].text} for p in players])

    data = pd.DataFrame(data)
    data.to_csv('raw_data/stats.csv', index=False)

    print(data)


def playoff_points_scrape(driver):
    '''
    Creates the playoffs.csv dataset
    '''
    # Open players website
    url = 'https://www.nba.com/stats/players/traditional'
    driver.get(url)
    time.sleep(2)

    years = [f'{i}-{((i+1)%100):02}' for i in range(1996, 2023)]
    #years = ['2022-23']


    data = []

    g_select = driver.find_elements(By.CLASS_NAME, 'DropDown_select__4pIg9')[1]
    g_dropdown = Select(g_select)
    g_dropdown.select_by_visible_text('Playoffs')
    
    time.sleep(2)
    
    t_select = driver.find_elements(By.CLASS_NAME, 'DropDown_select__4pIg9')[2]
    t_dropdown = Select(t_select)
    t_dropdown.select_by_visible_text('Totals')
    
    time.sleep(2)

    for year in years:


        yr_select = driver.find_elements(By.CLASS_NAME, 'DropDown_select__4pIg9')[0]
        yr_dropdown = Select(yr_select)
        yr_dropdown.select_by_visible_text(year)

        time.sleep(3)

        row_select = driver.find_elements(By.CLASS_NAME, 'DropDown_select__4pIg9')[25]
        dropdown = Select(row_select)
        dropdown.select_by_visible_text("All")

        time.sleep(3)

        players = driver.find_element(By.CLASS_NAME, 'Crom_body__UYOcU').find_elements(By.TAG_NAME, 'tr')
        players = [p.find_elements(By.TAG_NAME, 'td') for p in players]
        data.extend([{'Year': year, 'Name': p[1].text, 'Team': p[2].text, 'Points': p[8].text} for p in players])

    data = pd.DataFrame(data)
    data.to_csv('raw_data/playoffs.csv', index=False)

    print(data)


def rating_scrape(driver):
    '''
    Creates the rating.csv dataset
    '''
    # Open players website
    url = 'https://www.nba.com/stats/players/advanced'
    driver.get(url)
    time.sleep(2)

    years = [f'{i}-{((i+1)%100):02}' for i in range(1996, 2024)]
    #years = ['2022-23']


    data = []


    for year in years:


        yr_select = driver.find_elements(By.CLASS_NAME, 'DropDown_select__4pIg9')[0]
        yr_dropdown = Select(yr_select)
        yr_dropdown.select_by_visible_text(year)

        time.sleep(3)

        row_select = driver.find_elements(By.CLASS_NAME, 'DropDown_select__4pIg9')[25]
        dropdown = Select(row_select)
        dropdown.select_by_visible_text("All")

        time.sleep(3)

        players = driver.find_element(By.CLASS_NAME, 'Crom_body__UYOcU').find_elements(By.TAG_NAME, 'tr')
        players = [p.find_elements(By.TAG_NAME, 'td') for p in players]
        data.extend([{'Year': year, 'Name': p[1].text, 'Team': p[2].text, 'Offensive Rating': p[8].text, 'Defensive Rating': p[9].text, 'Net Rating': p[10].text} for p in players])

    data = pd.DataFrame(data)
    data.to_csv('raw_data/rating.csv', index=False)

    print(data)


def all_star_scrape(driver):
    '''
    Creates the all_star.csv dataset
    '''
    url = 'https://www.basketball-reference.com/awards/all_star_by_player.html'
    driver.get(url)
    time.sleep(2)

    players = driver.find_elements(By.TAG_NAME, 'tbody')[30].find_elements(By.TAG_NAME, 'tr')
    players = [p.find_elements(By.TAG_NAME, 'td') for p in players if p.get_attribute("class") != 'thead']

    data = [{'Name': p[1].text, 'Selections': p[2].text} for p in players]

    data = pd.DataFrame(data)
    data.to_csv('raw_data/all_star.csv', index=False)

    print(data)


def mvps_scrape(driver):
    '''
    Creates the mvps.csv dataset
    '''
    url = 'https://www.basketball-reference.com/awards/mvp.html'
    driver.get(url)
    time.sleep(2)

    players = driver.find_elements(By.TAG_NAME, 'tbody')[30].find_elements(By.TAG_NAME, 'tr')
    players = [p.find_elements(By.TAG_NAME, 'td') for p in players]

    # .extend(p.find_elements(By.TAG_NAME, 'th'))
    data = [{'Player': p[1].text, 'Team': p[4].text} for p in players if len(p) != 0]

    data = pd.DataFrame(data)
    data.to_csv('raw_data/mvps.csv', index=True)

    print(data)


def origins_geospatial():
    '''
    Creates the orgins.csv dataset
    (Shape files currently not working)
    '''
    
    players = pd.read_csv('raw_data/players.csv')
    season = pd.read_csv('raw_data/stats.csv')
    #shape = gpd.read_file('raw_data/earth.shp')

    season = season[['Year', 'Name']]
    season = season[(season['Year'] == '2000-01') | (season['Year'] == '2023-24')]

    origins = season.merge(players, on='Name', how='left')
    origins = origins[['Year', 'CoI']]
    
    #origins = origins.merge(shape, left_on='CoI', right_on='Country', how='right')

    origins.to_csv('data_organized/origins_geospatial.csv', index=False)
    

def forgien_percent():
    '''
    Creates the origins_of_players.csv dataset
    '''
    players = pd.read_csv('raw_data/players.csv')
    season = pd.read_csv('raw_data/stats.csv')
    draft = pd.read_csv('raw_data/draft.csv')
    
    season = season[['Name', 'Year']]
    
    origins = season.merge(players, on='Name', how='left')
    origins['CoI'] = origins['CoI'].apply(lambda CoI: 1 if CoI != 'USA' else 0)
    origins = origins.groupby('Year')['CoI'].apply(lambda s: s.sum()/s.count())
    
    draft_origins = draft.merge(players, on='Name', how='left')
    draft_origins['CoI'] =  draft_origins['CoI'].apply(lambda CoI: 1 if CoI != 'USA' else 0)
    draft_origins =  draft_origins.groupby('Year')['CoI'].apply(lambda s: s.sum()/s.count())
    draft_origins = draft_origins.loc[2000:]
    
    draft_origins.index = [f'{i}-{((i+1)%100):02}' for i in range(2000, 2024)]
    
    origins = pd.DataFrame({'Proportion of Players':origins, 'Proportion of Drafted Players':draft_origins})
    origins.to_csv('data_organized/origins_of_players.csv', index=True)

    
def rating_scatter():
    '''
    Creates the player_rating_status.csv dataset
    '''
    ratings = pd.read_csv('raw_data/rating.csv')
    players = pd.read_csv('raw_data/players.csv')
    
    ratings = ratings[(ratings['Year'] == '2000-01') | (ratings['Year'] == '2023-24')]
    
    ratings_status = ratings.merge(players, on='Name', how='left')
    ratings_status['CoI'] = ratings_status['CoI'].apply(lambda CoI: True if CoI != 'USA' else False)
    
    ratings_status = ratings_status[['Name', 'Year', 'CoI', 'Offensive Rating', 'Defensive Rating']]
    ratings_status = ratings_status.rename(columns={'CoI':'Forgien?'})
    
    ratings_status.to_csv('data_organized/player_ratings_status.csv', index=False)


def net_rating_line():
    '''
    Creates the net_rating_overtime.csv dataset
    '''
    ratings = pd.read_csv('raw_data/rating.csv')
    players = pd.read_csv('raw_data/players.csv')
    
    ratings_over_time = ratings.merge(players, on='Name', how='left')
    ratings_over_time = ratings_over_time[['Year', 'Net Rating', 'CoI']]
    
    forgien_net_time = ratings_over_time[ratings_over_time['CoI'] != 'USA']
    domestic_net_time = ratings_over_time[ratings_over_time['CoI'] == 'USA']

    
    forgien_net_time = forgien_net_time.groupby('Year')['Net Rating'].mean()
    domestic_net_time = domestic_net_time.groupby('Year')['Net Rating'].mean()
    
    net_over_time = pd.DataFrame({'Domestic':domestic_net_time, 'Forgien':forgien_net_time})
    
    net_over_time.to_csv('data_organized/net_rating_overtime.csv', index=True)
    

def champs_status_line():
    '''
    Creates the finals_forgein_percentage.csv dataset
    '''
    
    def normalize_champs(s):
        if (s == 'Denver Nuggets'):
            return 'DEN'
        
        elif (s == 'Golden State Warriors'):
            return 'GSW'
        
        elif (s == 'Milwaukee Bucks'):
            return 'MIL'
        
        elif (s == 'Los Angeles Lakers'):
            return 'LAL'
        
        elif (s == 'Toronto Raptors'):
            return 'TOR'
        
        elif (s == 'Cleveland Cavaliers'):
            return 'CLE'
        
        elif (s == 'San Antonio Spurs'):
            return 'SAS'
        
        elif (s == 'Miami Heat'):
            return 'MIA'
        
        elif (s == 'Dallas Mavericks'):
            return 'DAL'
        
        elif (s == 'Boston Celtics'):
            return 'BOS'
        
        elif (s == 'Detroit Pistons'):
            return 'DET'
        
        elif (s == 'Phoenix Suns'):
            return 'PHX'
        
        elif (s == 'Oklahoma City Thunder'):
            return 'OKC'
        
        elif (s == 'Orlando Magic'):
            return 'ORL'
        
        elif (s == 'Brooklyn Nets'):
            return 'BKN'
        
        elif (s == 'Philadelphia 76ers'):
            return 'PHI'
        
        elif (s == 'Indiana Pacers'):
            return 'IND'
        
        elif (s == 'New York Knicks'):
            return 'NYK'
        
        elif (s == 'Los Angeles Clippers'):
            return 'LAC'
        
        elif (s == 'Chicago Bulls'):
            return 'CHI'
        
        elif (s == 'Houston Rockets'):
            return 'HOU'
        
        elif (s == 'Washington Wizards'):
            return 'WAS'
        
        elif (s == 'Sacramento Kings'):
            return 'SAC'
        
        elif (s == 'Atlanta Hawks'):
            return 'ATL'
        
        elif (s == 'Utah Jazz'):
            return 'UTA'
        
        elif (s == 'Portland Trail Blazers'):
            return 'POR'
        
        elif (s == 'Charlotte Hornets'):
            return 'CHA'
        
        elif (s == 'New Orleans Pelicans'):
            return 'NOP'
        
        elif (s == 'Minnesota Timberwolves'):
            return 'MIN'

        elif (s == 'Memphis Grizzlies'):
            return 'MEM'
        
        else:
            return None
    
    def normalize_year(s):
        return '20'+s[-2:]
    
    champs = pd.read_csv('raw_data/championships.csv')
    seasons = pd.read_csv('raw_data/stats.csv')
    players = pd.read_csv('raw_data/players.csv')
    
    champs = champs[champs['Year'] > 2000]
    
    seasons['Year'] = seasons['Year'].apply(normalize_year)
    
    champs['Champion'] = champs['Champion'].apply(normalize_champs)
    champs['Runner-Up'] = champs['Runner-Up'].apply(normalize_champs)
    champs['Year'] = champs['Year'].apply(str)
    
    champs['Id_Champion'] = champs['Champion'] + champs['Year']
    champs['Id_Runner_Up'] = champs['Runner-Up'] + champs['Year']
    seasons['Id'] = seasons['Team'] + seasons['Year']

    champions_roster = champs.merge(seasons, left_on='Id_Champion', right_on='Id', how='left')
    runner_up_roster = champs.merge(seasons, left_on='Id_Runner_Up', right_on='Id', how='left')

    finals_rosters = pd.concat([champions_roster, runner_up_roster], ignore_index=True)    
    finals_rosters = finals_rosters.merge(players, on='Name', how='left')
    finals_rosters = finals_rosters[['Year_x', 'Champion', 'Runner-Up', 'Name', 'CoI']]
    
    finals_rosters = finals_rosters.rename(columns={'Year_x':'Year'})
    
    finals_rosters['CoI'] = finals_rosters['CoI'].apply(lambda CoI: 1 if CoI != 'USA' else 0)
    finals_rosters = finals_rosters.groupby('Year')['CoI'].apply(lambda s: s.sum()/s.count())
    
    finals_rosters.to_csv('data_organized/finals_forgein_percentage.csv', index=True)


def forgien_mvp_prop():
    '''
    Cretes the popularity_overtime.csv dataset
    '''
    mvps = pd.read_csv('raw_data/mvps.csv')
    players = pd.read_csv('raw_data/players.csv')
    
    mvps_proportion = mvps.merge(players, left_on='Player', right_on='Name')
    mvps_proportion = mvps_proportion[['Name', 'CoI']]
    
    mvps_proportion.to_csv('data_organized/mvps_proportion.csv', index=True)
    

def popularity_overtime():
    value = pd.read_csv('raw_data/avg_franchise_value.csv')
    views = pd.read_csv('raw_data/finals_viewership.csv')
    
    popularity = value.merge(views, on='Year', how='left')
    
    popularity.to_csv('data_organized/popularity_overtime.csv', index=False)
    
    
def franchise_growth():
    '''
    Creates the franchise_growth.csv dataset
    '''
    
    def normalize_names(s):
        if (s == 'Denver Nuggets'):
            return 'DEN'
        
        elif (s == 'Golden State Warriors'):
            return 'GSW'
        
        elif (s == 'Milwaukee Bucks'):
            return 'MIL'
        
        elif (s == 'Los Angeles Lakers'):
            return 'LAL'
        
        elif (s == 'Toronto Raptors'):
            return 'TOR'
        
        elif (s == 'Cleveland Cavaliers'):
            return 'CLE'
        
        elif (s == 'San Antonio Spurs'):
            return 'SAS'
        
        elif (s == 'Miami Heat'):
            return 'MIA'
        
        elif (s == 'Dallas Mavericks'):
            return 'DAL'
        
        elif (s == 'Boston Celtics'):
            return 'BOS'
        
        elif (s == 'Detroit Pistons'):
            return 'DET'
        
        elif (s == 'Phoenix Suns'):
            return 'PHX'
        
        elif (s == 'Oklahoma City Thunder'):
            return 'OKC'
        
        elif (s == 'Orlando Magic'):
            return 'ORL'
        
        elif (s == 'Brooklyn Nets'):
            return 'BKN'
        
        elif (s == 'Philadelphia 76ers'):
            return 'PHI'
        
        elif (s == 'Indiana Pacers'):
            return 'IND'
        
        elif (s == 'New York Knicks'):
            return 'NYK'
        
        elif (s == 'Los Angeles Clippers'):
            return 'LAC'
        
        elif (s == 'Chicago Bulls'):
            return 'CHI'
        
        elif (s == 'Houston Rockets'):
            return 'HOU'
        
        elif (s == 'Washington Wizards'):
            return 'WAS'
        
        elif (s == 'Sacramento Kings'):
            return 'SAC'
        
        elif (s == 'Atlanta Hawks'):
            return 'ATL'
        
        elif (s == 'Utah Jazz'):
            return 'UTA'
        
        elif (s == 'Portland Trail Blazers'):
            return 'POR'
        
        elif (s == 'Charlotte Hornets'):
            return 'CHA'
        
        elif (s == 'New Orleans Pelicans'):
            return 'NOP'
        
        elif (s == 'Minnesota Timberwolves'):
            return 'MIN'

        elif (s == 'Memphis Grizzlies'):
            return 'MEM'
        
        else:
            return None
    
    value = pd.read_csv('raw_data/franchise_value.csv')
    players = pd.read_csv('raw_data/players.csv')
    season = pd.read_csv('raw_data/stats.csv')
    
    value['Team'] = value['Team'].apply(normalize_names)
    value['Growth'] = value['2022–23'] - value['2012–13']

    season['Year'] = season['Year'].apply(lambda s: int(s[:4]))
    season = season[(season['Year'] <= 2022) & (season['Year'] >= 2012)]
    season['Year'] = season['Year'].apply(str)
    
    origins = season.merge(players, on='Name', how='left')
    origins = origins[origins['Team_x'] != 'NOH']
    origins = origins[origins['CoI'] != 'USA']
    origins = origins.groupby('Team_x')['CoI'].count()
    
    growth_per_franchise = value.merge(origins, left_on='Team', right_on='Team_x', how='right')
    growth_per_franchise = growth_per_franchise[['Team', 'Growth', 'CoI']]
    growth_per_franchise = growth_per_franchise.rename(columns={'CoI':'# of Forgien Players'})
    
    growth_per_franchise.to_csv('data_organized/franchise_growth.csv')


def all_star_frequency():
    '''
    Creates the all_star_origins.csv dataset
    '''
    all_star = pd.read_csv('raw_data/all_star.csv')
    players = pd.read_csv('raw_data/players.csv')
    
    all_star_origin = all_star.merge(players, on='Name', how='left')
    all_star_origin = all_star_origin.groupby('CoI')['Selections'].sum()
    
    all_star_origin.to_csv('data_organized/all_star_origins.csv')
    

def jersey_sales_overtime():
    '''
    Creates the jersey_sales_overtime.csv dataset
    '''
    jersey = pd.read_csv('raw_data/jersey_leaders.csv')
    players = pd.read_csv('raw_data/players.csv')
    
    jersey_sales_origin = jersey.merge(players, left_on='Player', right_on='Name', how='left')
    jersey_sales_origin = jersey_sales_origin[jersey_sales_origin['CoI'] != 'USA']
    
    jersey_sales_origin = jersey_sales_origin.groupby('Year')['Player'].count()
    
    jersey_sales_origin.to_csv('data_organized/jersey_sales_overtime.csv')

def playoff_point_distribtion():
    '''
    Creates the playoff_points_distribution.csv dataset
    '''
    playoffs = pd.read_csv('raw_data/playoffs.csv')
    players = pd.read_csv('raw_data/players.csv')

    playoff_points_origin = playoffs.merge(players, on='Name', how='left')
    playoff_points_origin = playoff_points_origin[['Year', 'Name', 'Team_x', 'Points', 'CoI']]
    playoff_points_origin = playoff_points_origin.rename(columns={'Team_x':'Team'})
    
    playoff_points_origin.to_csv('data_organized/playoff_points_distribution.csv', index=False)

    


if __name__ == '__main__':
    main()
