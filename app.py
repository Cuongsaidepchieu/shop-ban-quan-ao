import os
import pymysql
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from wtforms import StringField, PasswordField, SubmitField, DecimalField, IntegerField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange

app = Flask(__name__)
app.config['SECRET_KEY'] = 'changeme123456789'


MYSQL_HOST = '127.0.0.1'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PASSWORD = ''          
MYSQL_DB = 'fashion_shop'    

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Bạn cần đăng nhập để truy cập trang này.'

class User(UserMixin):
    def __init__(self, id, name, email, password_hash, is_admin):
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.is_admin = is_admin

    def get_id(self):
        return str(self.id)

    @property
    def is_authenticated(self):
        return True

@login_manager.user_loader
def load_user(user_id):
    
    row = query_db('SELECT id, name, email, password_hash, is_admin FROM users WHERE id = %s', [user_id], one=True)
    if row:
        return User(row['id'], row['name'], row['email'], row['password_hash'], row['is_admin'])
    return None


class RegisterForm(FlaskForm):
    name = StringField('Tên', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mật khẩu', validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField('Xác nhận mật khẩu', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Đăng ký')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mật khẩu', validators=[DataRequired()])
    submit = SubmitField('Đăng nhập')

class ProductForm(FlaskForm):
    name = StringField('Tên sản phẩm', validators=[DataRequired(), Length(min=3, max=100)])
    price = DecimalField('Giá (đ)', validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField('Số lượng', validators=[DataRequired(), NumberRange(min=0)])
    category = StringField('Danh mục', validators=[DataRequired(), Length(min=2, max=50)])
    description = TextAreaField('Mô tả', validators=[DataRequired(), Length(min=10, max=500)])
    image = StringField('Ảnh (URL)', validators=[DataRequired(), Length(min=5, max=200)])
    is_featured = BooleanField('Sản phẩm nổi bật')
    submit = SubmitField('Lưu sản phẩm')

class CheckoutForm(FlaskForm):
    fullname = StringField('Họ và tên', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Số điện thoại', validators=[DataRequired(), Length(min=9, max=15)])
    address = TextAreaField('Địa chỉ giao hàng', validators=[DataRequired(), Length(min=10, max=200)])
    submit = SubmitField('Xác nhận đặt hàng')

class ReviewForm(FlaskForm):
    name = StringField('Tên', validators=[DataRequired(), Length(min=3, max=50)])
    comment = TextAreaField('Đánh giá', validators=[DataRequired(), Length(min=5, max=300)])
    submit = SubmitField('Gửi đánh giá')


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor, 
            autocommit=True
        )
        g._database = db
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    db = get_db()
    query = query.replace('?', '%s') 
    with db.cursor() as cur:
        cur.execute(query, args)
        rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=(), commit=False, many=False, lastrowid=False):
    db = get_db()
    query = query.replace('?', '%s')
    with db.cursor() as cur:
        if many:
            cur.executemany(query, args)
        else:
            cur.execute(query, args)
        rowid = cur.lastrowid if lastrowid else None
    return rowid

def init_db():
    db = get_db()
    with app.open_resource('schema_mysql.sql', mode='r', encoding='utf-8') as f:
        sql = f.read()
    with db.cursor() as cur:
        for statement in sql.split(';'):
            statement = statement.strip()
            if statement:
                cur.execute(statement)
    seed_data()

