from flask import Flask, request, jsonify

app = Flask(__name__)

# -------------------------
# 変換ロジック
# -------------------------
def convert_youtube_url(url: str) -> str:
    base_mobile = "https://m.youtube.com/watch?v="
    base_pc = "https://www.youtube.com/watch?v="

    if url.startswith(base_mobile):
        video_id = url[len(base_mobile):]
        return f"https://youtu.be/{video_id}"

    elif url.startswith(base_pc):
        video_id = url[len(base_pc):]
        return f"https://youtu.be/{video_id}"

    else:
        raise ValueError("対応していないURL形式です")


# -------------------------
# フロント（HTML）
# -------------------------
@app.route("/")
def index():
    return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>YouTube URL 変換ツール</title>
    <style>
        body { font-family: sans-serif; padding: 20px; }
        input { width: 300px; padding: 8px; }
        button { padding: 8px 12px; margin-left: 10px; }
        #result { margin-top: 20px; font-size: 18px; font-weight: bold; }
    </style>
</head>
<body>

    <h1>YouTube URL 変換ツール</h1>

    <input id="urlInput" type="text" placeholder="URLを入力">
    <button onclick="convert()">変換する</button>

    <p id="result"></p>
    <button id="copyBtn" onclick="copyResult()" style="display:none;">コピーする</button>

    <script>
        async function convert() {
            const url = document.getElementById("urlInput").value;

            const res = await fetch("/convert", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({url})
            });

            const data = await res.json();

            if (data.success) {
                document.getElementById("result").innerText = data.converted;
                document.getElementById("copyBtn").style.display = "inline-block";
            } else {
                document.getElementById("result").innerText = "エラー: " + data.error;
                document.getElementById("copyBtn").style.display = "none";
            }
        }

        function copyResult() {
            const text = document.getElementById("result").innerText;
            navigator.clipboard.writeText(text);
        }
    </script>

</body>
</html>
"""


# -------------------------
# API
# -------------------------
@app.route("/convert", methods=["POST"])
def convert():
    data = request.json
    url = data.get("url")

    try:
        result = convert_youtube_url(url)
        return jsonify({"success": True, "converted": result})
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
