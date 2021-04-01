'''
# Release: alpha
# 
# Author: Michael K
# GitHub: @EmbersAtDawn
# 
'''

#--------------------------------------------------------IMPORT STATEMENTS--------------------------------------------------------#
import os
import time
import requests
import textwrap
import platform
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#------------------------------------------------------------FUNCTIONS------------------------------------------------------------#
def display_welcome_message():

    print('--------------------------------------------------------------')
    print('|  Welcome to the Unofficial Roosterteeth Series Downloader  |')
    print('--------------------------------------------------------------\n')

def display_wait_message():

    print('\nWaiting for server response . . .\n')

def display_series_info(series):
    '''
    Input: Show series as a dictionary containing the following keys:
        'title'
        'num_seasons'
        'summary'
    '''

    print('Information Found for this Series')
    print('---------------------------------')
    print('Title: {}'.format(series['title']))
    print('Seasons: {}'.format(series['num_seasons']))
    print('Summary: ')
    print('{}'.format(textwrap.fill(series['summary'], width=120, initial_indent=' '*9, subsequent_indent=' '*9)))
    print()

def display_seasons(num_seasons):
    '''
    Input: An integer indicating the total number of seasons in a series

    Display:
        [ 1 ] - Season 1
        etc

    Return: User choice via get_numerical_selection()
    '''

    # Display the seasons that are available for download
    first_option = 1
    last_option = num_seasons
    print('Seasons Available for Download in this Series')
    print('---------------------------------------------')
    for i in range(num_seasons):
        print('[ {num} ] - Season {num}'.format(num = i+1))

    return get_numerical_selection(first_option, last_option)

def display_season_episodes(season):
    '''
    Input: Show season containing at least the following keys:
        'title'

    Display:
        [ 1 ] - Episode 1 Title
        etc

    Format: season['episode#']['title' : 'episode_title']

    Return: User choice via get_numerical_selection()
    '''

    # Display the seasons that are available for download
    first_option = 1
    last_option = len(season.values())
    print('Episodes Available for Download in this Season')
    print('----------------------------------------------')
    if last_option > 1:
        print('[ {} ] - {}'.format('0', 'All Episodes'))
        first_option = 0
    for i, episode in enumerate(season.values()):
        print('[ {} ] - {}'.format(i+1, episode['title']))

    return get_numerical_selection(first_option, last_option)


def ffmpeg_present():
    '''
    Return: True / False
    '''

    ffmpeg_path = os.path.join('C:\\', 'FFmpeg', 'bin', 'ffmpeg.exe')
    ffmpeg_path2 = os.path.join('C:\\', 'bin', 'ffmpeg.exe')
    if ( os.path.exists(ffmpeg_path) or (os.path.exists(ffmpeg_path2)) ):
        print('Yay, FFmpeg is installed and we can get going!!\n')
        return True
    else:
        print("You'll need to get FFmpeg installed first. :/\n")
        return False
    

def get_numerical_selection(start, stop):
    '''
    Input: Start integer, Stop integer

    Description: Asks user for input until they choose a value within the specified input range

    Return: User choice number as a string value
    '''

    # Make list of strings that are valid season selections
    valid_choices = [str(x) for x in range(start, (stop+1))]

    # Get users choice of which season to download
    choice = input('\nPlease make a selection to continue: ')
    while True:
        if choice in valid_choices:
            break
        elif choice == 'exit': # exit opportunity
            driver.quit()
            quit()
        else:
            choice = input('\nInvalid selection, please try again: ')
    
    return choice

def get_series_url():
    '''
    Return: Verified URL
    '''

    base = 'https://roosterteeth.com'
    default = 'https://roosterteeth.com/series/rwby'
    url = input('\nPlease enter the home URL of a series on Roosterteeth.com eg: https://roosterteeth.com/series/rwby\n')
    while not url.startswith(base):
        if url == '':
            url = default
            print('Using default URL [{}]\n'.format(default))
            break
        elif url == 'exit':
            exit()
        else:
            url = input('Invalid URL. Please try again: ')
    # Clean URL if user accidently pasted a link to a season
    if "?season=" in url:
        url = url[:url.index('?season=')]
    return url


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


def create_save_path(show_title, season_number):
    '''
    Input: Show title, Season number

    Description: Creates folder tree for storing episodes
        ie. C:/Users/Username/Desktop/RWBY/Season 1

    Return: Save path as a string
    '''
    season = 'Season ' + season_number
    show_folders = os.path.join(show_title, season)

    if platform.system() == 'Windows':
        desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    else:
        desktop = os.path.expanduser('~Desktop')

    save_path = os.path.join(desktop, show_folders)

    if not os.path.exists(save_path):
        os.makedirs(save_path)
        print('\nDirectory "{}" created.'.format(save_path))
    else:
        print('\nDirectory "{}" already exists.'.format(save_path))
    
    return save_path


