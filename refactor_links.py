import os
import re

def update_links(filepath):
    if not os.path.exists(filepath): return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Public links
    content = content.replace('href="index.html"', 'href="{{ url_for(\'index\') }}"')
    content = content.replace('href="about.html"', 'href="{{ url_for(\'about\') }}"')
    content = content.replace('href="contact.html"', 'href="{{ url_for(\'contact\') }}"')
    content = content.replace('href="login.html"', 'href="{{ url_for(\'login\') }}"')
    content = content.replace('href="forgot-password.html"', 'href="{{ url_for(\'forgot_password\') }}"')
    content = content.replace('href="thank-you.html"', 'href="{{ url_for(\'thank_you\') }}"')

    # Admin links
    content = content.replace('href="admin_dashboard.html"', 'href="{{ url_for(\'admin_dashboard\') }}"')
    content = content.replace('href="Admin-profile.html"', 'href="{{ url_for(\'admin_profile\') }}"')
    content = content.replace('href="face_registration.html"', 'href="{{ url_for(\'face_registration\') }}"')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        print(f"Updated links in {filepath}")

# Update components
update_links('templates/components/navbar.html')
update_links('templates/components/footer.html')
update_links('templates/components/admin_sidebar.html')
