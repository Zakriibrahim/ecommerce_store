from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, FloatField, IntegerField
from wtforms.validators import DataRequired, Email, Length
from flask_babel import Babel, gettext as _
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///party_yacout.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Babel configuration for multilingual support
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['LANGUAGES'] = {
    'en': 'English',
    'fr': 'Français',
    'ar': 'العربية'
}

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
babel = Babel(app)

@babel.localeselector
def get_locale():
    # Check if language is set in session, otherwise use browser preference
    return session.get('language', request.accept_languages.best_match(app.config['LANGUAGES'].keys()))

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_en = db.Column(db.String(100), nullable=False)
    name_fr = db.Column(db.String(100))
    name_ar = db.Column(db.String(100))
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_en = db.Column(db.String(100), nullable=False)
    name_fr = db.Column(db.String(100))
    name_ar = db.Column(db.String(100))
    description_en = db.Column(db.Text)
    description_fr = db.Column(db.Text)
    description_ar = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    original_price = db.Column(db.Float)
    discount = db.Column(db.Integer)
    image = db.Column(db.String(200))
    stock = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    is_active = db.Column(db.Boolean, default=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    order_number = db.Column(db.String(20), unique=True)
    total_amount = db.Column(db.Float, nullable=False)
    shipping_cost = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='pending')
    shipping_address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    order_items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

