'''
#  RTDL: Main
#  Project Page: https://github.com/EmbersAtDawn/rtdl
#  
#  Current ToDo: 
# 
'''
#------------------------------------------------------------IMPORT STATEMENTS------------------------------------------------------------#
import system as sys
import web
import time

#------------------------------------------------------------------MAIN-------------------------------------------------------------------#
if __name__ == '__main__':
    series = {}

    sys.display_welcome_message()

    if sys.ffmpeg_present():

        # Get series URL from user and make sure it's valid || exit possible
        try:
            series_url = sys.get_series_url()
        except Exception:
            print('ERROR: Failed to verify URL.')


        # Start the webdriver
        try:
            print('Starting webdriver. This may take a moment...')
            options = web.webdriver.FirefoxOptions()
            options.add_argument('-headless')
            driver = web.webdriver.Firefox(options=options)
        except Exception:
            print('CRITICAL ERROR: Failed to start the web driver.')
            quit()


        # Use URL to get series information
        try:
            series['info'] = web.fetch_series_info(driver, series_url)
        except Exception:
            print('ERROR: Failed to get series information.')
            driver.quit()
            quit()


        # Display the series info for user to see
        try:
            sys.display_series_info(series['info'])
        except Exception:
            print('ERROR: Failed to display series information.')
            driver.quit()
            quit()



        # Print a menu based on the series found and get user selection
        try:
            selected_season = sys.display_seasons(series['info']['num_seasons'])
            current_season = 'season_' + selected_season
        except Exception:
            print('ERROR: Failed to get season selection.')
            driver.quit()
            quit()

        # Create save directory
        try:
            save_path = sys.create_save_path(series['info']['title'], selected_season)
        except Exception:
            print('ERROR: Failed to create / verify save directory.')
            driver.quit()
            quit()



        # Get episode(s) data based on user selected season
        try:
            series[current_season] = web.fetch_season_episodes(driver, series['info']['series_url'], selected_season)
        except Exception:
            print('ERROR: Failed to get episode data for the selected season.')
            driver.quit()
            quit()

        try:
            selected_episode = sys.display_season_episodes(series[current_season])
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
                    series[current_season][current_episode] = web.fetch_episode_data(driver, series[current_season][current_episode])
                    # Run ffmpeg on the current episode
                    sys.run_ffmpeg(series[current_season][current_episode], save_path)
                    i += 1
            else:
                # Download only the selected episode
                current_episode = 'episode_' + selected_episode
                series[current_season][current_episode] = web.fetch_episode_data(driver, series[current_season][current_episode])
                # Run ffmpeg on the current episode
                sys.run_ffmpeg(series[current_season][current_episode], save_path)
        except Exception:
            print('ERROR: Failed to download episode(s).')



        # Close web driver
        driver.quit()

        print('\n========== Finished All Operations! ==========\n')
    time.sleep(0.5)
    input("Press Enter to Exit . . .")
# %%
