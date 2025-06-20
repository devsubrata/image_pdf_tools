from django.shortcuts import render
from django.http import JsonResponse

import requests
import os

# Replace with your actual API key
API_KEY = os.getenv("YT_API_KEY")


def songs_by_artist(request):
    return render(request, "youtube-api/top_songs_by_artist.html")

def top_youtube_songs(request):
    return render(request, "youtube-api/top_youtube_songs.html")


def youtube_search(request):
    query = request.GET.get("q", "English Songs")
    total_needed = int(request.GET.get("count", 50))
    video_ids = set()
    next_page_token = None

    # Pagination loop to collect enough unique video IDs
    try:
        while len(video_ids) < total_needed:
            search_params = {
                'part': 'snippet',
                'q': query,
                'type': 'video',
                'videoCategoryId': '10',
                'maxResults': 50,
                'order': 'viewCount',
                'key': API_KEY
            }
            if next_page_token:
                search_params['pageToken'] = next_page_token

            response = requests.get("https://www.googleapis.com/youtube/v3/search", params=search_params)

            # 🚨 Handle quota error
            if response.status_code == 403:
                return JsonResponse({
                    "error": "YouTube API quota exceeded. Please try again after midnight PST."
                }, status=403)

            # 🚨 Handle other bad responses
            if response.status_code != 200:
                return JsonResponse({
                    "error": f"Failed to fetch data from YouTube API. Status code: {response.status_code}"
                }, status=500)
            
            data = response.json()
            items = data.get('items', [])
            ids = [item['id']['videoId'] for item in items if 'videoId' in item['id']]
            video_ids.update(ids)

            next_page_token = data.get('nextPageToken')
            if not next_page_token:
                break

        video_ids = list(video_ids)[:total_needed]
        final_results = []

        # Fetch video details in chunks of 50 (API limit)
        for i in range(0, len(video_ids), 50):
            chunk = video_ids[i:i + 50]
            stats_params = {
                'part': 'snippet,statistics',
                'id': ','.join(chunk),
                'key': API_KEY
            }
            stats_response = requests.get("https://www.googleapis.com/youtube/v3/videos", params=stats_params)

            if stats_response.status_code == 403:
                return JsonResponse({
                    "error": "YouTube API quota exceeded (videos endpoint). Try again tomorrow."
                }, status=403)

            if stats_response.status_code != 200:
                return JsonResponse({
                    "error": f"Failed to fetch video stats. Status code: {stats_response.status_code}"
                }, status=500)

            for item in stats_response.json().get('items', []):
                view_count = int(item["statistics"].get("viewCount", 0))
                final_results.append({
                    'title': item["snippet"]["title"],
                    'channel': item["snippet"]["channelTitle"],
                    'views': view_count,
                    'url': f"https://www.youtube.com/watch?v={item['id']}"
                })

        # Sort final results by views descending to get top viewed videos
        final_results.sort(key=lambda x: x['views'], reverse=True)
        return JsonResponse(final_results[:total_needed], safe=False)
    
    except Exception as e:
        return JsonResponse({"error": f"Server error: {str(e)}"}, status=500)

# https://www.googleapis.com/youtube/v3/search?part=snippet&q=Taylor+Swift+songs&type=video&videoCategoryId=10&maxResults=50&order=viewCount&key=YOUR_API_KEY
