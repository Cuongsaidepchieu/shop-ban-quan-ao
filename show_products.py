from app import query_db, app

with app.app_context():
    count = query_db('SELECT COUNT(*) as count FROM products', one=True)
    print('products count (via app):', count['count'] if count else 0)
    sample = query_db('SELECT id, name FROM products ORDER BY id DESC LIMIT 5')
    print('sample (via app):')
    for r in sample:
        print(r['id'], r['name'])
