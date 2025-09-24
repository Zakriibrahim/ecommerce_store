from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
from datetime import datetime
from functools import wraps

# Import translation system
import translations

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Database files
PRODUCTS_DB = "data/products.json"
USERS_DB = "data/users.json"
ORDERS_DB = "data/orders.json"
WISHLIST_DB = "data/wishlist.json"

def init_database():
    """Initialize database files with sample data"""
    os.makedirs("data", exist_ok=True)
    
    # Sample products
    if not os.path.exists(PRODUCTS_DB):
        products = [
            {
                "id": 1, 
                "name": "Gaming Laptop", 
                "price": 1299.99, 
                "category": "Electronics",
                "image": "💻",
                "description": "High-performance gaming laptop with RTX 4060",
                "stock": 15
            },
            {
                "id": 2, 
                "name": "Wireless Mouse", 
                "price": 49.99, 
                "category": "Electronics",
                "image": "🖱️",
                "description": "Ergonomic wireless mouse with RGB lighting",
                "stock": 50
            },
            {
                "id": 3, 
                "name": "Mechanical Keyboard", 
                "price": 89.99, 
                "category": "Electronics",
                "image": "⌨️",
                "description": "Mechanical keyboard with blue switches",
                "stock": 30
            },
            {
                "id": 4, 
                "name": "Smartphone", 
                "price": 799.99, 
                "category": "Electronics",
                "image": "📱",
                "description": "Latest smartphone with 5G capability",
                "stock": 25
            },
            {
                "id": 5, 
                "name": "Coffee Mug", 
                "price": 14.99, 
                "category": "Home",
                "image": "☕",
                "description": "Ceramic coffee mug with funny design",
                "stock": 100
            },
            {
                "id": 6, 
                "name": "T-Shirt", 
                "price": 24.99, 
                "category": "Clothing",
                "image": "👕",
                "description": "100% cotton t-shirt, various sizes available",
                "stock": 75
            }
        ]
        with open(PRODUCTS_DB, 'w') as f:
            json.dump(products, f, indent=2)
    
    # Initialize other databases
    if not os.path.exists(USERS_DB):
        with open(USERS_DB, 'w') as f:
            json.dump([], f)
    if not os.path.exists(ORDERS_DB):
        with open(ORDERS_DB, 'w') as f:
            json.dump([], f)
    
    # Initialize wishlist database
    if not os.path.exists(WISHLIST_DB):
        with open(WISHLIST_DB, 'w') as f:
            json.dump([], f)
    
    # Create default admin user
    users = load_json(USERS_DB)
    admin_user = next((u for u in users if u.get('is_admin')), None)
    if not admin_user:
        admin_user = {
            'id': 9999,
            'name': 'Administrator',
            'email': 'admin@techshop.com',
            'password': 'admin123',
            'is_admin': True,
            'created_at': datetime.now().isoformat()
        }
        users.append(admin_user)
        save_json(USERS_DB, users)

def get_translations():
    """Get translations for current language"""
    lang = session.get('language', 'auto')
    if lang == 'auto':
        # Detect browser language
        browser_lang = request.accept_languages.best_match(['en', 'fr', 'ar'])
        lang = browser_lang if browser_lang else 'en'
    
    return translations.load_translations(lang)

def t(key):
    """Translation helper function"""
    translations_dict = get_translations()
    return translations_dict.get(key, key)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def load_json(filepath):
    """Load JSON data from file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except:
        return []

def save_json(filepath, data):
    """Save data to JSON file"""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def get_cart_details():
    """Get cart items with totals"""
    cart = session.get('cart', {})
    products = load_json(PRODUCTS_DB)
    
    cart_items = []
    total = 0
    
    for product_id, quantity in cart.items():
        product = next((p for p in products if p['id'] == int(product_id)), None)
        if product:
            item_total = product['price'] * quantity
            total += item_total
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total': item_total
            })
    
    return cart_items, total

def calculate_shipping(total):
    """Calculate shipping fee - 45 MAD if total < 500 MAD, free otherwise"""
    return 45 if total < 500 else 0

def calculate_total_with_shipping(total):
    """Calculate total including shipping"""
    shipping = calculate_shipping(total)
    return total + shipping

# ==================== LANGUAGE & THEME ROUTES ====================
@app.route('/set_language/<lang>')
def set_language(lang):
    """Set user's preferred language"""
    if lang in ['en', 'fr', 'ar', 'auto']:
        session['language'] = lang
    return redirect(request.referrer or url_for('home'))