def seed_data():
    existing = query_db('SELECT COUNT(*) as count FROM products', one=True)
    if existing and existing['count'] == 0:
        products = [
            ('Áo sơ mi linen xanh', 450000, 25, 'Áo', 'Áo sơ mi linen thoáng mát, phong cách hiện đại.', 'https://images.unsplash.com/photo-1521334884684-d80222895322?auto=format&fit=crop&w=1200&q=80', 1),
            ('Quần jeans slimfit', 520000, 30, 'Quần', 'Jeans slimfit co giãn, phù hợp mặc đi làm và dạo phố.', 'https://images.unsplash.com/photo-1512436991641-6745cdb1723f?auto=format&fit=crop&w=1200&q=80', 1),
            ('Váy maxi hoa nhí', 650000, 20, 'Váy', 'Váy maxi nhẹ nhàng, thiết kế tôn dáng.', 'https://images.unsplash.com/photo-1503341455253-b2e723bb3dbb?auto=format&fit=crop&w=1200&q=80', 0),
            ('Áo khoác denim', 780000, 15, 'Áo khoác', 'Áo khoác denim thời thượng, dễ phối đồ.', 'https://images.unsplash.com/photo-1520975922972-8f90b7f145d2?auto=format&fit=crop&w=1200&q=80', 1),
            ('Set đồ thể thao', 720000, 18, 'Set đồ', 'Set áo thun + quần jogger thoải mái khi vận động.', 'https://images.unsplash.com/photo-1520975911207-19c05b6e1f9f?auto=format&fit=crop&w=1200&q=80', 0),
        ]
        execute_db('INSERT INTO products (name, price, stock, category, description, image, is_featured) VALUES (%s, %s, %s, %s, %s, %s, %s)', products, many=True)

    existing_admin = query_db('SELECT COUNT(*) as count FROM users WHERE is_admin = 1', one=True)
    if not existing_admin or existing_admin['count'] == 0:
        password_hash = bcrypt.generate_password_hash('admin123').decode('utf-8')
        execute_db('INSERT INTO users (name, email, password_hash, is_admin) VALUES (%s, %s, %s, %s)', ('Admin Shop', 'admin@shop.com', password_hash, 1))

@app.before_request
def ensure_db():
    try:
        query_db('SELECT 1 FROM users LIMIT 1', one=True)
    except Exception:
        init_db()

@app.context_processor
def inject_categories():
    categories = query_db('SELECT DISTINCT category FROM products')
    cart = session.get('cart', {})
    return {'categories': [row['category'] for row in categories] if categories else [], 'cart_quantity': sum(cart.values())}

@app.route('/')
def index():
    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    if search:
        products = query_db("SELECT * FROM products WHERE name LIKE %s OR category LIKE %s OR description LIKE %s", [f'%{search}%', f'%{search}%', f'%{search}%'])
    elif category:
        products = query_db('SELECT * FROM products WHERE category = %s', [category])
    else:
        products = query_db('SELECT * FROM products ORDER BY is_featured DESC, id DESC')
    featured = query_db('SELECT * FROM products WHERE is_featured = 1 LIMIT 4')
    return render_template('index.html', products=products, featured=featured, search=search, category=category)

@app.route('/product/<int:product_id>', methods=['GET', 'POST'])
def product_detail(product_id):
    product = query_db('SELECT * FROM products WHERE id = %s', [product_id], one=True)
    if not product:
        return redirect(url_for('index'))
    form = ReviewForm()
    if form.validate_on_submit():
        execute_db('INSERT INTO reviews (product_id, name, comment) VALUES (%s, %s, %s)', (product_id, form.name.data, form.comment.data))
        flash('Cảm ơn bạn đã gửi đánh giá!', 'success')
        return redirect(url_for('product_detail', product_id=product_id))
    reviews = query_db('SELECT * FROM reviews WHERE product_id = %s ORDER BY created_at DESC', [product_id])
    return render_template('product.html', product=product, form=form, reviews=reviews)

@app.route('/add-to-cart/<int:product_id>')
def add_to_cart(product_id):
    product = query_db('SELECT * FROM products WHERE id = %s', [product_id], one=True)
    if not product:
        flash('Sản phẩm không tồn tại.', 'danger')
        return redirect(url_for('index'))
    cart = session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    session['cart'] = cart
    flash(f'Đã thêm {product["name"]} vào giỏ hàng.', 'success')
    return redirect(request.referrer or url_for('index'))

@app.route('/cart', methods=['GET', 'POST'])
def cart():
    cart = session.get('cart', {})
    products = []
    total = 0
    for product_id, quantity in cart.items():
        p = query_db('SELECT * FROM products WHERE id = %s', [product_id], one=True)
        if p:
            item_total = p['price'] * quantity
            total += item_total
            products.append({'product': p, 'quantity': quantity, 'item_total': item_total})
    return render_template('cart.html', products=products, total=total)