# Forms
class LoginForm(FlaskForm):
    email = StringField(_('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_('Password'), validators=[DataRequired()])

class RegisterForm(FlaskForm):
    username = StringField(_('Username'), validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField(_('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_('Password'), validators=[DataRequired(), Length(min=6)])
    first_name = StringField(_('First Name'))
    last_name = StringField(_('Last Name'))

class ProductForm(FlaskForm):
    name_en = StringField(_('Name (English)'), validators=[DataRequired()])
    name_fr = StringField(_('Name (French)'))
    name_ar = StringField(_('Name (Arabic)'))
    description_en = TextAreaField(_('Description (English)'))
    description_fr = TextAreaField(_('Description (French)'))
    description_ar = TextAreaField(_('Description (Arabic)'))
    price = FloatField(_('Price (MAD)'), validators=[DataRequired()])
    original_price = FloatField(_('Original Price (MAD)'))
    discount = IntegerField(_('Discount (%)'))
    image = StringField(_('Image URL'))
    stock = IntegerField(_('Stock'), default=0)
    category_id = SelectField(_('Category'), coerce=int)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Helper functions
def get_cart_total():
    cart = session.get('cart', {})
    total = 0
    for product_id, item in cart.items():
        product = Product.query.get(int(product_id))
        if product:
            total += product.price * item['quantity']
    return total

def get_shipping_cost():
    total = get_cart_total()
    return 0 if total >= 500 else 45

def get_product_name(product):
    locale = get_locale()
    if locale == 'fr' and product.name_fr:
        return product.name_fr
    elif locale == 'ar' and product.name_ar:
        return product.name_ar
    return product.name_en

def get_product_description(product):
    locale = get_locale()
    if locale == 'fr' and product.description_fr:
        return product.description_fr
    elif locale == 'ar' and product.description_ar:
        return product.description_ar
    return product.description_en

# Routes
@app.route('/')
def index():
    featured_products = Product.query.filter_by(is_active=True).limit(4).all()
    return render_template('index.html', featured_products=featured_products)

@app.route('/products')
def products():
    category_id = request.args.get('category_id', type=int)
    search_query = request.args.get('search', '')
    
    query = Product.query.filter_by(is_active=True)
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if search_query:
        query = query.filter(Product.name_en.ilike(f'%{search_query}%') | 
                           Product.name_fr.ilike(f'%{search_query}%') |
                           Product.name_ar.ilike(f'%{search_query}%'))
    
    products = query.all()
    categories = Category.query.all()
    
    return render_template('products.html', products=products, categories=categories, 
                         search_query=search_query, category_id=category_id)

@app.route('/search_suggestions')
def search_suggestions():
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])
    
    products = Product.query.filter(
        (Product.name_en.ilike(f'%{query}%')) | 
        (Product.name_fr.ilike(f'%{query}%')) |
        (Product.name_ar.ilike(f'%{query}%'))
    ).limit(5).all()
    
    suggestions = []
    for product in products:
        suggestions.append({
            'id': product.id,
            'name': get_product_name(product),
            'price': product.price,
            'image': product.image
        })
    
    return jsonify(suggestions)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    cart = session.get('cart', {})
    
    product_key = str(product_id)
    if product_key in cart:
        cart[product_key]['quantity'] += 1
    else:
        cart[product_key] = {
            'quantity': 1,
            'name': get_product_name(product),
            'price': product.price,
            'image': product.image
        }
    
    session['cart'] = cart
    flash(_('Product added to cart!'), 'success')
    return redirect(request.referrer or url_for('index'))

@app.route('/update_cart/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    cart = session.get('cart', {})
    product_key = str(product_id)
    
    if quantity <= 0:
        cart.pop(product_key, None)
    else:
        if product_key in cart:
            cart[product_key]['quantity'] = quantity
    
    session['cart'] = cart
    return redirect(url_for('view_cart'))

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    product_key = str(product_id)
    cart.pop(product_key, None)
    session['cart'] = cart
    flash(_('Product removed from cart'), 'info')
    return redirect(url_for('view_cart'))

@app.route('/cart')
def view_cart():
    cart = session.get('cart', {})
    cart_items = []
    total = 0
    
    for product_id, item in cart.items():
        product = Product.query.get(int(product_id))
        if product:
            item_total = product.price * item['quantity']
            total += item_total
            cart_items.append({
                'product': product,
                'quantity': item['quantity'],
                'item_total': item_total
            })
    
    shipping_cost = 0 if total >= 500 else 45
    grand_total = total + shipping_cost
    
    return render_template('cart.html', cart_items=cart_items, total=total, 
                         shipping_cost=shipping_cost, grand_total=grand_total)

@app.route('/checkout')
def checkout():
    if not session.get('cart'):
        flash(_('Your cart is empty'), 'warning')
        return redirect(url_for('view_cart'))
    
    cart = session.get('cart', {})
    total = get_cart_total()
    shipping_cost = get_shipping_cost()
    grand_total = total + shipping_cost
    
    return render_template('checkout.html', total=total, shipping_cost=shipping_cost, 
                         grand_total=grand_total)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:  # In real app, use password hashing
            login_user(user)
            flash(_('Logged in successfully!'), 'success')
            return redirect(url_for('index'))
        else:
            flash(_('Invalid email or password'), 'error')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,  # In real app, hash this password
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        db.session.add(user)
        db.session.commit()
        flash(_('Account created successfully! Please login.'), 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash(_('Logged out successfully'), 'info')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('profile.html', orders=orders)

@app.route('/change_language/<language>')
def change_language(language):
    if language in app.config['LANGUAGES']:
        session['language'] = language
    return redirect(request.referrer or url_for('index'))

# Admin routes
@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash(_('Access denied'), 'error')
        return redirect(url_for('index'))
    
    products_count = Product.query.count()
    orders_count = Order.query.count()
    users_count = User.query.count()
    
    return render_template('admin/dashboard.html', 
                         products_count=products_count,
                         orders_count=orders_count,
                         users_count=users_count)

@app.route('/admin/products')
@login_required
def admin_products():
    if not current_user.is_admin:
        flash(_('Access denied'), 'error')
        return redirect(url_for('index'))
    
    products = Product.query.all()
    return render_template('admin/products.html', products=products)

@app.route('/admin/product/new', methods=['GET', 'POST'])
@login_required
def admin_add_product():
    if not current_user.is_admin:
        flash(_('Access denied'), 'error')
        return redirect(url_for('index'))
    
    form = ProductForm()
    form.category_id.choices = [(c.id, c.name_en) for c in Category.query.all()]
    
    if form.validate_on_submit():
        product = Product(
            name_en=form.name_en.data,
            name_fr=form.name_fr.data,
            name_ar=form.name_ar.data,
            description_en=form.description_en.data,
            description_fr=form.description_fr.data,
            description_ar=form.description_ar.data,
            price=form.price.data,
            original_price=form.original_price.data,
            discount=form.discount.data,
            image=form.image.data,
            stock=form.stock.data,
            category_id=form.category_id.data
        )
        db.session.add(product)
        db.session.commit()
        flash(_('Product added successfully!'), 'success')
        return redirect(url_for('admin_products'))
    
    return render_template('admin/product_form.html', form=form)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# Initialize database and create admin user
@app.before_first_request
def create_tables():
    db.create_all()
    # Create admin user if not exists
    if not User.query.filter_by(email='admin@partyyacout.com').first():
        admin = User(
            username='admin',
            email='admin@partyyacout.com',
            password='admin123',  # Change this in production!
            first_name='Admin',
            last_name='User',
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
    
    # Create default categories if not exist
    if Category.query.count() == 0:
        categories = [
            {'en': 'Birthday Parties', 'fr': 'Fêtes d\'anniversaire', 'ar': 'حفلات أعياد الميلاد'},
            {'en': 'Wedding Decorations', 'fr': 'Décorations de mariage', 'ar': 'ديكورات الزفاف'},
            {'en': 'Balloons', 'fr': 'Ballons', 'ar': 'البالونات'},
            {'en': 'Tableware', 'fr': 'Articles de table', 'ar': 'أدوات المائدة'}
        ]
        for cat_data in categories:
            category = Category(
                name_en=cat_data['en'],
                name_fr=cat_data['fr'],
                name_ar=cat_data['ar']
            )
            db.session.add(category)
        db.session.commit()

# Context processor to make functions available in all templates
@app.context_processor
def inject_global_variables():
    return dict(
        get_locale=get_locale,
        get_product_name=get_product_name,
        get_product_description=get_product_description,
        get_cart_total=get_cart_total,
        get_shipping_cost=get_shipping_cost,
        cart_count=len(session.get('cart', {}))
    )

if __name__ == '__main__':
    app.run(debug=True)