@app.route('/set_theme/<theme>')
def set_theme(theme):
    """Set user's preferred theme"""
    if theme in ['light', 'dark', 'auto']:
        session['theme'] = theme
    return redirect(request.referrer or url_for('home'))

# ==================== WISHLIST FUNCTIONALITY ====================
@app.route('/wishlist')
@login_required
def wishlist():
    """User wishlist page"""
    wishlists = load_json(WISHLIST_DB)
    user_wishlist = next((w for w in wishlists if w['user_id'] == session['user_id']), None)
    
    if not user_wishlist:
        user_wishlist = {'user_id': session['user_id'], 'items': []}
        wishlists.append(user_wishlist)
        save_json(WISHLIST_DB, wishlists)
    
    products = load_json(PRODUCTS_DB)
    wishlist_items = []
    
    for item in user_wishlist['items']:
        product = next((p for p in products if p['id'] == item['product_id']), None)
        if product:
            wishlist_items.append({
                'product': product,
                'added_date': item['added_date']
            })
    
    return render_template('wishlist.html', wishlist_items=wishlist_items, t=t)

@app.route('/add_to_wishlist/<int:product_id>')
@login_required
def add_to_wishlist(product_id):
    """Add product to wishlist"""
    products = load_json(PRODUCTS_DB)
    product = next((p for p in products if p['id'] == product_id), None)
    
    if not product:
        return jsonify({'success': False, 'message': t('product_not_found')})
    
    wishlists = load_json(WISHLIST_DB)
    user_wishlist = next((w for w in wishlists if w['user_id'] == session['user_id']), None)
    
    if not user_wishlist:
        user_wishlist = {'user_id': session['user_id'], 'items': []}
        wishlists.append(user_wishlist)
    
    # Check if product already in wishlist
    if any(item['product_id'] == product_id for item in user_wishlist['items']):
        return jsonify({'success': False, 'message': t('product_already_in_wishlist')})
    
    # Add product to wishlist
    user_wishlist['items'].append({
        'product_id': product_id,
        'added_date': datetime.now().isoformat()
    })
    
    save_json(WISHLIST_DB, wishlists)
    return jsonify({'success': True, 'message': t('added_to_wishlist')})

@app.route('/remove_from_wishlist/<int:product_id>')
@login_required
def remove_from_wishlist(product_id):
    """Remove product from wishlist"""
    wishlists = load_json(WISHLIST_DB)
    user_wishlist = next((w for w in wishlists if w['user_id'] == session['user_id']), None)
    
    if user_wishlist:
        user_wishlist['items'] = [item for item in user_wishlist['items'] if item['product_id'] != product_id]
        save_json(WISHLIST_DB, wishlists)
    
    return redirect(url_for('wishlist'))

@app.route('/move_to_cart/<int:product_id>')
@login_required
def move_to_cart(product_id):
    """Move product from wishlist to cart"""
    # First remove from wishlist
    wishlists = load_json(WISHLIST_DB)
    user_wishlist = next((w for w in wishlists if w['user_id'] == session['user_id']), None)
    
    if user_wishlist:
        user_wishlist['items'] = [item for item in user_wishlist['items'] if item['product_id'] != product_id]
        save_json(WISHLIST_DB, wishlists)
    
    # Then add to cart
    products = load_json(PRODUCTS_DB)
    product = next((p for p in products if p['id'] == product_id), None)
    
    if product and product['stock'] > 0:
        if 'cart' not in session:
            session['cart'] = {}
        
        cart = session['cart']
        product_key = str(product_id)
        
        if product_key in cart:
            cart[product_key] += 1
        else:
            cart[product_key] = 1
        
        session['cart'] = cart
        session.modified = True
    
    return redirect(url_for('wishlist'))

# ==================== ADMIN AUTHENTICATION ====================
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Check admin credentials
        if email == 'admin@techshop.com' and password == 'admin123':
            session['admin_logged_in'] = True
            session['admin_email'] = email
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin/login.html', error='Invalid admin credentials')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    session.pop('admin_email', None)
    return redirect(url_for('admin_login'))

