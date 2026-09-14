from flask import Flask, request, jsonify

app = Flask(__name__)

# ==========================
# URL判別ロジック
# ==========================
def extract_video_id(url: str):
    import re
    match = re.search(r"v=([a-zA-Z0-9_-]+)", url)
    if match:
        return match.group(1)

    # youtu.be形式
    match = re.search(r"youtu\.be/([a-zA-Z0-9_-]+)", url)
    if match:
        return match.group(1)

    return None


def extract_playlist_id(url: str):
    import re
    match = re.search(r"list=([a-zA-Z0-9_-]+)", url)
    if match:
        return match.group(1)
    return None


# ==========================
# API: URL変換（動画 or プレイリスト判別）
# ==========================
@app.route("/convert", methods=["POST"])
def convert():
    data = request.json
    url = data.get("url")

    playlist_id = extract_playlist_id(url)
    video_id = extract_video_id(url)

    if playlist_id:
        return jsonify({"success": True, "type": "playlist", "id": playlist_id})

    if video_id:
        return jsonify({"success": True, "type": "video", "id": video_id})

    return jsonify({"success": False, "error": "動画IDまたはプレイリストIDが見つかりません"}), 400


# ==========================
# トップページ（UI改良版）
# ==========================
@app.route("/")
def index():
    return """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>YouTube 再生ツール</title>

<script src="https://www.youtube.com/iframe_api"></script>

<style>
    body {
        font-family: "Segoe UI", sans-serif;
        background: #f5f7fa;
        margin: 0;
        padding: 0;
        display: flex;
        justify-content: center;
        align-items: flex-start;
        min-height: 100vh;
    }

    .container {
        background: #fff;
        width: 90%;
        max-width: 700px;
        margin-top: 40px;
        padding: 30px;
        border-radius: 16px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
        text-align: center;
    }

    h2 {
        margin-bottom: 20px;
        font-size: 24px;
        color: #333;
    }

    #ytInput {
        width: 100%;
        padding: 14px;
        font-size: 16px;
        border: 1px solid #ddd;
        border-radius: 10px;
        outline: none;
        transition: 0.2s;
    }

    #ytInput:focus {
        border-color: #4a90e2;
        box-shadow: 0 0 5px rgba(74,144,226,0.4);
    }

    button {
        margin-top: 15px;
        padding: 12px 20px;
        font-size: 16px;
        background: #4a90e2;
        color: #fff;
        border: none;
        border-radius: 10px;
        cursor: pointer;
        transition: 0.2s;
        width: 100%;
    }

    button:hover {
        background: #357ABD;
    }

    #status {
        margin-top: 10px;
        color: #555;
        font-size: 14px;
    }

    #player {
        margin-top: 25px;
        border-radius: 12px;
        overflow: hidden;
    }
</style>

</head>
<body>

<div class="container">
    <h2>YouTube 再生ツール</h2>

    <input id="ytInput" type="text" placeholder="動画URLまたはプレイリストURLを入力">
    <button onclick="loadFromUrl()">読み込む</button>

    <p id="status"></p>

    <div id="player"></div>
</div>

<script>
let player;

// YouTube API 読み込み後に自動で呼ばれる
function onYouTubeIframeAPIReady() {
    player = new YT.Player('player', {
        height: '360',
        width: '640',
        videoId: '',
        playerVars: {
            'playsinline': 1
        }
    });
}

// サーバーにURLを送って判別してもらう
async function loadFromUrl() {
    const url = document.getElementById("ytInput").value;

    const res = await fetch("/convert", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({url})
    });

    const data = await res.json();

    if (!data.success) {
        document.getElementById("status").innerText = "Error: " + data.error;
        return;
    }

    document.getElementById("status").innerText = "読み込み成功";

    if (data.type === "video") {
        player.loadVideoById(data.id);
    } else if (data.type === "playlist") {
        player.loadPlaylist({
            list: data.id,
            listType: 'playlist',
            index: 0
        });
    }
}
</script>

</body>
</html>
"""

# ==========================
# 起動
# ==========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
