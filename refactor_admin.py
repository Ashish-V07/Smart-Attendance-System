import os

admin_files = ['admin_dashboard.html', 'Admin-profile.html', 'face_registration.html']

sidebar_placeholder = '<!-- SIDEBAR PLACEHOLDER -->\n\t<div id="sidebar-placeholder"></div>\n\t<!-- END SIDEBAR PLACEHOLDER -->'
header_placeholder = '<!-- HEADER PLACEHOLDER -->\n\t<div id="header-placeholder"></div>\n\t<!-- END HEADER PLACEHOLDER -->'

js_script = '''
	<!-- Load Components -->
	<script>
		document.addEventListener("DOMContentLoaded", function() {
			fetch('components/admin_sidebar.html')
				.then(response => response.text())
				.then(data => {
					document.getElementById('sidebar-placeholder').innerHTML = data;
					
					// Re-initialize sidebar logic here since it's loaded dynamically
					const currentUrl = window.location.pathname.split('/').pop();
					const menuItems = document.querySelectorAll('#adminSidebarMenu li a');
					menuItems.forEach(item => {
						const itemUrl = item.getAttribute('href');
						if (itemUrl === currentUrl || (currentUrl === '' && itemUrl === 'admin_dashboard.html')) {
							item.parentElement.classList.add('active');
						} else {
							item.parentElement.classList.remove('active');
						}
					});
				});

			fetch('components/admin_header.html')
				.then(response => response.text())
				.then(data => {
					document.getElementById('header-placeholder').innerHTML = data;
					
					// Re-attach mobile toggle event listener
					setTimeout(() => {
						const mobileToggle = document.getElementById('mobile-toggle');
						if(mobileToggle) {
							mobileToggle.addEventListener('click', function(){
								document.getElementById('sidebar-placeholder').classList.toggle('active');
								// Wait, the sidebar itself needs the active class. 
								const sidebarObj = document.getElementById('sidebar');
								if(sidebarObj) sidebarObj.classList.toggle('active');
							});
						}
					}, 100);
				});
		});
	</script>
</body>'''

for file in admin_files:
    if not os.path.exists(file): continue
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace sidebar
    start_idx = content.find('<!-- Sidebar -->\n\t<aside class="sidebar" id="sidebar">')
    if start_idx == -1:
        start_idx = content.find('\t<!-- Sidebar -->\n\t<aside class="sidebar" id="sidebar">')
    
    end_idx = content.find('</aside>')
    if start_idx != -1 and end_idx != -1:
        end_idx += len('</aside>')
        content = content[:start_idx] + sidebar_placeholder + content[end_idx:]
    
    # Replace header
    start_idx = content.find('<!-- Top Header -->\n\t\t<header class="top-header">')
    if start_idx == -1:
        start_idx = content.find('\t\t<!-- Top Header -->\n\t\t<header class="top-header">')
        
    end_idx = content.find('</header>')
    if start_idx != -1 and end_idx != -1:
        end_idx += len('</header>')
        content = content[:start_idx] + header_placeholder + content[end_idx:]
        
    # Replace body script
    if '<!-- Load Components -->' not in content:
        content = content.replace('</body>', js_script)
        
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
        print(f'Processed {file}')
