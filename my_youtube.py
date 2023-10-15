from youtubesearchpython import VideosSearch
from yt_iframe import yt

# Set your search query here
search_query = "new devi song"

# Perform the YouTube search
videosSearch = VideosSearch(search_query, limit=10)

# Get the search results
results = videosSearch.result()

# Initialize an empty list to store video links
video_links = []

# Extract video links from the search results
for video in results['result']:
    video_links.append(video['link'])

# Initialize an empty list to store iframe tags
iframe_tags = []

# Loop through the video links and convert them to iframe tags
for video_link in video_links:
    video_id = video_link.split("v=")[1]
    iframe_code = yt.video(video_link)
    # iframe_code = iframe = yt.video(url, width=width, height=height)
    iframe_tags.append(iframe_code)

# Print the iframe HTML tags
for i, iframe in enumerate(iframe_tags, 1):
    print(f"Video {i} Iframe:")
    print(iframe)
    print("\n")