# ==================== USER AUTHENTICATION ====================
@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email_phone = request.form['email_phone']
        password = request.form['password']
        
        users = load_json(USERS_DB)
        user = next((u for u in users if (u['email'] == email_phone or u.get('phone') == email_phone) and u['password'] == password), None)
        
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            return redirect(request.args.get('next') or url_for('home'))
        else:
            return render_template('login.html', error=t('invalid_credentials'))
    
    return render_template('login.html', t=t)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form.get('phone', '')
        password = request.form['password']
        
        users = load_json(USERS_DB)
        
        # Check if email already exists
        if any(u['email'] == email for u in users):
            return render_template('register.html', error=t('email_already_registered'))
        
        new_user = {
            'id': max([u['id'] for u in users]) + 1 if users else 1,
            'name': name,
            'email': email,
            'phone': phone,
            'password': password,
            'created_at': datetime.now().isoformat()
        }
        
        users.append(new_user)
        save_json(USERS_DB, users)
        
        session['user_id'] = new_user['id']
        session['user_name'] = new_user['name']
        return redirect(url_for('home'))
    
    return render_template('register.html', t=t)

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    return redirect(url_for('home'))

@app.route('/profile')
@login_required
def profile():
    """User profile"""
    users = load_json(USERS_DB)
    user = next((u for u in users if u['id'] == session['user_id']), None)
    orders = load_json(ORDERS_DB)
    user_orders = [o for o in orders if o.get('customer_email') == user['email'] or o.get('customer_phone') == user.get('phone', '')]
    
    return render_template('profile.html', user=user, orders=user_orders, t=t, wishlist_count=wishlist_count)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    users = load_json(USERS_DB)
    user = next((u for u in users if u['id'] == session['user_id']), None)
    
    if request.method == 'POST':
        user['name'] = request.form['name']
        user['email'] = request.form['email']
        user['phone'] = request.form.get('phone', '')
        
        save_json(USERS_DB, users)
        session['user_name'] = user['name']
        return redirect(url_for('profile'))
    
    return render_template('edit_profile.html', user=user, t=t)

# ==================== SEARCH FUNCTIONALITY ====================
@app.route('/search')
def search_products():
    """Search products by name or description"""
    query = request.args.get('q', '').lower().strip()
    
    if not query:
        return redirect(url_for('products'))
    
    products = load_json(PRODUCTS_DB)
    search_results = []
    
    for product in products:
        if (query in product['name'].lower() or 
            query in product['description'].lower() or 
            query in product['category'].lower()):
            search_results.append(product)
    
    return render_template('search_results.html', 
                         products=search_results, 
                         query=query, 
                         results_count=len(search_results),
                         t=t)

# ==================== ORDER TRACKING ====================
@app.route('/track_order', methods=['GET', 'POST'])
def track_order():
    """Order tracking page"""
    if request.method == 'POST':
        order_id = request.form.get('order_id')
        phone = request.form.get('phone')
        
        orders = load_json(ORDERS_DB)
        order = None
        
        # Try to find order by ID and phone
        for o in orders:
            if (str(o['id']) == order_id and 
                o.get('customer_phone') == phone):
                order = o
                break
        
        return render_template('track_order.html', order=order, searched=True, t=t)
    
    return render_template('track_order.html', order=None, searched=False, t=t)

# ==================== REVIEWS & RATINGS ====================
@app.route('/product/<int:product_id>/review', methods=['POST'])
@login_required
def add_review(product_id):
    """Add product review"""
    rating = int(request.json['rating'])
    comment = request.json.get('comment', '')
    
    products = load_json(PRODUCTS_DB)
    product = next((p for p in products if p['id'] == product_id), None)
    
    if not product:
        return jsonify({'success': False, 'message': t('product_not_found')}

@app.route('/my_orders')
@login_required
def my_orders():
    """User orders page"""
    users = load_json(USERS_DB)
    user = next((u for u in users if u['id'] == session['user_id']), None)
    orders = load_json(ORDERS_DB)
    user_orders = [o for o in orders if o.get('customer_email') == user['email'] or o.get('customer_phone') == user.get('phone', '')]
    
    # Get wishlist count for the profile page
    wishlists = load_json(WISHLIST_DB)
    user_wishlist = next((w for w in wishlists if w['user_id'] == session['user_id']), None)
    wishlist_count = len(user_wishlist['items']) if user_wishlist else 0
    
    return render_template('orders.html', orders=user_orders, t=t)

# Update the profile route to include wishlist count
)
    
    if 'reviews' not in product:
        product['reviews'] = []
    
    # Check if user already reviewed
    existing_review = next((r for r in product['reviews'] if r['user_id'] == session['user_id']), None)
    if existing_review:
        existing_review['rating'] = rating
        existing_review['comment'] = comment
        existing_review['date'] = datetime.now().isoformat()
    else:
        product['reviews'].append({
            'user_id': session['user_id'],
            'user_name': session['user_name'],
            'rating': rating,
            'comment': comment,
            'date': datetime.now().isoformat()
        })
    
    save_json(PRODUCTS_DB, products)
    return jsonify({'success': True, 'message': t('review_added')})

