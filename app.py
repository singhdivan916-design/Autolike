import os
import requests
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Internal data source – hidden from the user
DATA_SOURCE_URL = os.getenv("DATA_SOURCE_URL", "https://200-like-limit-api.vercel.app/like")
DEFAULT_KEY = os.getenv("DEFAULT_KEY", "JUBAYER")
DEFAULT_SERVER = os.getenv("DEFAULT_SERVER", "bd")

@app.route('/like', methods=['GET'])
def get_likes():
    uid = request.args.get('uid')
    if not uid:
        return jsonify({"error": "Missing required parameter: uid"}), 400

    key = request.args.get('key', DEFAULT_KEY)
    server = request.args.get('server_name', DEFAULT_SERVER)

    try:
        # Internal call – not exposed to the client
        url = f"{DATA_SOURCE_URL}?uid={uid}&key={key}&server_name={server}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        raw = resp.json()
    except Exception:
        return jsonify({"error": "Unable to retrieve data at this time"}), 502

    # Transform the raw response into our own clean format
    status = raw.get("status", 0)
    if status == 1:
        return jsonify({
            "success": True,
            "user": {
                "uid": raw.get("UID"),
                "nickname": raw.get("PlayerNickname")
            },
            "likes": {
                "current": raw.get("LikesafterCommand"),
                "before": raw.get("LikesbeforeCommand"),
                "added": raw.get("LikesGivenByAPI"),
                "net_change": raw.get("LikesafterCommand", 0) - raw.get("LikesbeforeCommand", 0)
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }), 200
    else:
        return jsonify({
            "success": False,
            "error": "Request could not be completed",
            "code": status
        }), 400

if __name__ == "__main__":
    app.run(debug=True, port=5000)
