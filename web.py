'''
#  RTDL: Web Functions
#  Project Page: https://github.com/EmbersAtDawn/rtdl
#  
#  Current ToDo: 
# 
'''
# Case: wrong file run
if __name__ == '__main__':
    print('Please run rtdl.py instead.\n')
    input('Press ENTER to exit . . .')
    quit()
#------------------------------------------------------------IMPORT STATEMENTS------------------------------------------------------------#
from system import display_wait_message
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#------------------------------------------------------------WEB INTERACTION--------------------------------------------------------------#
def fetch_series_info(driver, series_url):
    '''
    Return: Series Info as Dictionary with Keys: 'title', 'num_seasons', 'summary', 'series_url'
    '''

    series_title_class = 'featured-title'
    series_num_seasons_class = 'season-info'
    series_summary_class = 'featured-summary'
    
    # Navigate to page and set up wait option
    display_wait_message()
    driver.get(series_url)
    wait = WebDriverWait(driver, 10)

    # Get the data
    series_title = (wait.until(EC.presence_of_element_located((By.CLASS_NAME, series_title_class)))).text.strip()
    num_seasons = (wait.until(EC.presence_of_element_located((By.CLASS_NAME, series_num_seasons_class)))).text.strip()
    series_summary = (wait.until(EC.presence_of_element_located((By.CLASS_NAME, series_summary_class)))).text.strip()

    # Change number of seasons from a string to an int (format input ex: "7 seasons")
    num_seasons = int(num_seasons.split()[0])

    # Create information dictionary
    info = {'title' : series_title, 'num_seasons' : num_seasons, 'summary' : series_summary, 'series_url' : series_url}
    return info

def fetch_season_episodes(driver, series_url, season_num):
    '''
    Input:  Series URL, Season Number (as a string)
    
    Return: Season Episodes as a Dictionary with Keys: 'title', 'episode_url'
    '''
    
    # series_url format: https://roosterteeth.com/rwby
    # season_num addon format: ?season=1

    season = {}
    season_url = series_url + '?season=' + season_num
    episode_container_path = '//*[@id="root"]/div/div/div[3]/main/div/section[1]/div[2]/section[1]/div[2]'
    episode_title_class = 'episode-title'

    # Start the web driver and wait option
    display_wait_message()
    driver.get(season_url)
    wait = WebDriverWait(driver, 10)

    all_episodes = (wait.until(EC.presence_of_element_located((By.XPATH, episode_container_path)))).find_elements(By.CLASS_NAME, episode_title_class)
    for i, episode in enumerate(all_episodes):
        current_episode = 'episode_' + str(i+1)

        season[current_episode] = {'title' : episode.text, 'episode_url' : episode.get_attribute('href')}

    return season

def fetch_episode_data(driver, episode):
    '''
    Input: Episode dictionary containing at least the following keys:
        'episode_url'
    Return: Episode Data as a Dictionary with Keys: 'title', 'episode_url', 'description', 'vid_url', 'sub_url'
    '''

    video_path = '//*[@id="video-player_html5_api"]/source'
    description_class = 'video-details__description'
    title_class = 'video-details__title'
    # paywall_class = 'paywall-login__link'  # to be added later?
    eng_sub = '#EXT-X-MEDIA:TYPE=SUBTITLES,GROUP-ID="subs",LANGUAGE="en",NAME="English",AUTOSELECT=YES,DEFAULT=NO,URI="'
    sub_url = ''

    # Start the web driver and wait option
    display_wait_message()
    driver.get(episode['episode_url'])
    wait = WebDriverWait(driver, 10)

    # ----- Implement checking for paywall and logging in ----- #


    # Update data
    episode['title'] = ((wait.until(EC.presence_of_element_located((By.CLASS_NAME, title_class)))).text).strip()
    episode['description'] = ((wait.until(EC.presence_of_element_located((By.CLASS_NAME, description_class)))).text).strip()
    episode['vid_url'] = (wait.until(EC.presence_of_element_located((By.XPATH, video_path)))).get_attribute("src")

    # Get subtitles if available
    playlist = requests.get(episode['vid_url']).text

    if eng_sub in playlist:
        i = playlist.index(eng_sub) + len(eng_sub)

        while playlist[i] != '"':
            sub_url += playlist[i]
            i += 1

        # Update sub_url if m3u8 playlist is found
        episode['sub_url'] = sub_url

    return episode
