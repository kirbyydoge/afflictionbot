import os
import botdb as bdb
from googleapiclient.discovery import build

BOT_TOKEN = os.environ["BOT_TOKEN"]
GOOGLE_DEV_KEY = os.environ["GOOGLE_DEV_KEY"]
cached_youtubers = []
cached_videos = {}
youtube = None

youtubers = bdb.fetch_youtubers()

def init_youtubers():
	global youtube
	youtube = build('youtube','v3',developerKey=GOOGLE_DEV_KEY)
	for youtuber in youtubers:
		cached_youtubers.append((youtuber["name"], youtuber["url"]))
		req = youtube.playlistItems().list(
			playlistId = "UUXin0u5SrVEBjn5LhOoG97A",
			part = "snippet",
			maxResults = 1
		)
		res = req.execute()
		video_id = res['items'][0]['snippet']['resourceId']['videoId']
		cached_videos[youtuber["name"]] = video_id

def loop():
	for youtuber in cached_youtubers:
		req = youtube.playlistItems().list(
			playlistId = "UUXin0u5SrVEBjn5LhOoG97A",
			part = "snippet",
			maxResults = 1
		)
		res = req.execute()
		video_id = res['items'][0]['snippet']['resourceId']['videoId']
		if cached_videos[youtuber[0]] != video_id:
			print("new video")
		else:
			print("existing video")

init_youtubers()
loop()