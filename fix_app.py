#!/usr/bin/env python3
import re

# Read the current app.py
with open('app.py', 'r') as f:
    content = f.read()

# Fix 1: Replace before_first_request with before_request
content = content.replace('@app.before_first_request', '@app.before_request')
content = content.replace('def create_tables():', 'def initialize_app():')

# Fix 2: Add tables creation check
tables_fix = '''
# Create tables on first request
if not hasattr(app, 'tables_created'):
    db.create_all()
    app.tables_created = True
'''

# Insert the tables fix before the context processor
if '# Context processor to make functions available in all templates' in content:
    content = content.replace(
        '# Context processor to make functions available in all templates',
        tables_fix + '\n# Context processor to make functions available in all templates'
    )

# Fix 3: Update add_to_cart to handle AJAX
old_add_to_cart = '''@app.route('/add_to_cart/<int:product_id>')
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
    return redirect(request.referrer or url_for('index'))'''

new_add_to_cart = '''@app.route('/add_to_cart/<int:product_id>')
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
    
    # Return JSON for AJAX requests, otherwise redirect
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'cart_count': len(cart)})
    else:
        flash(_('Product added to cart!'), 'success')
        return redirect(request.referrer or url_for('index'))'''

content = content.replace(old_add_to_cart, new_add_to_cart)

# Write the fixed content back
with open('app.py', 'w') as f:
    f.write(content)

print("✅ app.py has been fixed successfully!")
