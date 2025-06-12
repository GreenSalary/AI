import requests

url = "https://greensalary-api.onrender.com/api/image"
file_path = "test.jpg"

with open(file_path, "rb") as f:
    files = {"image": ("test.jpg", f, "image/jpeg")}
    response = requests.post(url, files=files)

print("Status code:", response.status_code)
print("Response body:", response.text)
