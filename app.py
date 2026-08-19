import os
import io
import pandas as pd
import pymysql
import math
from flask import Flask, render_template, request, redirect, url_for, session, flash, g, send_file
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange
from wtforms import StringField, PasswordField, SubmitField, DecimalField, IntegerField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange
from datetime import date

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
login_manager.login_message = 'Vui lòng đăng nhập để sử dụng tính năng này.'
login_manager.login_message_category = 'warning'
class User(UserMixin):
    def __init__(self, id, name, email, is_admin, role):
        self.id = id
        self.name = name
        self.email = email
        self.is_admin = is_admin
        self.role = role

    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    user = query_db('SELECT id, name, email, is_admin, role FROM users WHERE id = %s', [user_id], one=True)
    if user:
        return User(user['id'], user['name'], user['email'], user['is_admin'], user['role'])
    return None

class RegistrationForm(FlaskForm):
    name = StringField('Họ và tên', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mật khẩu', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Xác nhận mật khẩu', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Đăng ký')
class AdminAddUserForm(FlaskForm):
    role = SelectField('Vị trí công tác', choices=[('Nhân viên', 'Nhân viên bán hàng'), ('Admin', 'Quản trị viên')])
    name = StringField('Họ và tên', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mật khẩu', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Thêm nhân sự')
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mật khẩu', validators=[DataRequired()])
    submit = SubmitField('Đăng nhập')

class ProductForm(FlaskForm):
    name = StringField('Tên sản phẩm', validators=[DataRequired(), Length(min=3, max=100)])
    price = DecimalField('Giá (đ)', validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField('Số lượng', validators=[DataRequired(), NumberRange(min=0)])
    category = StringField('Danh mục', validators=[DataRequired(), Length(min=2, max=50)])
    description = TextAreaField('Mô tả', validators=[DataRequired(), Length(min=5, max=500)])
    image = StringField('Ảnh (URL)', validators=[DataRequired(), Length(min=5, max=500)])
    is_featured = BooleanField('Nổi bật')
    submit = SubmitField('Lưu')

class CheckoutForm(FlaskForm):
    fullname = StringField('Họ tên', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('SĐT', validators=[DataRequired(), Length(min=9, max=15)])
    address = TextAreaField('Địa chỉ', validators=[Length(max=200)])
    submit = SubmitField('Đặt hàng')

class ReviewForm(FlaskForm):
    name = StringField('Tên', validators=[DataRequired(), Length(min=2, max=50)])
    comment = TextAreaField('Đánh giá', validators=[DataRequired(), Length(min=3, max=300)])
    rating = IntegerField('Sao', validators=[DataRequired(), NumberRange(min=1, max=5)])
    submit = SubmitField('Gửi')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = pymysql.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB, cursorclass=pymysql.cursors.DictCursor, autocommit=True)
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

def execute_db(query, args=(), lastrowid=False):
    db = get_db()
    query = query.replace('?', '%s')
    with db.cursor() as cur:
        cur.execute(query, args)
        rowid = cur.lastrowid if lastrowid else None
    return rowid

@app.context_processor
def inject_globals():
    
    categories = query_db('SELECT DISTINCT category FROM products WHERE is_active = 1')
    ...
    
    # 1. Khởi tạo biến
    cart_quantity = 0
    wishlist_count = 0
    
    if current_user.is_authenticated:
        # 2. ĐẾM GIỎ HÀNG TỪ DATABASE (KHÔNG DÙNG SESSION NỮA)
        cart_res = query_db('SELECT SUM(quantity) as total FROM cart WHERE user_id = %s', [current_user.id], one=True)
        if cart_res and cart_res['total']:
            cart_quantity = cart_res['total']
            
        # 3. Đếm Yêu thích
        res = query_db('SELECT COUNT(*) as cnt FROM wishlist WHERE user_id = %s', [current_user.id], one=True)
        if res: wishlist_count = res['cnt']
        
    return {
        'categories': [row['category'] for row in categories] if categories else [], 
        'cart_quantity': cart_quantity,
        'wishlist_count': wishlist_count
    }

# ==========================================
# CÁC ROUTE KHÁCH HÀNG & MUA SẮM
# ==========================================
@app.route('/')
def index():
    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    page = request.args.get('page', 1, type=int) 
    per_page = 10 
    
    # LUÔN PHẢI CÓ ĐIỀU KIỆN is_active = 1 CHO KHÁCH HÀNG
    where_clause = "is_active = 1"
    params = []
    
    if search:
        where_clause += " AND (name LIKE %s OR category LIKE %s)"
        params = [f'%{search}%', f'%{search}%']
    elif category and category != 'Tất cả':
        where_clause += " AND category = %s"
        params = [category]
        
    total_products = query_db(f'SELECT COUNT(id) as cnt FROM products WHERE {where_clause}', params, one=True)['cnt']
    total_pages = math.ceil(total_products / per_page) if total_products > 0 else 1
    offset = (page - 1) * per_page
    
    query = f'SELECT * FROM products WHERE {where_clause} ORDER BY is_featured DESC, id DESC LIMIT %s OFFSET %s'
    products = query_db(query, params + [per_page, offset])
    
    featured = query_db('SELECT * FROM products WHERE is_featured = 1 AND is_active = 1 LIMIT 4')
    
    categories_data = query_db('SELECT DISTINCT category FROM products WHERE category IS NOT NULL AND is_active = 1')
    categories = [row['category'] for row in categories_data]
    
    return render_template('index.html', products=products, featured=featured, search=search, category=category, page=page, total_pages=total_pages, categories=categories)

@app.route('/product/<int:product_id>', methods=['GET', 'POST'])
def product_detail(product_id):
    # Lấy thông tin sản phẩm hiện tại
    product = query_db('SELECT * FROM products WHERE id = %s AND is_active = 1', [product_id], one=True)
    if not product: return redirect(url_for('index'))
    
    # Kiểm tra xem user đã đánh giá sản phẩm này chưa
    user_has_reviewed = False
    if current_user.is_authenticated:
        reviewed = query_db('SELECT id FROM reviews WHERE product_id = %s AND name = %s', [product_id, current_user.name], one=True)
        if reviewed:
            user_has_reviewed = True

    form = ReviewForm()
    if form.validate_on_submit():
        if user_has_reviewed:
            flash('Bạn đã đánh giá sản phẩm này rồi!', 'danger')
        else:
            execute_db('INSERT INTO reviews (product_id, name, comment, rating) VALUES (%s, %s, %s, %s)', 
                       (product_id, form.name.data, form.comment.data, form.rating.data))
            flash('Cảm ơn bạn đã đánh giá!', 'success')
        return redirect(url_for('product_detail', product_id=product_id))
        
    reviews = query_db('SELECT * FROM reviews WHERE product_id = %s ORDER BY created_at DESC', [product_id])
    
    avg_rating_row = query_db('SELECT AVG(rating) as avg_rating, COUNT(id) as total_reviews FROM reviews WHERE product_id = %s', [product_id], one=True)
    avg_rating = round(avg_rating_row['avg_rating'], 1) if avg_rating_row['avg_rating'] else 0
    total_reviews = avg_rating_row['total_reviews']
    
    # ==========================================
    # LẤY 4 SẢN PHẨM LIÊN QUAN (Cùng danh mục, ngẫu nhiên)
    # ==========================================
    related_products = query_db(
        'SELECT * FROM products WHERE category = %s AND id != %s AND is_active = 1 ORDER BY RAND() LIMIT 4',
        [product['category'], product_id]
    )
    
    return render_template('product.html', product=product, form=form, reviews=reviews, 
                         avg_rating=avg_rating, total_reviews=total_reviews, 
                         user_has_reviewed=user_has_reviewed, related_products=related_products)

@app.route('/add-to-cart/<int:product_id>', methods=['POST', 'GET'])
@login_required
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    
    product = query_db('SELECT stock, name FROM products WHERE id = %s', [product_id], one=True)
    if not product or product['stock'] < quantity:
        flash('Sản phẩm đã hết hàng hoặc không đủ số lượng!', 'error')
        return redirect(request.referrer or url_for('index'))

    existing_item = query_db('SELECT id, quantity FROM cart WHERE user_id = %s AND product_id = %s', 
                             [current_user.id, product_id], one=True)
    
    if existing_item:
        new_quantity = existing_item['quantity'] + quantity
        if new_quantity > product['stock']:
            flash(f'Không thể thêm! Bạn chỉ có thể mua tối đa {product["stock"]} sản phẩm này.', 'error')
        else:
            # DÙNG execute_db thay cho query_db
            execute_db('UPDATE cart SET quantity = %s WHERE id = %s', (new_quantity, existing_item['id']))
            flash(f'Đã cập nhật số lượng {product["name"]} trong giỏ hàng.', 'success')
    else:
        # DÙNG execute_db thay cho query_db
        execute_db('INSERT INTO cart (user_id, product_id, quantity) VALUES (%s, %s, %s)', 
                 (current_user.id, product_id, quantity))
        flash(f'Đã thêm {product["name"]} vào giỏ hàng.', 'success')
        
    return redirect(request.referrer or url_for('index'))

@app.route('/cart')
@login_required
def cart():
    # Khách hàng/Admin đều vào được giỏ hàng
    
    # 1. Truy vấn lấy danh sách sản phẩm trong giỏ của user đang đăng nhập
    # Dùng LEFT JOIN hoặc JOIN để lấy thông tin từ bảng products
    cart_items = query_db('''
        SELECT c.id, c.quantity, p.id as product_id, p.name, p.price, p.image, p.stock
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = %s
    ''', [current_user.id])
    
    # Lấy tổng số lượng trên icon
    total_qty_query = query_db('SELECT SUM(quantity) as total FROM cart WHERE user_id = %s', [current_user.id], one=True)
    cart_quantity = total_qty_query['total'] if total_qty_query['total'] else 0

    return render_template('cart.html', cart_items=cart_items, cart_quantity=cart_quantity)
@app.route('/update-cart/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    quantity = int(request.form.get('quantity', 1))
    if quantity < 1:
        quantity = 1 # Vá lỗi người dùng nhập số 0
        
    item = query_db('''
        SELECT c.id, c.product_id, p.stock 
        FROM cart c JOIN products p ON c.product_id = p.id 
        WHERE c.id = %s AND c.user_id = %s
    ''', [item_id, current_user.id], one=True)

    if item:
        if quantity > item['stock']:
            flash(f'Chỉ còn {item["stock"]} sản phẩm trong kho!', 'error')
        else:
            execute_db('UPDATE cart SET quantity = %s WHERE id = %s', (quantity, item_id))

    return redirect(url_for('cart'))

@app.route('/admin/order/<int:order_id>/update', methods=['POST'])
@login_required
def update_order_status(order_id):
    
    if not current_user.is_admin and current_user.role != 'Nhân viên':
        return redirect(url_for('index'))

    new_status = request.form.get('status')
    
    order = query_db('SELECT status FROM orders WHERE id = %s', [order_id], one=True)
    if not order:
        flash('Không tìm thấy đơn hàng!', 'error')
        return redirect(url_for('admin_orders'))
        
    old_status = order['status']

    # ==========================================
    # CHỐT CHẶN BẢO MẬT: Nếu đơn cũ ĐÃ HỦY thì chặn đứng
    # ==========================================
    if old_status == 'Đã hủy':
        flash('Đơn hàng này đã bị hủy và bị khóa, không thể thay đổi trạng thái!', 'error')
        return redirect(url_for('admin_orders'))

    # Cập nhật trạng thái mới vào database
    execute_db('UPDATE orders SET status = %s WHERE id = %s', (new_status, order_id))

    # Xử lý cộng trả lại kho nếu chuyển sang Đã hủy
    if new_status == 'Đã hủy' and old_status != 'Đã hủy':
        order_items = query_db('SELECT product_id, quantity FROM order_items WHERE order_id = %s', [order_id])
        for item in order_items:
            # Cộng trả lại số lượng vào kho cho từng sản phẩm (dùng execute_db thay cho query_db)
            execute_db('UPDATE products SET stock = stock + %s WHERE id = %s', 
                       (item['quantity'], item['product_id']))
                     
        flash('Đã cập nhật HỦY ĐƠN. Số lượng sản phẩm đã được tự động hoàn trả vào kho!', 'success')
    else:
        flash(f'Đã cập nhật trạng thái đơn hàng thành "{new_status}"!', 'success')

    return redirect(url_for('admin_orders'))
@app.route('/remove-from-cart/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    
    execute_db('DELETE FROM cart WHERE id = %s AND user_id = %s', (item_id, current_user.id))
    flash('Đã xóa sản phẩm khỏi giỏ hàng.', 'success')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    cart_items = query_db('''
        SELECT c.*, p.price, p.stock, p.name 
        FROM cart c 
        JOIN products p ON c.product_id = p.id 
        WHERE c.user_id = %s
    ''', [current_user.id])
    
    if not cart_items:
        flash('Giỏ hàng của bạn đang trống!', 'error')
        return redirect(url_for('cart'))
        
    total_amount = 0
    for item in cart_items:
        if item['quantity'] > item['stock']:
            flash(f'Lỗi: Sản phẩm "{item["name"]}" hiện chỉ còn {item["stock"]} cái. Vui lòng giảm số lượng!', 'error')
            return redirect(url_for('cart'))
        total_amount += item['quantity'] * item['price']
        
    # ==========================================
    # XỬ LÝ LOGIC MÃ GIẢM GIÁ (VOUCHER)
    # ==========================================
    voucher_code = request.form.get('voucher_code', '').strip()
    discount_applied = 0
    voucher_id = None
    
    if voucher_code:
        # 1. Kiểm tra xem mã có tồn tại trong DB không
        voucher = query_db('SELECT * FROM vouchers WHERE code = %s', [voucher_code], one=True)
        
        if not voucher:
            flash('Mã giảm giá không tồn tại!', 'error')
            return redirect(url_for('cart'))
            
        # 2. Kiểm tra hạn sử dụng (So sánh với ngày hiện tại)
        if voucher['expires_at'] < date.today():
            flash('Mã giảm giá đã hết hạn sử dụng!', 'error')
            return redirect(url_for('cart'))
            
        # 3. Kiểm tra số lượng lượt dùng còn lại
        if voucher['usage_limit'] <= 0:
            flash('Mã giảm giá đã hết lượt sử dụng!', 'error')
            return redirect(url_for('cart'))
            
        # 4. Kiểm tra điều kiện giá trị đơn hàng tối thiểu
        if total_amount < voucher['min_order_amount']:
            formatted_min = '{:,.0f}'.format(voucher['min_order_amount'])
            flash(f'Đơn hàng tối thiểu phải từ {formatted_min} đ mới được áp dụng mã này!', 'error')
            return redirect(url_for('cart'))
            
        # Nếu thỏa mãn hết -> Tính toán tiền giảm
        discount_applied = float(voucher['discount_amount'])
        voucher_id = voucher['id']
        
    # Tổng tiền thực tế sau khi trừ voucher (Không để âm tiền)
    final_amount = max(0, total_amount - discount_applied)
    
    payment_method = request.form.get('payment_method', 'COD')
    address = request.form.get('address')
    phone = request.form.get('phone')
    
    # Lưu đơn hàng với tổng tiền đã trừ voucher (Sử dụng get_db() từ hệ thống có sẵn[cite: 1, 2])
    cursor = get_db().cursor()
    cursor.execute('''
        INSERT INTO orders (user_id, total_amount, payment_method, address, phone, status, created_at) 
        VALUES (%s, %s, %s, %s, %s, 'Chờ thanh toán', NOW())
    ''', [current_user.id, final_amount, payment_method, address, phone])
    order_id = cursor.lastrowid
    get_db().commit()
    
    for item in cart_items:
        # Lưu chi tiết đơn hàng[cite: 1, 2]
        execute_db('INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (%s, %s, %s, %s)', 
                 (order_id, item['product_id'], item['quantity'], item['price']))
        
        # Trừ kho sản phẩm[cite: 1, 2]
        execute_db('UPDATE products SET stock = stock - %s WHERE id = %s', 
                 (item['quantity'], item['product_id']))
                 
    # 5. TRỪ ĐI 1 LƯỢT SỬ DỤNG CỦA VOUCHER TRONG DB NẾU ĐÃ DÙNG THÀNH CÔNG
    if voucher_id:
        execute_db('UPDATE vouchers SET usage_limit = usage_limit - 1 WHERE id = %s', [voucher_id])
        
    # Xóa giỏ hàng sau khi đặt xong[cite: 1, 2]
    execute_db('DELETE FROM cart WHERE user_id = %s', (current_user.id,))
    
    flash('Đặt hàng thành công với mã giảm giá! Cảm ơn bạn đã mua sắm.', 'success')
    return redirect(url_for('my_orders'))
# Route mới để hiển thị QR
@app.route('/payment-info/<int:order_id>')
@login_required
def payment_info(order_id):
    order = query_db('SELECT * FROM orders WHERE id = %s', [order_id], one=True)
    return render_template('payment_info.html', order=order)

@app.route('/confirm-payment/<int:order_id>', methods=['POST'])
@login_required
def confirm_payment(order_id):
    # Đảm bảo đơn hàng thuộc về user hiện tại
    order = query_db('SELECT user_id FROM orders WHERE id = %s', [order_id], one=True)
    if order and order['user_id'] == current_user.id:
        execute_db('UPDATE orders SET status = %s WHERE id = %s', ('Chờ xác nhận', order_id))
        flash('Đã xác nhận chuyển khoản! Shop sẽ kiểm tra và xác nhận đơn hàng sớm nhất.', 'success')
    return redirect(url_for('my_orders'))

@app.route('/my-orders')
@login_required
def my_orders():
    page = request.args.get('page', 1, type=int)
    selected_date = request.args.get('date', '').strip()
    per_page = 5  
    
    where_clause = "user_id = %s"
    params = [current_user.id]
    
    if selected_date:
        where_clause += " AND DATE(created_at) = %s"
        params.append(selected_date)
        
    total_orders = query_db(f'SELECT COUNT(id) as cnt FROM orders WHERE {where_clause}', params, one=True)['cnt']
    total_pages = math.ceil(total_orders / per_page) if total_orders > 0 else 1
    offset = (page - 1) * per_page
    
    orders = query_db(f'SELECT * FROM orders WHERE {where_clause} ORDER BY created_at DESC LIMIT %s OFFSET %s', params + [per_page, offset])
    
    for order in orders:
        items = query_db(
            'SELECT order_items.product_id, products.name, products.image, order_items.quantity, order_items.unit_price '
            'FROM order_items JOIN products ON products.id = order_items.product_id WHERE order_items.order_id = %s', 
            [order['id']]
        )
        
        # Kiểm tra xem user hiện tại đã đánh giá sản phẩm này chưa
        for item in items:
            reviewed = query_db('SELECT id FROM reviews WHERE product_id = %s AND name = %s', [item['product_id'], current_user.name], one=True)
            item['has_reviewed'] = True if reviewed else False
            
        order['order_items'] = items
        
    return render_template('my_orders.html', orders=orders, page=page, total_pages=total_pages, selected_date=selected_date)
# ==========================================
# AUTH
# ==========================================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = query_db('SELECT * FROM users WHERE email = %s', [form.email.data], one=True)
        if existing_user:
            flash('Email này đã được sử dụng!', 'danger')
            return redirect(url_for('register'))
            
        hashed_password = generate_password_hash(form.password.data)
        
        
        execute_db(
            'INSERT INTO users (name, email, password, is_admin, role) VALUES (%s, %s, %s, %s, %s)',
            (form.name.data, form.email.data, hashed_password, 0, 'Khách hàng')
        )
        flash('Đăng ký thành công! Hãy đăng nhập.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = query_db('SELECT * FROM users WHERE email = %s', [form.email.data], one=True)
        
        
        if user and (user['password'] == form.password.data or check_password_hash(user['password'], form.password.data)):
            user_obj = User(user['id'], user['name'], user['email'], user['is_admin'], user['role'])
            login_user(user_obj)
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Email hoặc mật khẩu không chính xác!', 'danger')
            
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/wishlist')
@login_required
def wishlist():
    products = query_db('SELECT p.* FROM products p JOIN wishlist w ON p.id = w.product_id WHERE w.user_id = %s ORDER BY w.created_at DESC', [current_user.id])
    return render_template('wishlist.html', products=products)

@app.route('/wishlist/toggle/<int:product_id>', methods=['POST'])
@login_required
def toggle_wishlist(product_id):
    exists = query_db('SELECT * FROM wishlist WHERE user_id = %s AND product_id = %s', [current_user.id, product_id], one=True)
    if exists:
        execute_db('DELETE FROM wishlist WHERE user_id = %s AND product_id = %s', (current_user.id, product_id))
        flash('Đã gỡ khỏi danh sách yêu thích.', 'info')
    else:
        execute_db('INSERT INTO wishlist (user_id, product_id) VALUES (%s, %s)', (current_user.id, product_id))
        flash('Đã lưu vào danh sách yêu thích!', 'success')
    return redirect(request.referrer or url_for('index'))


# QUẢN TRỊ (ADMIN)

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin and current_user.role != 'Nhân viên': 
        return redirect(url_for('index'))
    
    from datetime import date
    current_month = request.args.get('month_num', date.today().strftime('%m'))
    current_year = request.args.get('year_num', date.today().strftime('%Y'))
    
    monthly_stats = query_db("SELECT COUNT(id) as total_completed, SUM(total_amount) as total_revenue FROM orders WHERE YEAR(created_at) = %s AND MONTH(created_at) = %s AND status = 'Hoàn thành'", [current_year, current_month], one=True)
    total_monthly_orders = query_db("SELECT COUNT(id) as total_all FROM orders WHERE YEAR(created_at) = %s AND MONTH(created_at) = %s", [current_year, current_month], one=True)
    
    monthly_revenue = monthly_stats['total_revenue'] if monthly_stats and monthly_stats['total_revenue'] else 0
    monthly_orders_count = monthly_stats['total_completed'] if monthly_stats and monthly_stats['total_completed'] else 0
    total_all = total_monthly_orders['total_all'] if total_monthly_orders and total_monthly_orders['total_all'] else 0
    
    efficiency_rate = (monthly_orders_count / total_all) * 100 if total_all > 0 else 0
    
    products = query_db('SELECT * FROM products ORDER BY id DESC')
    # GIỚI HẠN CHỈ LẤY 6 ĐƠN MỚI NHẤT
    orders = query_db('SELECT * FROM orders ORDER BY created_at DESC LIMIT 6') 
    low_stock = query_db('SELECT * FROM products WHERE stock <= 5 ORDER BY stock ASC')
    
    return render_template('admin.html', products=products, orders=orders, low_stock=low_stock, monthly_revenue=monthly_revenue, monthly_orders_count=monthly_orders_count, efficiency_rate=efficiency_rate, current_month=current_month, current_year=current_year)

@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
def admin_users():
    
    if not current_user.is_admin or current_user.is_admin != 1:
        flash('Bạn không có quyền truy cập trang này!', 'danger')
        return redirect(url_for('index'))
        
    form = AdminAddUserForm()
    if form.validate_on_submit():
        existing_user = query_db('SELECT * FROM users WHERE email = %s', [form.email.data], one=True)
        if existing_user:
            flash('Email này đã tồn tại trong hệ thống!', 'danger')
            return redirect(url_for('admin_users'))
            
        hashed_password = generate_password_hash(form.password.data)
        role = form.role.data # 'Nhân viên' hoặc 'Admin'
        is_admin = 1 if role == 'Admin' else 0
        
        execute_db(
            'INSERT INTO users (name, email, password, is_admin, role) VALUES (%s, %s, %s, %s, %s)',
            (form.name.data, form.email.data, hashed_password, is_admin, role)
        )
        flash(f'Đã thêm tài khoản {role} thành công!', 'success')
        return redirect(url_for('admin_users'))
        
    users = query_db('SELECT * FROM users ORDER BY id DESC')
    return render_template('admin_users.html', form=form, users=users)
@app.route('/admin/customers')
@login_required
def admin_customers():
    if not current_user.is_admin: return redirect(url_for('index'))
    customers = query_db('SELECT phone, MAX(fullname) AS fullname, MAX(email) AS email, COUNT(DISTINCT orders.id) AS order_count, SUM(order_items.quantity) AS total_items, SUM(orders.total_amount) AS total_spent FROM orders JOIN order_items ON order_items.order_id = orders.id GROUP BY phone ORDER BY total_spent DESC')
    return render_template('admin_customers.html', customers=customers)

@app.route('/admin/customer/<phone>')
@login_required
def admin_customer_detail(phone):
    if not current_user.is_admin: return redirect(url_for('index'))
    customer = query_db('SELECT orders.phone, MAX(orders.fullname) AS fullname, MAX(orders.email) AS email, COUNT(DISTINCT orders.id) AS order_count, SUM(order_items.quantity) AS total_items, SUM(orders.total_amount) AS total_spent FROM orders JOIN order_items ON order_items.order_id = orders.id WHERE orders.phone = %s GROUP BY orders.phone', [phone], one=True)
    orders = query_db('SELECT id, fullname, email, phone, address, total_amount, created_at, status FROM orders WHERE phone = %s ORDER BY created_at DESC', [phone])
    for order in orders:
        order['order_details'] = query_db('SELECT products.name, order_items.quantity, order_items.unit_price FROM order_items JOIN products ON products.id = order_items.product_id WHERE order_items.order_id = %s', [order['id']])
    return render_template('admin_customer_detail.html', customer=customer, orders=orders)

# QUẢN LÝ ĐƠN HÀNG (Lọc theo ngày + Phân trang 10 dòng)
@app.route('/admin/orders')
@login_required
def admin_orders():
    if not current_user.is_admin and current_user.role != 'Nhân viên': 
        return redirect(url_for('index'))
        
    page = request.args.get('page', 1, type=int)
    
    
    from datetime import date
    default_today = date.today().strftime('%Y-%m-%d')
    
    
    selected_date = request.args.get('date', default_today)
    per_page = 10
    
    where_clause = "1=1"
    params = []
    
    if selected_date:
        where_clause = "DATE(created_at) = %s"
        params.append(selected_date)
        
    total_orders = query_db(f'SELECT COUNT(id) as cnt FROM orders WHERE {where_clause}', params, one=True)['cnt']
    total_pages = math.ceil(total_orders / per_page)
    offset = (page - 1) * per_page
    
    orders = query_db(f'SELECT * FROM orders WHERE {where_clause} ORDER BY created_at DESC LIMIT %s OFFSET %s', params + [per_page, offset])
    
    orders_data = []
    for o in orders:
        item_cnt = query_db('SELECT SUM(quantity) as total_qty FROM order_items WHERE order_id = %s', [o['id']], one=True)['total_qty'] or 0
        orders_data.append({'order': o, 'item_count': item_cnt})

    return render_template('admin_orders.html', orders_data=orders_data, page=page, total_pages=total_pages, selected_date=selected_date)


@app.route('/admin/products')
@login_required
def admin_products():
    if not current_user.is_admin: return redirect(url_for('index'))
    return render_template('admin_products.html', products=query_db('SELECT * FROM products ORDER BY id DESC'))

@app.route('/admin/product/add', methods=['GET', 'POST'])
@login_required
def admin_add_product():
    if not current_user.is_admin: return redirect(url_for('index'))
    form = ProductForm()
    if form.validate_on_submit():
        execute_db('INSERT INTO products (name, price, stock, category, description, image, is_featured) VALUES (%s, %s, %s, %s, %s, %s, %s)', (form.name.data, float(form.price.data), int(form.stock.data), form.category.data, form.description.data, form.image.data, int(form.is_featured.data)))
        flash('Thêm sản phẩm thành công.', 'success')
        return redirect(url_for('admin_products'))
    return render_template('admin_product_form.html', form=form, action='Thêm Sản Phẩm')

@app.route('/admin/product/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_product(product_id):
    if not current_user.is_admin: return redirect(url_for('index'))
    product = query_db('SELECT * FROM products WHERE id = %s', [product_id], one=True)
    form = ProductForm(data=product) if request.method == 'GET' else ProductForm()
    if form.validate_on_submit():
        execute_db('UPDATE products SET name=%s, price=%s, stock=%s, category=%s, description=%s, image=%s, is_featured=%s WHERE id=%s', (form.name.data, float(form.price.data), int(form.stock.data), form.category.data, form.description.data, form.image.data, int(form.is_featured.data), product_id))
        flash('Cập nhật thành công.', 'success')
        return redirect(url_for('admin_products'))
    return render_template('admin_product_form.html', form=form, action='Chỉnh Sửa Sản Phẩm')
@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_user(user_id):
    if not current_user.is_admin or current_user.is_admin != 1:
        flash('Bạn không có quyền truy cập!', 'danger')
        return redirect(url_for('index'))
        
    user = query_db('SELECT * FROM users WHERE id = %s', [user_id], one=True)
    if not user:
        flash('Không tìm thấy tài khoản!', 'danger')
        return redirect(url_for('admin_users'))
        
    
    if user['role'] == 'Khách hàng':
        flash('Không được phép chỉnh sửa tài khoản khách hàng!', 'danger')
        return redirect(url_for('admin_users'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        role = request.form.get('role')
        new_password = request.form.get('password')
        is_admin = 1 if role == 'Admin' else 0
        
        if new_password:
            hashed_pw = generate_password_hash(new_password)
            execute_db('UPDATE users SET name = %s, role = %s, is_admin = %s, password = %s WHERE id = %s', 
                       (name, role, is_admin, hashed_pw, user_id))
        else:
            execute_db('UPDATE users SET name = %s, role = %s, is_admin = %s WHERE id = %s', 
                       (name, role, is_admin, user_id))
                       
        flash('Cập nhật tài khoản thành công!', 'success')
        return redirect(url_for('admin_users'))
        
    return render_template('admin_edit_user.html', user=user)
@app.route('/admin/product/delete/<int:product_id>')
@login_required
def admin_delete_product(product_id):
    if not current_user.is_admin: return redirect(url_for('index'))
    
    
    execute_db('UPDATE products SET is_active = 0 WHERE id = %s', [product_id])
    
    flash('Đã ẩn sản phẩm thành công (Bảo toàn lịch sử đơn hàng cũ).', 'success')
    return redirect(url_for('admin_products'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = query_db('SELECT * FROM users WHERE id = %s', [current_user.id], one=True)
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_info':
            name = request.form.get('name')
            execute_db('UPDATE users SET name = %s WHERE id = %s', (name, current_user.id))
            flash('Cập nhật thông tin cá nhân thành công!', 'success')
            return redirect(url_for('profile'))
            
        elif action == 'change_password':
            old_password = request.form.get('old_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            is_old_correct = (user['password'] == old_password) or check_password_hash(user['password'], old_password)
            
            if not is_old_correct:
                flash('Mật khẩu hiện tại không chính xác!', 'danger')
            elif new_password != confirm_password:
                flash('Mật khẩu mới và xác nhận mật khẩu không khớp!', 'danger')
            elif len(new_password) < 6:
                flash('Mật khẩu mới phải có ít nhất 6 ký tự!', 'danger')
            else:
                hashed_pw = generate_password_hash(new_password)
                execute_db('UPDATE users SET password = %s WHERE id = %s', (hashed_pw, current_user.id))
                flash('Đổi mật khẩu thành công!', 'success')
            return redirect(url_for('profile'))
            
    return render_template('profile.html', user=user)
@app.route('/admin/transactions')
@login_required
def admin_transactions():
    if not current_user.is_admin and current_user.role != 'Nhân viên': 
        return redirect(url_for('index'))
        
    page = request.args.get('page', 1, type=int)
    
    # Lấy ngày hôm nay theo chuẩn YYYY-MM-DD làm mặc định
    from datetime import date
    default_today = date.today().strftime('%Y-%m-%d')
    
    selected_date = request.args.get('date', default_today)
    per_page = 10
    
    where_clause = "status = 'Hoàn thành'"
    params = []
    
    if selected_date:
        where_clause += " AND DATE(created_at) = %s"
        params.append(selected_date)
        
    summary_query = f"""
        SELECT COUNT(o.id) as total_orders, SUM(o.total_amount) as total_revenue,
               (SELECT SUM(oi.quantity) FROM order_items oi JOIN orders ord ON oi.order_id = ord.id WHERE ord.status = 'Hoàn thành' {" AND DATE(ord.created_at) = %s" if selected_date else ""}) as total_products
        FROM orders o WHERE {where_clause}
    """
    summary_params = [selected_date] * 2 if selected_date else []
    summary = query_db(summary_query, summary_params, one=True)
    
    total_revenue = summary['total_revenue'] if summary and summary['total_revenue'] else 0
    total_orders_count = summary['total_orders'] if summary and summary['total_orders'] else 0
    total_products_sold = summary['total_products'] if summary and summary['total_products'] else 0

    total_tx = query_db(f'SELECT COUNT(id) as cnt FROM orders WHERE {where_clause}', params, one=True)['cnt']
    total_pages = math.ceil(total_tx / per_page)
    offset = (page - 1) * per_page
    
    transactions = query_db(f'SELECT * FROM orders WHERE {where_clause} ORDER BY created_at DESC LIMIT %s OFFSET %s', params + [per_page, offset])
    
    return render_template('admin_transactions.html', 
                           transactions=transactions, 
                           page=page, 
                           total_pages=total_pages, 
                           selected_date=selected_date,
                           total_revenue=total_revenue,
                           total_orders_count=total_orders_count,
                           total_products_sold=total_products_sold)
@app.route('/cancel-order/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    
    order = query_db('SELECT status FROM orders WHERE id = %s AND user_id = %s', [order_id, current_user.id], one=True)
    
    if not order:
        flash('Không tìm thấy đơn hàng hoặc bạn không có quyền hủy đơn này!', 'error')
        return redirect(url_for('my_orders'))
        
    
    if order['status'] not in ['Chờ thanh toán', 'Chờ xác nhận']:
        flash('Đơn hàng đã được xử lý hoặc đang giao, không thể tự hủy. Vui lòng liên hệ Hotline!', 'error')
        return redirect(url_for('my_orders'))
        
    
    query_db('UPDATE orders SET status = %s WHERE id = %s', ['Đã hủy', order_id])
    
    
    order_items = query_db('SELECT product_id, quantity FROM order_items WHERE order_id = %s', [order_id])
    for item in order_items:
        query_db('UPDATE products SET stock = stock + %s WHERE id = %s', 
                 [item['quantity'], item['product_id']])
                 
    flash('Bạn đã hủy đơn hàng thành công!', 'success')
    return redirect(url_for('my_orders'))
@app.route('/admin/export/excel')
@login_required
def export_excel():
    if not current_user.is_admin: return redirect(url_for('index'))
    orders = query_db('SELECT id, fullname, phone, total_amount, status, created_at FROM orders ORDER BY created_at DESC')
    df = pd.DataFrame(orders)
    df.columns = ['Mã Đơn', 'Khách hàng', 'SĐT', 'Tổng Tiền (đ)', 'Trạng thái', 'Ngày Đặt']
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer: df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name='DoanhThu.xlsx')

@app.route('/admin/export/pdf')
@login_required
def export_pdf():
    if not current_user.is_admin: return redirect(url_for('index'))
    return render_template('admin_print_report.html', orders=query_db('SELECT * FROM orders ORDER BY created_at DESC'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)