'''
#  RTDL: System Functions
#  Project Page: https://github.com/EmbersAtDawn/rtdl
#  
#  Current ToDo: Find better way to quit cleanly (line 130)
# 
'''
# Case: wrong file run
if __name__ == '__main__':
    print('Please run rtdl.py instead.\n')
    input('Press ENTER to exit . . .')
    quit()
#------------------------------------------------------------IMPORT STATEMENTS------------------------------------------------------------#
import os
import textwrap
import platform
import subprocess

#----------------------------------------------------------------DISPLAYS-----------------------------------------------------------------#
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


#------------------------------------------------------------USER INTERACTION-------------------------------------------------------------#
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

def get_numerical_selection(start, stop):
    '''
    Input: Start integer, Stop integer

    Description: Asks user for input until they choose a value within the specified input range

    Return: User choice number as a string value
    '''

    # Make list of strings that are valid season selections
    valid_choices = [str(x) for x in range(start, (stop+1))]

    # Get users choice of which season to download
    choice = input('\nPlease make a selection to continue (or "exit" to quit): ')
    while True:
        if choice in valid_choices:
            break
        elif choice == 'exit': # exit opportunity
            # driver.quit()  << need to be able to close webdriver cleanly
            quit()
        else:
            choice = input('\nInvalid selection, please try again: ')
    
    return choice


#------------------------------------------------------------FILE INTERACTION-------------------------------------------------------------#
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


#-------------------------------------------------------------PROGRAM CALLS---------------------------------------------------------------#
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
