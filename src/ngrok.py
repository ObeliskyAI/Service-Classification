from pyngrok import ngrok, conf
import time

PORT = 8080
NGROK_AUTH_TOKEN = "36VzJHJwDq1xlWI1txjCpwklQea_7XGMVAKUz8MhSHk7s11Np"


# Use the existing ngrok installation
conf.get_default().ngrok_path = r"C:\ngrok\ngrok.exe"

# Set authentication token
ngrok.set_auth_token(NGROK_AUTH_TOKEN)

# Start tunnel
tunnel = ngrok.connect(8080)

print("ngrok URL:", tunnel.public_url)
print("API base URL:", tunnel.public_url)

try:
    input("Press Enter to stop ngrok...")
finally:
    ngrok.kill()