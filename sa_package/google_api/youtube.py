import datetime
import pandas as pd
from googleapiclient.discovery import build

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

class YoutubeApi:

    def __init__(self, api_key):
        self.__youtube = build(
            YOUTUBE_API_SERVICE_NAME,
            YOUTUBE_API_VERSION, 
            developerKey=api_key
        )


    def get_channel_detail(self, channel_id):

        search_response = self.__youtube.channels().list(
            part="id, snippet, statistics",
            fields="items(id,snippet(title),statistics(subscriberCount))",
            id=channel_id,
        ).execute()


        channel_name = None
        subscribers = None

        for item in search_response.get("items", []):
            channel_name = item["snippet"]["title"]
            subscribers = item["statistics"]["subscriberCount"]

        return {'channel_name':channel_name, 'subscribers':subscribers}



    def get_channel_videos(self, channel_id, published_after=None, published_before=None):
        
        video_df = pd.DataFrame()

        if published_before is None:
            published_before = datetime.datetime.today().strftime("%Y-%m-%dT%H:%M:%SZ")

        if published_after is None:
            published_after = "1970-01-01T00:00:00Z"

        page_token = ""
        while True:
            search_response = self.__youtube.search().list(
                part="id, snippet",
                fields="items(id,snippet(title, channelId, publishTime))",
                channelId=channel_id,
                maxResults=50,
                order="date",
                pageToken=page_token,
                publishedBefore=published_before,
                publishedAfter=published_after
            ).execute()

            for item in search_response.get("items", []):
                if item["id"]["kind"] == "youtube#video":
                    try:
                        video_df = video_df.append({
                            "video_id": item["id"]["videoId"],
                            "title": item["snippet"]["title"],
                            "channel_id": item["snippet"]["channelId"],
                            "upload_date": datetime.datetime.strptime(item["snippet"]["publishTime"], "%Y-%m-%dT%H:%M:%SZ")
                        }, ignore_index=True)
                    except Exception as e:
                        print()
                        print(item)

            next_page_token = search_response.get("nextPageToken", None)
            if next_page_token is None:
                break
            else:
                page_token = next_page_token

        return video_df



    def get_video_detail(self, video_id):

        search_response = self.__youtube.videos().list(
            part="id, snippet",
            id=video_id,
        ).execute()

        title = None
        upload_date = None
        channel_id = None

        for item in search_response.get("items", []):
            if item["kind"] == "youtube#video":
                title = item["snippet"]["title"]
                upload_date = datetime.datetime.strptime(item["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ")
                channel_id = item["snippet"]["channelId"]

        return {'title': title, 'upload_date': upload_date, 'channel_id': channel_id}