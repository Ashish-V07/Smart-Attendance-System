import os
import glob
import re

template_dir = 'templates'
html_files = glob.glob(os.path.join(template_dir, '*.html'))
# Also components
html_files.extend(glob.glob(os.path.join(template_dir, 'components', '*.html')))

for file in html_files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace href="assets/..."
    content = re.sub(
        r'href="assets/(.*?)"',
        r'href="{{ url_for(\'static\', filename=\'\1\') }}"',
        content
    )

    # Replace src="assets/..."
    content = re.sub(
        r'src="assets/(.*?)"',
        r'src="{{ url_for(\'static\', filename=\'\1\') }}"',
        content
    )
    
    # Replace background-image: url(assets/...)
    content = re.sub(
        r'url\(assets/(.*?)\)',
        r'url({{ url_for(\'static\', filename=\'\1\') }})',
        content
    )

    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
        print(f'Fixed asset paths in {file}')
