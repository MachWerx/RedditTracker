#! /usr/local/bin/python3

import sys
import time
import argparse
import os.path

def main():
  parser = argparse.ArgumentParser(description='Track stats on a Reddit post.')
  parser.add_argument('--post_class',
      default = 'uI_hDmU5GSiudtABRz_37 ',
      help='The class name for the main post.')
  parser.add_argument('--profile_path',
      help='If you want to log in as specific user, go to chrome://version/ in Chrome and pass in the profile path. You will probably want to create a new user directory for this.')
  parser.add_argument('url', help='The URL to track')
  parser.add_argument('logfile', help='The file the log should be saved to')
  args = parser.parse_args()

  # import selenium
  try:
    from selenium import webdriver
  except ImportError as e:
    print('This program needs Selenium to browse websites. For more info, see:')
    print('  https://pypi.org/project/selenium/')
    sys.exit()

  # use chromedriver
  try:
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    chrome_options = Options()
    #chrome_options.add_argument("--headless")
    if args.profile_path:
      dir = os.path.dirname(args.profile_path)
      profile = os.path.basename(args.profile_path)
      print('user data dir', dir)
      print('profile', profile)
      chrome_options.add_argument("--user-data-dir=" + dir + "");
      chrome_options.add_argument("--profile-directory=" + profile + "");
  except AttributeError as e:
    print('This program needs ChromeDriver to browse websites. For more info, see:')
    print('  https://chromedriver.chromium.org/downloads')
    sys.exit()

  # import lxml
  try:
    import lxml.html
  except ImportError as e:
    print('This program needs lxml to parse websites. For more info, see:')
    print('  https://lxml.de/installation.html')
    sys.exit()

  # Initialize log file
  #with open(args.logfile, 'w') as file:
  #    file.write(',Upvotes,Comments,Awards\n')

  print('Initializing Chrome...', end='\r')
  #with webdriver.Chrome(options=chrome_options) as driver:
  with webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options) as driver:
    while True:
      print('Grabbing web page...  ', end='\r')
      driver.get(args.url)

      print('Parsing web page... ', end='\r')
      tree = lxml.html.fromstring(driver.page_source)

      # time stamp data
      data = [time.strftime('%Y/%m/%d %H:%M:%S')]

      try:
        # get upvotes and comment count
        description = tree.xpath('//meta[@property="og:description"]/@content')[0]
        votes = description.split(' votes ')[0].replace(',','')
        data.append(votes)
        comments = description.split('and')[1].split(' ')[1].replace(',','')
        data.append(comments)

        # find badges
        main_post = tree.xpath('//*[@class="' + args.post_class + '"]')[0]
        award_ids = [s for s in main_post.xpath('.//*/@id') if 'PostAwardBadges' in s]
        for award_id in award_ids:
          award = main_post.xpath('.//*[@id="' + award_id + '"]')[0]
          badge_type = award.xpath('.//@alt')[0]
          data.append(badge_type)
          badge_count = award.getparent()[1].text
          if badge_count:
            data.append(badge_count)
          else:
            data.append('1')
      except IndexError as e:
        print('Index error at ', data[0])
      if len(data) > 1:
        stats = ','.join(data)
        with open(args.logfile, 'a') as file:
          file.write(stats + '\n')
        print(stats)
        wait(60)  # add line to log and wait a minute
      else:
        wait(3)  # no data found, wait a few seconds and retry

def wait(seconds):
  animation = '|/-\\'
  idx = 0
  stop_time = time.time() + seconds
  while time.time() < stop_time:
    print('Waiting:', int(stop_time - time.time()), animation[idx%len(animation)], end=' \r')
    idx += 1
    time.sleep(0.1)

if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt as e:
    print('Exiting')
    sys.exit()
