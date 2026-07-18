import os
import glob
import re

template_dir = 'templates'
html_files = glob.glob(os.path.join(template_dir, '*.html'))
html_files.extend(glob.glob(os.path.join(template_dir, 'components', '*.html')))

for file in html_files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove the backslashes inserted by the previous script
    # e.g., {{ url_for(\'static\', filename=\'...\') }}
    # -> {{ url_for('static', filename='...') }}
    
    content = content.replace("\\'", "'")

    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
        print(f'Fixed syntax in {file}')
