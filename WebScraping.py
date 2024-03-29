
from bs4 import BeautifulSoup
import requests
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select




def main():
    options = Options()
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36")
    options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    options.add_argument("start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    
    webdriver_service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=webdriver_service, options = options)
    
    #player_scrape(driver)
    #draft_scrape(driver)
    #stats_scrape(driver)
    #all_star_scrape(driver)
    mvps_scrape(driver)
    
    
def player_scrape(driver):
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
    data.to_csv('players.csv', index=False)


def draft_scrape(driver):
    
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
    data.to_csv('draft.csv', index=False)

    print(data)
    
    
def stats_scrape(driver):
    
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
    data.to_csv('stats.csv', index=False)

    print(data)
    

def all_star_scrape(driver):
    url = 'https://www.basketball-reference.com/awards/all_star_by_player.html'
    driver.get(url)
    time.sleep(2)
    
    players = driver.find_elements(By.TAG_NAME, 'tbody')[30].find_elements(By.TAG_NAME, 'tr')
    players = [p.find_elements(By.TAG_NAME, 'td') for p in players if p.get_attribute("class") != 'thead']
    
    data = [{'Name': p[1].text, 'Selections': p[2].text} for p in players]
        
    data = pd.DataFrame(data)
    data.to_csv('all_star.csv', index=False)

    print(data)


def mvps_scrape(driver):
    url = 'https://www.basketball-reference.com/awards/mvp.html'
    driver.get(url)
    time.sleep(2)
    
    players = driver.find_elements(By.TAG_NAME, 'tbody')[30].find_elements(By.TAG_NAME, 'tr')
    players = [p.find_elements(By.TAG_NAME, 'td') for p in players]
    
    # .extend(p.find_elements(By.TAG_NAME, 'th'))
    data = [{'Player': p[1].text, 'Team': p[4].text} for p in players if len(p) != 0]
        
    data = pd.DataFrame(data)
    data.to_csv('mvps.csv', index=True)

    print(data)


        

if __name__ == '__main__':
    main()
