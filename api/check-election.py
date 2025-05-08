import requests
import xmltodict
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/check-election', methods=['GET'])
def check_election():
    try:
        # URL RSS feedu
        feed_url = 'https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114'
        
        # Klicová slova pro detekci volby papeže
        keywords = [
            'pope elected', 'new pope', 'white smoke', 'new pontiff',
            'habemus papam', 'papal conclave', 'vatican elects',
            'successor to francis', 'new vatican leader',
            'conclave selects pope', 'st. peters square',
            'new head of catholic church'
        ]
        
        # Načtení a parsování RSS feedu
        response = requests.get(feed_url)
        feed = xmltodict.parse(response.text)
        
        # Získání položek z RSS feedu
        items = feed['rss']['channel']['item']
        
        # Nastavení prahu pro novost článku (posledních 48 hodin)
        recent_threshold = 48 * 60 * 60  # 48 hodin v sekundách
        now = time.time()
        
        # Filtrace článků podle věku a klíčových slov
        matches = []
        for item in items:
            pub_date = item['pubDate']
            pub_timestamp = time.mktime(time.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z'))
            age = now - pub_timestamp
            
            if age > recent_threshold:
                continue
            
            title = item['title'].lower()
            description = item.get('description', '').lower()
            if any(keyword in title or keyword in description for keyword in keywords):
                matches.append({
                    'title': item['title'],
                    'link': item['link'],
                    'pubDate': item['pubDate']
                })
        
        # Odeslání výsledků
        response_payload = {
            'popeElected': len(matches) > 0,
            'articles': matches
        }

        return jsonify(response_payload)

    except Exception as e:
        print(f"Error checking election status: {e}")
        return jsonify({'error': 'Election check failed'}), 500

if __name__ == '__main__':
    app.run(debug=True)
