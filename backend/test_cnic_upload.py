import requests

# Token jo tumhe mila tha
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo1LCJzZXNzaW9uX2lkIjoiMDc2NjE3NzYtMTkyMi00YjhkLTgwYTktMDI5OGE3YmYxZjA4IiwiZXhwIjoxNzcwNTg3NDI2LCJpYXQiOjE3NzA1ODY1MjYsInR5cGUiOiJ2ZXJpZmljYXRpb24ifQ.XFiJQ047dxw9PckbwOGfRymztCjpgW-WEfym65TQ-Ag"

session_id = "07661776-1922-4b8d-80a9-0298a7bf1f08"

# Dummy files banao (testing ke liye)
with open("test_front.jpg", "wb") as f:
    f.write(b"fake image data front")
    
with open("test_back.jpg", "wb") as f:
    f.write(b"fake image data back")

# Upload karo
files = {
    'cnic_front': open('test_front.jpg', 'rb'),
    'cnic_back': open('test_back.jpg', 'rb')
}

data = {
    'session_id': session_id
}

response = requests.post(
    'http://process.env.NEXT_PUBLIC_API_URL/api/chat/submit-cnic',
    files=files,
    data=data
)

print("Status:", response.status_code)
print("Response:", response.json())