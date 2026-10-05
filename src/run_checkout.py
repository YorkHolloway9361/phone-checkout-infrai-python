from phone_checkout import InfraiClient, checkout


if __name__ == "__main__":
    client = InfraiClient()
    result = checkout("+15551234567", "order-1001", 49.90, client)
    print(result)
