import time
import board
import displayio
import framebufferio
import rgbmatrix
import terminalio
import json
import urllib.request
from adafruit_display_text import label

displayio.release_displays()
matrix = rgbmatrix.RGBMatrix(
    width=64, height=32, bit_depth=4,
    rgb_pins=[board.D6, board.D5, board.D9, board.D11, board.D10, board.D12],
    addr_pins=[board.A5, board.A4, board.A3, board.A2],
    clock_pin=board.D13, latch_pin=board.D0, output_enable_pin=board.D1
)
display = framebufferio.FramebufferDisplay(matrix, auto_refresh=True)
main_group = displayio.Group()

YOUTUBE_CHANNEL_ID = "CHANNEL_ID"
YOUTUBE_API_KEY = "API_KEY"
GITHUB_USER = "GITHUB_USERNAME"
GITHUB_REPO = "GITHUB_REPO"
GITHUB_TOKEN = "GITHUB_TOKEN"

COLORS = {
    "youtube": 0xFF0000,
    "github": 0x00FF00,
    "text": 0xFFFFFF,
    "error": 0xFFA500
}

text_lines = [
    label.Label(terminalio.FONT, color=COLORS["text"], y=8),
    label.Label(terminalio.FONT, color=COLORS["text"], y=18),
    label.Label(terminalio.FONT, color=COLORS["text"], y=28)
]

for line in text_lines:
    main_group.append(line)

display.root_group = main_group

def scroll_text(lines, speed=0.1):
    max_x = max(line.bounding_box[2] for line in lines if line.text)
    start_x = 64
    
    for i in range(start_x, -max_x, -1):
        for idx, line in enumerate(lines):
            line.x = i + (idx * 10)
        time.sleep(speed)

def get_youtube_stats():
    try:
        url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics,snippet&id={YOUTUBE_CHANNEL_ID}&key={YOUTUBE_API_KEY}"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            return {
                "title": data["items"][0]["snippet"]["title"],
                "views": int(data["items"][0]["statistics"]["viewCount"]),
                "subs": int(data["items"][0]["statistics"]["subscriberCount"])
            }
    except Exception as e:
        print("YouTube Error:", e)
        return None

def get_github_stats():
    try:
        url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}"
        headers = {}
        if GITHUB_TOKEN:
            headers["Authorization"] = f"token {GITHUB_TOKEN}"
        
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return {
                "stars": data["stargazers_count"],
                "forks": data["forks_count"],
                "issues": data["open_issues_count"]
            }
    except Exception as e:
        print("GitHub Error:", e)
        return None

def format_number(num):
    if isinstance(num, str): return num
    if num >= 1_000_000: return f"{num/1_000_000:.1f}M"
    if num >= 1_000: return f"{num/1_000:.1f}K"
    return str(num)

def show_data(platform, data):
    text_lines[0].color = COLORS[platform]
    text_lines[1].color = COLORS["text"]
    text_lines[2].color = COLORS["text"]
    
    if platform == "youtube":
        text_lines[0].text = f"YT: {data['title'][:16]}"
        text_lines[1].text = f"Views: {format_number(data['views'])}"
        text_lines[2].text = f"Subs: {format_number(data['subs'])}"
    else:
        text_lines[0].text = f"GH: {GITHUB_REPO}"
        text_lines[1].text = f"Stars: {format_number(data['stars'])}"
        text_lines[2].text = f"Forks: {format_number(data['forks'])}"
    
    scroll_text(text_lines)

while True:
    try:
        yt_data = get_youtube_stats()
        if yt_data:
            show_data("youtube", yt_data)
        
        gh_data = get_github_stats()
        if gh_data:
            show_data("github", gh_data)
        
    except Exception as e:
        text_lines[0].text = "API Error"
        text_lines[1].text = "Check"
        text_lines[2].text = "Configuration"
        scroll_text(text_lines)
        time.sleep(5)