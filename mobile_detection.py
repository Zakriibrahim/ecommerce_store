#!/usr/bin/env python3
# Mobile detection patch for app.py

# Read the current app.py
with open('app.py', 'r') as f:
    content = f.read()

# Add mobile detection function at the top (after imports)
mobile_detection_code = '''

def is_mobile_request():
    """Detect if the request is from a mobile device"""
    user_agent = request.headers.get('User-Agent', '').lower()
    mobile_keywords = ['mobile', 'android', 'iphone', 'ipod', 'ipad', 'blackberry', 'webos']
    return any(keyword in user_agent for keyword in mobile_keywords)

'''

# Find the right place to insert (after imports and before routes)
insert_point = content.find('app.secret_key =')
if insert_point != -1:
    # Find the end of the imports section
    import_end = content.rfind('import translations', insert_point)
    if import_end != -1:
        # Insert after the last import
        insert_pos = content.find('\\n', import_end) + 1
        content = content[:insert_pos] + mobile_detection_code + content[insert_pos:]

# Update the home route to use mobile template
content = content.replace(
    '@app.route(\'/\')\\ndef home():',
    '@app.route(\'/\')\\ndef home():\\n    """Home page"""\\n    if is_mobile_request():\\n        products = load_json(PRODUCTS_DB)\\n        featured_products = products[:4]\\n        categories = list(set(p[\'category\'] for p in products))\\n        return render_template(\'index_mobile.html\', featured_products=featured_products, categories=categories, t=t)\\n    else:\\n        products = load_json(PRODUCTS_DB)\\n        featured_products = products[:4]\\n        return render_template(\'index.html\', featured_products=featured_products, t=t)'
)

# Write the updated content back
with open('app.py', 'w') as f:
    f.write(content)

print("Mobile detection added to app.py")
