import requests


def checkout():
    URL = "https://a.khalti.com/api/v2/epayment/initiate/"

    payload = {
        "return_url": "http://127.0.0.1:8000/",
        "website_url": "http://127.0.0.1:8000/",
        "amount": 1200,
        "purchase_order_id": 111112222,
        "purchase_order_name": "test",
        "customer_info": {
            "name": "Unish",
            "email": "i@gmail.com",
            "phone": "9811496763",
        },
    }
    headers = {"Authorization": "Key 8eb5e556328c47f2a2a4a7c9b3511b32"}
    try:
        response = requests.post(URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        print(data)
    except requests.RequestException as e:
        print(f"Request to Khalti API failed: {e}")


checkout()
