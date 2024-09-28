import os
import logging
from yookassa import Configuration, Payment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_yoomoney_connection():
    YOOMONEY_SHOP_ID = os.environ.get('YOOMONEY_SHOP_ID')
    YOOMONEY_SECRET_KEY = os.environ.get('YOOMONEY_SECRET_KEY')

    logger.info(f"Testing YooMoney connection with Shop ID: {YOOMONEY_SHOP_ID[:5]}...{YOOMONEY_SHOP_ID[-5:] if YOOMONEY_SHOP_ID else 'Not set'}")

    Configuration.account_id = YOOMONEY_SHOP_ID
    Configuration.secret_key = YOOMONEY_SECRET_KEY

    try:
        # Attempt to create a minimal payment to test the connection
        payment = Payment.create({
            "amount": {
                "value": "1.00",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://www.example.com/return_url"
            },
            "capture": True,
            "description": "Test payment"
        })

        logger.info(f"Successfully created test payment with ID: {payment.id}")
        logger.info(f"Payment status: {payment.status}")
        logger.info(f"Confirmation URL: {payment.confirmation.confirmation_url}")
        return True
    except Exception as e:
        logger.error(f"Failed to create test payment: {str(e)}")
        return False

if __name__ == "__main__":
    if test_yoomoney_connection():
        print("YooMoney API connection test passed successfully.")
    else:
        print("YooMoney API connection test failed. Please check your credentials and try again.")
