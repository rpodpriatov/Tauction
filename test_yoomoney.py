import os
import requests
from dotenv import load_dotenv
load_dotenv()


YOOMONEY_SHOP_ID = os.getenv('YOOMONEY_SHOP_ID')
YOOMONEY_SECRET_KEY = os.getenv('YOOMONEY_SECRET_KEY')
YOOMONEY_API_URL = 'https://api.yookassa.ru/v3/payments'

payment = {
    "amount": {
        "value": "10.00",
        "currency": "RUB"
    },
    "confirmation": {
        "type": "redirect",
        "return_url": "https://yourdomain.com/yoomoney_success"
    },
    "capture": True,
    "description": "Test Payment",
    "metadata": {
        "user_id": 1,
        "amount": 10
    }
}

headers = {
    "Content-Type": "application/json"
}

auth = (YOOMONEY_SHOP_ID, YOOMONEY_SECRET_KEY)

response = requests.post(YOOMONEY_API_URL, json=payment, headers=headers, auth=auth)

if response.status_code == 201:
    print("Payment created successfully")
    print("Confirmation URL:", response.json()['confirmation']['confirmation_url'])
else:
    print("Failed to create payment")
    print("Response:", response.json())