def run_ffmpeg(episode, save_path):
    '''
    Input: Episode dictionary containing at least the following keys:
        'title'
        'description'
        'vid_url'
        'sub_url'
    Save Path as a string:
        ie. C:/Users/Username/Desktop/RWBY/Season 1
    '''

    # Create safe save file name and store on desktop
    safe_title = ''
    safe_chars = (' ', '_', '-')

    for char in episode['title']:
        if char.isalnum() or char in safe_chars:
            safe_title += char
        else:
            safe_title += '_'
    
    safe_title = safe_title.strip() + '.mp4'

    save_file = os.path.join(save_path, safe_title)

    # Check if video already exists before downloading
    if os.path.exists(save_file):
        print('"{}" already exists! Skipping redownload...\n'.format(safe_title))
    else:
        if 'sub_url' in episode.keys():  # Has subtitles
            args = [
                'ffmpeg',
                '-hide_banner',
                '-i "{}"'.format(episode['vid_url']),
                '-i "{}"'.format(episode['sub_url']),
                '-c:v copy',
                '-c:a copy',
                '-c:s mov_text',
                '-metadata title="{}"'.format(episode['title'].replace('"', "'")),
                '-metadata description="{}"'.format(episode['description'].replace('"', "'")),
                '-metadata:s:v:0 language=eng',
                '-metadata:s:a:0 language=eng',
                '-metadata:s:s:0 language=eng',
                '-f mp4',
                '"{}"'.format(save_file)
            ]
        else:  # No subtitles
            args = [
                'ffmpeg',
                '-hide_banner',
                '-i "{}"'.format(episode['vid_url']),
                '-c:v copy',
                '-c:a copy',
                '-metadata title="{}"'.format(episode['title'].replace('"', "'")),
                '-metadata description="{}"'.format(episode['description'].replace('"', "'")),
                '-metadata:s:v:0 language=eng',
                '-metadata:s:a:0 language=eng',
                '-f mp4',
                '"{}"'.format(save_file)
            ]

        subprocess.run(' '.join(args))


#--------------------------------------------------------------MAIN---------------------------------------------------------------#
if __name__ == '__main__':
    series = {}

    display_welcome_message()

    if ffmpeg_present():

        # Get series URL from user and make sure it's valid || exit possible
        try:
            series_url = get_series_url()
        except Exception:
            print('ERROR: Failed to verify URL.')


        # Start the webdriver
        try:
            print('Starting webdriver. This may take a moment...')
            options = webdriver.FirefoxOptions()
            options.add_argument('-headless')
            driver = webdriver.Firefox(options=options)
        except Exception:
            print('CRITICAL ERROR: Failed to start the web driver.')
            quit()


        # Use URL to get series information
        try:
            series['info'] = fetch_series_info(driver, series_url)
        except Exception:
            print('ERROR: Failed to get series information.')
            driver.quit()
            quit()


        # Display the series info for user to see
        try:
            display_series_info(series['info'])
        except Exception:
            print('ERROR: Failed to display series information.')
            driver.quit()
            quit()



        # Print a menu based on the series found and get user selection
        try:
            selected_season = display_seasons(series['info']['num_seasons'])
            current_season = 'season_' + selected_season
        except Exception:
            print('ERROR: Failed to get season selection.')
            driver.quit()
            quit()

        # Create save directory
        try:
            save_path = create_save_path(series['info']['title'], selected_season)
        except Exception:
            print('ERROR: Failed to create / verify save directory.')
            driver.quit()
            quit()



        # Get episode(s) data based on user selected season
        try:
            series[current_season] = fetch_season_episodes(driver, series['info']['series_url'], selected_season)
        except Exception:
            print('ERROR: Failed to get episode data for the selected season.')
            driver.quit()
            quit()

        try:
            selected_episode = display_season_episodes(series[current_season])
        except Exception:
            print('ERROR: Failed to get episode selection.')
            driver.quit()
            quit()

        try:
            if selected_episode == '0':
                # Download all episodes in the season
                num_episodes = len(series[current_season].values())
                print('Downloading all episodes in this season...')
                i = 1
                while i <= num_episodes:
                    current_episode = 'episode_' + str(i)
                    series[current_season][current_episode] = fetch_episode_data(driver, series[current_season][current_episode])
                    # Run ffmpeg on the current episode
                    run_ffmpeg(series[current_season][current_episode], save_path)
                    i += 1
            else:
                # Download only the selected episode
                current_episode = 'episode_' + selected_episode
                series[current_season][current_episode] = fetch_episode_data(driver, series[current_season][current_episode])
                # Run ffmpeg on the current episode
                run_ffmpeg(series[current_season][current_episode], save_path)
        except Exception:
            print('ERROR: Failed to download episode(s).')



        # Close web driver
        driver.quit()

        print('\n========== Finished All Operations! ==========\n')
    time.sleep(0.5)
    input("Press Enter to Exit . . .")