# ==================== ADMIN ROUTES ====================
@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    products = load_json(PRODUCTS_DB)
    orders = load_json(ORDERS_DB)
    
    total_products = len(products)
    total_orders = len(orders)
    total_revenue = sum(order['total'] for order in orders)
    
    recent_orders = orders[-5:]  # Last 5 orders
    
    return render_template('admin/dashboard.html',
                         total_products=total_products,
                         total_orders=total_orders,
                         total_revenue=total_revenue,
                         recent_orders=recent_orders)

@app.route('/admin/products')
@admin_required
def admin_products():
    """Admin products management"""
    products = load_json(PRODUCTS_DB)
    categories = list(set(p['category'] for p in products))
    return render_template('admin/products.html', products=products, categories=categories)

@app.route('/admin/products/add', methods=['GET', 'POST'])
@admin_required
def admin_add_product():
    """Add new product"""
    if request.method == 'POST':
        products = load_json(PRODUCTS_DB)
        
        new_product = {
            'id': max([p['id'] for p in products]) + 1 if products else 1,
            'name': request.form['name'],
            'price': float(request.form['price']),
            'category': request.form['category'],
            'image': request.form['image'],
            'description': request.form['description'],
            'stock': int(request.form['stock'])
        }
        
        products.append(new_product)
        save_json(PRODUCTS_DB, products)
        return redirect('/admin/products')
    
    products = load_json(PRODUCTS_DB)
    categories = list(set(p['category'] for p in products))
    return render_template('admin/add_product.html', categories=categories)

@app.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_product(product_id):
    """Edit product"""
    products = load_json(PRODUCTS_DB)
    product = next((p for p in products if p['id'] == product_id), None)
    
    if not product:
        return "Product not found", 404
    
    if request.method == 'POST':
        product['name'] = request.form['name']
        product['price'] = float(request.form['price'])
        product['category'] = request.form['category']
        product['image'] = request.form['image']
        product['description'] = request.form['description']
        product['stock'] = int(request.form['stock'])
        
        save_json(PRODUCTS_DB, products)
        return redirect('/admin/products')
    
    categories = list(set(p['category'] for p in products))
    return render_template('admin/edit_product.html', product=product, categories=categories)

@app.route('/admin/products/delete/<int:product_id>')
@admin_required
def admin_delete_product(product_id):
    """Delete product"""
    products = load_json(PRODUCTS_DB)
    products = [p for p in products if p['id'] != product_id]
    save_json(PRODUCTS_DB, products)
    return redirect('/admin/products')

@app.route('/admin/orders')
@admin_required
def admin_orders():
    """Admin orders management"""
    orders = load_json(ORDERS_DB)
    return render_template('admin/orders.html', orders=orders)

@app.route('/admin/orders/update_status/<int:order_id>', methods=['POST'])
@admin_required
def admin_update_order_status(order_id):
    """Update order status"""
    orders = load_json(ORDERS_DB)
    order = next((o for o in orders if o['id'] == order_id), None)
    
    if order:
        order['status'] = request.json['status']
        save_json(ORDERS_DB, orders)
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': 'Order not found'})

@app.route('/admin/categories')
@admin_required
def admin_categories():
    """Manage categories"""
    products = load_json(PRODUCTS_DB)
    categories = list(set(p['category'] for p in products))
    return render_template('admin/categories.html', categories=categories)

# ==================== CUSTOMER ROUTES ====================
@app.route('/')
def home():
    """Home page"""
    products = load_json(PRODUCTS_DB)
    featured_products = products[:4]
    return render_template('index.html', featured_products=featured_products, t=t)

