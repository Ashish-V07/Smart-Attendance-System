

from werkzeug.security import generate_password_hash, check_password_hash

hashed_password = generate_password_hash("Ashish@123")
print(hashed_password)

