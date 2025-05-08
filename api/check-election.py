from flask import Flask, jsonify
from flask_cors import CORS
import requests
import xmltodict
from datetime import datetime, timedelta

app = Flask(__name__)  # Správné použití __name__
CORS(app)

@app.route("/api/check-election", methods=["GET"])
def check_election():
    try:
        feed_url = "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114"
        keywords = [
            "pope elected", "new pope", "white smoke", "new pontiff",
            "habemus papam", "papal conclave", "vatican elects",
            "successor to francis", "new vatican leader",
            "conclave selects pope", "st. peter's square",
            "new head of catholic church"
        ]

        response = requests.get(feed_url, timeout=10)
        response.raise_for_status()  # Přidání kontroly HTTP chyb
        data = xmltodict.parse(response.content)

        items = data.get("rss", {}).get("channel", {}).get("item", [])
        if not isinstance(items, list):
            items = [items]

        now = datetime.utcnow()
        recent_cutoff = now - timedelta(hours=48)

        matches = []
        for item in items:
            pub_date_str = item.get("pubDate", "")
            try:
                pub_date = datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S %z")
            except ValueError:
                continue

            if pub_date.replace(tzinfo=None) < recent_cutoff:
                continue

            title = item.get("title", "").lower()
            desc = item.get("description", "").lower()
            if any(keyword in title or keyword in desc for keyword in keywords):
                matches.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "pubDate": item.get("pubDate", "")
                })

        return jsonify({
            "popeElected": len(matches) > 0,
            "articles": matches
        })

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request failed: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
