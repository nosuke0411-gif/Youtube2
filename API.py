from flask import Flask, request, jsonify
import requests
import re
import isodate
import os

app = Flask(__name__)
API_KEY = os.getenv("YOUTUBE_API_KEY")


# ==========================
# プレイリストID抽出
# ==========================
def extract_playlist_id(url: str) -> str:
    match = re.search(r"list=([A-Za-z0-9_-]+)", url)
    if match:
        return match.group(1)
    raise ValueError("プレイリストIDが見つかりません")


# ==========================
# プレイリストから動画ID一覧を取得
# ==========================
def get_playlist_video_ids(playlist_id):
    url = "https://www.googleapis.com/youtube/v3/playlistItems"
    params = {
        "part": "contentDetails",
        "playlistId": playlist_id,
        "maxResults": 50,
        "key": API_KEY
    }

    res = requests.get(url, params=params).json()

    video_ids = []
    for item in res.get("items", []):
        video_ids.append(item["contentDetails"]["videoId"])

    return video_ids


# ==========================
# 動画の長さを取得（秒）
# ==========================
def get_video_duration(video_id):
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "contentDetails",
        "id": video_id,
        "key": API_KEY
    }

    res = requests.get(url, params=params).json()
    duration = res["items"][0]["contentDetails"]["duration"]
    seconds = isodate.parse_duration(duration).total_seconds()
    return seconds


# ==========================
# プレイリストの動画ID一覧を返す
# ==========================
@app.route("/playlist_items", methods=["POST"])
def playlist_items():
    data = request.json
    url = data.get("url")

    try:
        playlist_id = extract_playlist_id(url)
        video_ids = get_playlist_video_ids(playlist_id)
        return jsonify({"success": True, "videos": video_ids})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


# ==========================
# 動画の長さを返すAPI
# ==========================
@app.route("/video_duration", methods=["POST"])
def video_duration():
    data = request.json
    video_id = data.get("videoId")

    try:
        duration = get_video_duration(video_id)
        return jsonify({"success": True, "duration": duration})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


# ==========================
# HTML（iframeプレイヤー版）
# ==========================
@app.route("/")
def index():
    return """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>YouTube プレイリスト自動再生（iframe版）</title>
<style>
    body {
        font-family: sans-serif;
        display: flex;
        flex-direction: column;
        align-items: center;
        background: #f7f7f7;
        margin: 0;
        padding: 20px;
    }
    .container {
        width: 90%;
        max-width: 600px;
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
        text-align: center;
    }
    input {
        width: 100%;
        padding: 14px;
        font-size: 18px;
        border-radius: 8px;
        border: 1px solid #ccc;
    }
    button {
        width: 100%;
        padding: 14px;
        margin-top: 15px;
        font-size: 18px;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        background: #007bff;
        color: white;
    }
    #status {
        margin-top: 20px;
        font-size: 18px;
        font-weight: bold;
    }
    iframe {
        margin-top: 20px;
        width: 560px;
        height: 315px;
        max-width: 100%;
    }
</style>
</head>
<body>

<div class="container">
    <h2>YouTube プレイリスト自動再生（iframe版）</h2>

    <input id="urlInput" type="text" placeholder="プレイリストURLを入力">

    <button onclick="playlistIframeAuto()">プレイリスト自動再生</button>

    <p id="status"></p>

    <iframe id="player"
        src=""
        frameborder="0"
        allow="autoplay; encrypted-media"
        allowfullscreen>
    </iframe>
</div>

<script>
async function playlistIframeAuto() {
    const url = document.getElementById("urlInput").value;

    const res = await fetch("/playlist_items", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({url})
    });

    const data = await res.json();

    if (!data.success) {
        document.getElementById("status").innerText = "Error: " + data.error;
        return;
    }

    const videos = data.videos;
    const player = document.getElementById("player");

    document.getElementById("status").innerText = "自動再生中…";

    for (let i = 0; i < videos.length; i++) {
        const videoId = videos[i];

        // ★ iframe に動画を流し込む → ミュートされない
        player.src = `https://www.youtube.com/embed/${videoId}?autoplay=1`;

        // 動画の長さを取得
        const durationRes = await fetch("/video_duration", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({videoId})
        });

        const durationData = await durationRes.json();
        const duration = durationData.duration;

        // 動画の長さだけ待つ
        await new Promise(resolve => setTimeout(resolve, duration * 1000));
    }

    document.getElementById("status").innerText = "完了";
}
</script>

</body>
</html>
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