@app.route('/products')
def products():
    """Products page with filtering"""
    category = request.args.get('category', '')
    products = load_json(PRODUCTS_DB)
    
    if category:
        products = [p for p in products if p['category'].lower() == category.lower()]
    
    categories = list(set(p['category'] for p in load_json(PRODUCTS_DB)))
    return render_template('products.html', products=products, categories=categories, selected_category=category, t=t)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Product detail page"""
    products = load_json(PRODUCTS_DB)
    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        return "Product not found", 404
    return render_template('product_detail.html', product=product, t=t)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    """Add item to cart"""
    product_id = int(request.json['product_id'])
    quantity = int(request.json.get('quantity', 1))
    
    products = load_json(PRODUCTS_DB)
    product = next((p for p in products if p['id'] == product_id), None)
    
    if not product:
        return jsonify({'success': False, 'message': t('product_not_found')})
    
    if product['stock'] < quantity:
        return jsonify({'success': False, 'message': t('not_enough_stock')})
    
    # Initialize cart in session
    if 'cart' not in session:
        session['cart'] = {}
    
    cart = session['cart']
    product_key = str(product_id)
    
    if product_key in cart:
        cart[product_key] += quantity
    else:
        cart[product_key] = quantity
    
    session['cart'] = cart
    session.modified = True
    
    return jsonify({'success': True, 'message': t('added_to_cart'), 'cart_count': sum(cart.values())})

@app.route('/cart')
def view_cart():
    """View shopping cart"""
    cart_items, total = get_cart_details()
    shipping = calculate_shipping(total)
    total_with_shipping = calculate_total_with_shipping(total)
    return render_template('cart.html', 
                         cart_items=cart_items, 
                         total=total,
                         shipping=shipping,
                         total_with_shipping=total_with_shipping,
                         t=t)

@app.route('/update_cart', methods=['POST'])
def update_cart():
    """Update cart quantities"""
    product_id = str(request.json['product_id'])
    quantity = int(request.json['quantity'])
    
    if quantity <= 0:
        if 'cart' in session and product_id in session['cart']:
            del session['cart'][product_id]
    else:
        if 'cart' in session and product_id in session['cart']:
            session['cart'][product_id] = quantity
    
    session.modified = True
    return jsonify({'success': True})

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    """Remove item from cart"""
    if 'cart' in session and str(product_id) in session['cart']:
        del session['cart'][str(product_id)]
        session.modified = True
    
    return redirect(url_for('view_cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """Checkout process"""
    cart_items, total = get_cart_details()
    shipping = calculate_shipping(total)
    total_with_shipping = calculate_total_with_shipping(total)
    
    if request.method == 'POST':
        # Process order with new fields
        full_name = request.form['full_name']
        phone = request.form['phone']
        city = request.form['city']
        address = request.form['address']
        payment_method = "cash_on_delivery"
        
        # Get cart items
        cart = session.get('cart', {})
        products = load_json(PRODUCTS_DB)
        
        order_items = []
        order_total = 0
        
        for product_id, quantity in cart.items():
            product = next((p for p in products if p['id'] == int(product_id)), None)
            if product:
                item_total = product['price'] * quantity
                order_total += item_total
                order_items.append({
                    'product_id': product['id'],
                    'product_name': product['name'],
                    'quantity': quantity,
                    'price': product['price'],
                    'total': item_total
                })
                
                # Update stock
                product['stock'] -= quantity
        
        # Save updated products
        save_json(PRODUCTS_DB, products)
        
        # Create order
        orders = load_json(ORDERS_DB)
        order = {
            'id': len(orders) + 1,
            'customer_name': full_name,
            'customer_phone': phone,
            'customer_city': city,
            'customer_address': address,
            'payment_method': payment_method,
            'user_id': session.get('user_id'),
            'items': order_items,
            'total': order_total,
            'status': 'Processing',
            'order_date': datetime.now().isoformat()
        }
        orders.append(order)
        save_json(ORDERS_DB, orders)
        
        # Clear cart
        session['cart'] = {}
        session.modified = True
        
        return redirect(url_for('thank_you', order_id=order['id']))
    
    # GET request - show checkout form
    if not cart_items:
        return redirect(url_for('home'))
    
    return render_template('checkout.html', 
                         cart_items=cart_items, 
                         total=total,
                         shipping=shipping,
                         total_with_shipping=total_with_shipping,
                         t=t)

@app.route('/thank_you/<int:order_id>')
def thank_you(order_id):
    """Thank you page after successful order"""
    orders = load_json(ORDERS_DB)
    order = next((o for o in orders if o['id'] == order_id), None)
    if not order:
        return "Order not found", 404
    return render_template('thank_you.html', order=order, t=t)

@app.route('/order_confirmation/<int:order_id>')
def order_confirmation(order_id):
    """Order confirmation page"""
    orders = load_json(ORDERS_DB)
    order = next((o for o in orders if o['id'] == order_id), None)
    if not order:
        return "Order not found", 404
    return render_template('order_confirmation.html', order=order, t=t)

@app.route('/api/cart_count')
def cart_count():
    """API endpoint to get cart count"""
    cart = session.get('cart', {})
    return jsonify({'count': sum(cart.values())})

if __name__ == '__main__':
    init_database()
    app.run(debug=True, host='0.0.0.0', port=5000)
