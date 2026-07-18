import os
import glob
import re

template_dir = 'templates'
html_files = glob.glob(os.path.join(template_dir, '*.html'))

for file in html_files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace Navbar placeholder
    content = re.sub(
        r'<!-- NAVBAR PLACEHOLDER -->.*?<!-- END NAVBAR PLACEHOLDER -->',
        '{% include "components/navbar.html" %}',
        content,
        flags=re.DOTALL
    )

    # Replace Footer placeholder
    content = re.sub(
        r'<!-- FOOTER PLACEHOLDER -->.*?<!-- END FOOTER PLACEHOLDER -->',
        '{% include "components/footer.html" %}',
        content,
        flags=re.DOTALL
    )

    # Replace Sidebar placeholder
    content = re.sub(
        r'<!-- SIDEBAR PLACEHOLDER -->.*?<!-- END SIDEBAR PLACEHOLDER -->',
        '{% include "components/admin_sidebar.html" %}',
        content,
        flags=re.DOTALL
    )

    # Replace Header placeholder
    content = re.sub(
        r'<!-- HEADER PLACEHOLDER -->.*?<!-- END HEADER PLACEHOLDER -->',
        '{% include "components/admin_header.html" %}',
        content,
        flags=re.DOTALL
    )

    # Remove the fetch script block
    # It starts with <!-- Load Components --> and ends before </body>
    content = re.sub(
        r'<!-- Load Components -->.*?</body>',
        '</body>',
        content,
        flags=re.DOTALL
    )

    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
        print(f'Refactored {file}')
