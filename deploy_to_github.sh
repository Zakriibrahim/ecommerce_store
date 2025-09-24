#!/bin/bash

# Script to deploy Party Yacout to GitHub
echo "🚀 Deploying Party Yacout to GitHub..."

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
fi

# Add all files to git
git add .

# Commit changes
git commit -m "🎉 Party Yacout v2.0 - Complete ecommerce store with multilingual support, user accounts, admin panel, and shopping cart

New Features:
- Multilingual support (English, French, Arabic)
- User registration and authentication
- Shopping cart functionality
- Admin panel for product management
- Search with suggestions
- Responsive design for all devices
- Moroccan currency (MAD) support
- Free shipping over 500 MAD
- Order history and user profiles
- Secure payment methods

Technical Improvements:
- SQLite database integration
- Flask-Login for authentication
- Flask-WTF for forms
- Flask-Babel for internationalization
- Bootstrap 5 responsive design
- JavaScript enhancements"

# Add GitHub remote (replace with your actual GitHub URL)
echo "📦 Pushing to GitHub..."
git remote add origin https://github.com/Zakriibrahim/ecommerce_store.git
git branch -M main
git push -u origin main

echo "✅ Deployment completed! Visit your GitHub repository to see the updates."
echo "🔗 GitHub Repository: https://github.com/Zakriibrahim/ecommerce_store"
