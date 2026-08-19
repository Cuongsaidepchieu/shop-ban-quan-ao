from app import app
import re
with app.test_client() as c:
    resp = c.get('/')
    html = resp.data.decode('utf-8')
    hrefs = re.findall(r'href="(/product/\d+)"', html)
    print('hrefs', hrefs[:20])
    for i, line in enumerate(html.splitlines(), 1):
        if '/product/' in line or 'data-detail-url' in line or 'Thêm giỏ hàng' in line:
            print(i, line)
