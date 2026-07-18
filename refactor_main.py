import os

main_files = ['about.html', 'contact.html', 'login.html', 'forgot-password.html', 'thank-you.html']
admin_files = ['admin_dashboard.html', 'Admin-profile.html', 'face_registration.html']

navbar_placeholder = '<!-- NAVBAR PLACEHOLDER -->\n\t<div id="navbar-placeholder"></div>\n\t<!-- END NAVBAR PLACEHOLDER -->'
footer_placeholder = '<!-- FOOTER PLACEHOLDER -->\n\t<div id="footer-placeholder"></div>\n\t<!-- END FOOTER PLACEHOLDER -->'

js_script = '''
	<!-- Load Components -->
	<script>
		document.addEventListener("DOMContentLoaded", function() {
			fetch('components/navbar.html')
				.then(response => response.text())
				.then(data => {
					document.getElementById('navbar-placeholder').innerHTML = data;
				});

			fetch('components/footer.html')
				.then(response => response.text())
				.then(data => {
					document.getElementById('footer-placeholder').innerHTML = data;
				});
		});
	</script>
</body>'''

for file in main_files:
    if not os.path.exists(file): continue
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    start_idx = content.find('<!-- START NAVBAR -->')
    end_idx = content.find('<!-- END NAVBAR -->')
    if start_idx != -1 and end_idx != -1:
        end_idx += len('<!-- END NAVBAR -->')
        content = content[:start_idx] + navbar_placeholder + content[end_idx:]
    
    start_idx = content.find('<!-- START FOOTER -->')
    end_idx = content.find('<!-- END FOOTER COPYRIGHT -->')
    if start_idx != -1 and end_idx != -1:
        end_idx += len('<!-- END FOOTER COPYRIGHT -->')
        content = content[:start_idx] + footer_placeholder + content[end_idx:]
        
    if '<!-- Load Components -->' not in content:
        content = content.replace('</body>', js_script)
        
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
        print(f'Processed {file}')