@app.route('/update-cart', methods=['POST'])
def update_cart():
    cart = session.get('cart', {})
    for product_id, quantity in request.form.items():
        if product_id.startswith('quantity_'):
            pid = product_id.replace('quantity_', '')
            try:
                qty = int(quantity)
            except ValueError:
                qty = 1
            if qty <= 0:
                cart.pop(pid, None)
            else:
                cart[pid] = qty
    session['cart'] = cart
    flash('Giỏ hàng đã được cập nhật.', 'success')
    return redirect(url_for('cart'))

@app.route('/remove-from-cart/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    cart.pop(str(product_id), None)
    session['cart'] = cart
    flash('Đã xóa sản phẩm khỏi giỏ hàng.', 'info')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = session.get('cart', {})
    if not cart:
        flash('Giỏ hàng trống, hãy thêm sản phẩm trước khi thanh toán.', 'warning')
        return redirect(url_for('index'))
    form = CheckoutForm()
    products = []
    total = 0
    item_count = 0
    for product_id, quantity in cart.items():
        p = query_db('SELECT * FROM products WHERE id = %s', [product_id], one=True)
        if p:
            item_total = p['price'] * quantity
            total += item_total
            item_count += quantity
            products.append({'product': p, 'quantity': quantity, 'item_total': item_total})
    if form.validate_on_submit():
        order_id = execute_db('INSERT INTO orders (fullname, email, phone, address, total_amount) VALUES (%s, %s, %s, %s, %s)',
                    (form.fullname.data, form.email.data, form.phone.data, form.address.data, total), lastrowid=True)
        for item in products:
            execute_db('INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (%s, %s, %s, %s)',
                       (order_id, item['product']['id'], item['quantity'], item['product']['price']))
        session.pop('cart', None)
        flash('Đặt hàng thành công! Chúng tôi sẽ liên hệ bạn sớm.', 'success')
        return redirect(url_for('index'))
    return render_template('checkout.html', products=products, total=total, item_count=item_count, form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if not current_user.is_authenticated or not getattr(current_user, 'is_admin', False):
        flash('Đăng ký tài khoản chỉ dành cho quản trị viên.', 'warning')
        return redirect(url_for('login'))
    form = RegisterForm()
    if form.validate_on_submit():
        existing = query_db('SELECT * FROM users WHERE email = %s', [form.email.data], one=True)
        if existing:
            flash('Email đã được đăng ký.', 'warning')
        else:
            password_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            execute_db('INSERT INTO users (name, email, password_hash, is_admin) VALUES (%s, %s, %s, %s)',
                       (form.name.data, form.email.data, password_hash, 0))
            flash('Tạo tài khoản thành viên thành công.', 'success')
            return redirect(url_for('admin_users'))
    return render_template('admin_user_form.html', form=form, action='Tạo tài khoản thành viên')

@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        flash('Bạn không có quyền truy cập.', 'danger')
        return redirect(url_for('index'))
    users = query_db('SELECT id, name, email, is_admin FROM users ORDER BY id DESC')
    return render_template('admin_users.html', users=users)

@app.route('/admin/user/add', methods=['GET', 'POST'])
@login_required
def admin_add_user():
    if not current_user.is_admin:
        flash('Bạn không có quyền truy cập.', 'danger')
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        existing = query_db('SELECT * FROM users WHERE email = %s', [form.email.data], one=True)
        if existing:
            flash('Email đã được đăng ký.', 'warning')
        else:
            password_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            execute_db('INSERT INTO users (name, email, password_hash, is_admin) VALUES (%s, %s, %s, %s)',
                       (form.name.data, form.email.data, password_hash, 0))
            flash('Tạo tài khoản thành viên thành công.', 'success')
            return redirect(url_for('admin_users'))
    return render_template('admin_user_form.html', form=form, action='Tạo tài khoản thành viên')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        row = query_db('SELECT id, name, email, password_hash, is_admin FROM users WHERE email = %s', [form.email.data], one=True)
        if row and bcrypt.check_password_hash(row['password_hash'], form.password.data):
            user = User(row['id'], row['name'], row['email'], row['password_hash'], row['is_admin'])
            login_user(user)
            flash('Đăng nhập thành công.', 'success')
            return redirect(url_for('index'))
        flash('Email hoặc mật khẩu không đúng.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('Bạn đã đăng xuất.', 'info')
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Bạn không có quyền truy cập.', 'danger')
        return redirect(url_for('index'))
    products = query_db('SELECT * FROM products ORDER BY id DESC')
    orders = query_db('SELECT * FROM orders ORDER BY created_at DESC LIMIT 10')
    return render_template('admin.html', products=products, orders=orders)

@app.route('/admin/customers')
@login_required
def admin_customers():
    if not current_user.is_admin:
        flash('Bạn không có quyền truy cập.', 'danger')
        return redirect(url_for('index'))
    customers = query_db(
        'SELECT phone, MAX(fullname) AS fullname, MAX(email) AS email, COUNT(DISTINCT orders.id) AS order_count, '
        'SUM(order_items.quantity) AS total_items, SUM(orders.total_amount) AS total_spent '
        'FROM orders JOIN order_items ON order_items.order_id = orders.id '
        'GROUP BY phone ORDER BY total_spent DESC')
    return render_template('admin_customers.html', customers=customers)

@app.route('/admin/customer/<phone>')
@login_required
def admin_customer_detail(phone):
    if not current_user.is_admin:
        flash('Bạn không có quyền truy cập.', 'danger')
        return redirect(url_for('index'))
    customer = query_db(
        'SELECT orders.phone, MAX(orders.fullname) AS fullname, MAX(orders.email) AS email, '
        'COUNT(DISTINCT orders.id) AS order_count, SUM(order_items.quantity) AS total_items, SUM(orders.total_amount) AS total_spent '
        'FROM orders JOIN order_items ON order_items.order_id = orders.id '
        'WHERE orders.phone = %s GROUP BY orders.phone', [phone], one=True)
    orders = query_db('SELECT id, fullname, email, phone, address, total_amount, created_at FROM orders WHERE phone = %s ORDER BY created_at DESC', [phone])
    for order in orders:
        order_id = order['id']
        items = query_db('SELECT products.name, order_items.quantity, order_items.unit_price FROM order_items JOIN products ON products.id = order_items.product_id WHERE order_items.order_id = %s', [order_id])
        order['items'] = items
    return render_template('admin_customer_detail.html', customer=customer, orders=orders)

@app.route('/admin/orders')
@login_required
def admin_orders():
    if not current_user.is_admin:
        flash('Bạn không có quyền truy cập.', 'danger')
        return redirect(url_for('index'))
    orders = query_db(
        'SELECT orders.id, orders.fullname, orders.email, orders.phone, orders.address, orders.total_amount, orders.created_at, '
        'SUM(order_items.quantity) AS total_items '
        'FROM orders JOIN order_items ON order_items.order_id = orders.id '
        'GROUP BY orders.id ORDER BY orders.created_at DESC')
    return render_template('admin_orders.html', orders=orders)

@app.route('/admin/product/add', methods=['GET', 'POST'])
@login_required
def admin_add_product():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    form = ProductForm()
    if form.validate_on_submit():
        execute_db('INSERT INTO products (name, price, stock, category, description, image, is_featured) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                   (form.name.data, float(form.price.data), int(form.stock.data), form.category.data, form.description.data, form.image.data, int(form.is_featured.data)))
        flash('Thêm sản phẩm mới thành công.', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_product_form.html', form=form, action='Thêm sản phẩm mới')

@app.route('/admin/product/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_product(product_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    product = query_db('SELECT * FROM products WHERE id = %s', [product_id], one=True)
    if not product:
        flash('Sản phẩm không tồn tại.', 'danger')
        return redirect(url_for('admin_dashboard'))
    if request.method == 'GET':
        form = ProductForm(data=product)
    else:
        form = ProductForm()
    if form.validate_on_submit():
        execute_db('UPDATE products SET name=%s, price=%s, stock=%s, category=%s, description=%s, image=%s, is_featured=%s WHERE id=%s',
                   (form.name.data, float(form.price.data), int(form.stock.data), form.category.data, form.description.data, form.image.data, int(form.is_featured.data), product_id))
        flash('Cập nhật sản phẩm thành công.', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_product_form.html', form=form, action='Chỉnh sửa sản phẩm')

@app.route('/admin/product/delete/<int:product_id>')
@login_required
def admin_delete_product(product_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    execute_db('DELETE FROM products WHERE id = %s', [product_id])
    execute_db('DELETE FROM reviews WHERE product_id = %s', [product_id])
    flash('Đã xóa sản phẩm.', 'info')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)