import requests, yaml, feedparser, random, time, traceback, os, sys

BASE_URL = 'https://ruqqus.com'
SUBMIT_URL = f'{BASE_URL}/api/v1/submit'
REFRESH_URL = f'{BASE_URL}/oauth/grant'

with open('config.yaml') as config_file:
	config = yaml.safe_load(config_file)
	ID = config['id']
	access_token = config['access-token']
	SECRET = config['secret']
	REFRESH_TOKEN = config['refresh-token']
	USER_AGENT = config['user-agent']

FEEDS = ['https://thegatewaypundit.com/feed/', 'https://bigleaguepolitics.com/feed/', 'https://dailywire.com/feeds/rss.xml']
GUILDS = ['Conservatives', 'Politic', 'Politics', 'News']

print("starting...")

def refresh_token():
	print("refreshing token...")
	r = requests.post(REFRESH_URL, headers = {"User-Agent": USER_AGENT}, data = {"client_id": ID,
										     "client_secret": SECRET,
										     "grant_type": "refresh",
										     "refresh_token": REFRESH_TOKEN})
	with open('config.yaml') as config_file:
		new_config = yaml.load(config_file)

	new_config['access-token'] = r.json().get("access_token")

	with open('config.yaml', 'w') as config_file:
		yaml.dump(new_config, config_file)

	access_token = new_config['access-token']
	print(f"new access token: {new_config['access-token']}")

	#restart
	print("restarting...")
	os.execv(sys.argv[0], sys.argv)

while True:
	try:
		feed = random.choice(FEEDS)
		guild = random.choice(GUILDS)

		for entry in feedparser.parse(feed).entries:
			text = f"{entry.link} {entry.title}"
			with open('articles.txt', 'a') as f:
				f.write(text + '\n')
		else:
			with open('articles.txt') as f:
				lines = [l.rstrip() for l in f]
				randent = random.choice(lines)
				link = randent.split()[0]
				title = randent.replace(link, '')
		try:
			post = requests.post(SUBMIT_URL, headers = {"Authorization": f"Bearer {access_token}",
								    "User-Agent": USER_AGENT,
								    "X-User-Type": "Bot"},
							 data = {"title": title,
								 "url": link,
								 "board": guild})
			post.raise_for_status()
			print(f"submitted: +{guild} : {title} ({link})")
			print("going to sleep for 1 min...")
			time.sleep(60)
		except requests.exceptions.HTTPError as e:
			print(f"HTTP error {e.response.status_code} {e.response.reason}")
			time.sleep(5)
			if e.response.status_code == 401:
				#refresh token
				refresh_token()
				time.sleep(5)
			else:
				time.sleep(55)
		finally:
			#clear articles.txt
			open("articles.txt", "r+").truncate(0)
	except Exception: 
		print(traceback.format_exc())
		time.sleep(60)
	except KeyboardInterrupt:
		print("goodnight, bye bye... :(")
		quit()




