from app import app
import re
with app.test_client() as c:
    for pid in [14, 12, 10, 8, 6, 4, 3, 1]:
        resp = c.get(f'/product/{pid}')
        html = resp.data.decode('utf-8')
        m = re.search(r'<h1[^>]*>(.*?)</h1>', html, flags=re.S)
        print(pid, m.group(1).strip() if m else 'no h1')
