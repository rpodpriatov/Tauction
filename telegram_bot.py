import os
import logging
import requests
from telegram import Update, LabeledPrice
from telegram.ext import (Application, CommandHandler, PreCheckoutQueryHandler,
                          MessageHandler, filters)
from telegram.error import BadRequest
from models import User, Auction
from db import db_session
from datetime import datetime

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

# YooMoney API Configuration
YOOMONEY_SHOP_ID = os.environ.get('YOOMONEY_SHOP_ID')
YOOMONEY_SECRET_KEY = os.environ.get('YOOMONEY_SECRET_KEY')
YOOMONEY_SHOP_ARTICLE_ID = os.environ.get('YOOMONEY_SHOP_ARTICLE_ID')
YOOMONEY_API_URL = 'https://api.yookassa.ru/v3/payments'

application = None  # Глобальная переменная для бота

async def start(update: Update, context):
    logger.info(f"User {update.effective_user.id} started the bot")
    await update.message.reply_text(
        'Welcome to the Auction Platform Bot! Use /buy_stars to purchase XTR stars.'
    )

async def buy_stars(update: Update, context):
    logger.info(
        f"buy_stars function called by user {update.effective_user.id}")
    try:
        chat_id = update.effective_chat.id
        title = "XTR Stars Purchase"
        description = "Purchase XTR stars for use in auctions"
        payload = "Custom-Payload"
        provider_token = os.environ.get('PAYMENT_PROVIDER_TOKEN')
        logger.info(
            f"PAYMENT_PROVIDER_TOKEN: {'Set' if provider_token else 'Not set'}"
        )
        if not provider_token:
            logger.error("PAYMENT_PROVIDER_TOKEN is not set")
            await update.message.reply_text(
                "Sorry, star purchases are not available at the moment.")
            return
        currency = "RUB"  # Обычно валюта указывается как "RUB" или другая валюта, а не "XTR"
        price = 1000  # Цена в копейках (10.00 RUB)
        prices = [LabeledPrice("XTR Stars", price)]

        logger.info(f"Sending invoice to user {update.effective_user.id}")
        await context.bot.send_invoice(chat_id, title, description, payload,
                                       provider_token, currency, prices)
        logger.info(f"Invoice sent to user {update.effective_user.id}")
    except Exception as e:
        logger.error(f"Error in buy_stars function: {str(e)}")
        await update.message.reply_text(
            "Sorry, there was an error processing your request. Please try again later."
        )

async def buy_stars_yoomoney(update: Update, context):
    logger.info(f"buy_stars_yoomoney function called by user {update.effective_user.id}")
    try:
        # Check if all required environment variables are set
        if not all([YOOMONEY_SHOP_ID, YOOMONEY_SECRET_KEY, YOOMONEY_SHOP_ARTICLE_ID]):
            missing_vars = [var for var in ['YOOMONEY_SHOP_ID', 'YOOMONEY_SECRET_KEY', 'YOOMONEY_SHOP_ARTICLE_ID'] if not os.environ.get(var)]
            logger.error(f"YooMoney configuration is incomplete. Missing variables: {', '.join(missing_vars)}")
            await update.message.reply_text("Sorry, YooMoney payments are not available at the moment. Please try again later or contact support.")
            return

        user_id = update.effective_user.id
        user = db_session.query(User).filter_by(telegram_id=str(user_id)).first()
        if not user:
            logger.info(f"Creating new user for Telegram ID: {user_id}")
            user = User(telegram_id=str(user_id),
                        username=update.effective_user.username,
                        xtr_balance=0)
            db_session.add(user)
            db_session.commit()
            logger.info(f"Created new user: {user.id}")

        # Set a minimum purchase amount (e.g., 10 XTR)
        min_amount = 10
        amount = context.args[0] if context.args else str(min_amount)
        try:
            amount = int(amount)
            if amount < min_amount:
                logger.warning(f"User {user_id} attempted to purchase less than the minimum amount")
                await update.message.reply_text(f"Minimum purchase amount is {min_amount} XTR. Please try again with a larger amount.")
                return
        except ValueError:
            logger.warning(f"User {user_id} provided an invalid amount: {amount}")
            await update.message.reply_text("Please provide a valid number of XTR to purchase. For example: /buy_stars_yoomoney 15")
            return

        total_amount = amount * 10  # 1 XTR = 10 RUB

        payment = {
            "amount": {
                "value": f"{total_amount:.2f}",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": f"{os.getenv('BASE_URL', 'https://your-domain.com')}/yoomoney_success"
            },
            "capture": True,
            "description": f"Purchase of {amount} XTR stars for user {user.id}",
            "metadata": {
                "user_id": user.id,
                "amount": amount
            },
            "receipt": {
                "customer": {
                    "full_name": update.effective_user.full_name,
                    "phone": "",  # You might want to ask for the user's phone number separately
                    "email": ""  # You might want to ask for the user's email separately
                },
                "items": [
                    {
                        "description": "XTR Stars",
                        "quantity": "1",
                        "amount": {
                            "value": f"{total_amount:.2f}",
                            "currency": "RUB"
                        },
                        "vat_code": "1",
                        "payment_mode": "full_prepayment",
                        "payment_subject": "service"
                    }
                ]
            },
            "merchant_customer_id": str(user.id),
            "save_payment_method": False
        }

        if YOOMONEY_SHOP_ARTICLE_ID:
            payment["merchant_article_id"] = YOOMONEY_SHOP_ARTICLE_ID

        auth = (YOOMONEY_SHOP_ID, YOOMONEY_SECRET_KEY)
        headers = {
            "Content-Type": "application/json",
            "Idempotence-Key": str(datetime.now().timestamp())
        }

        logger.info(f"Sending payment request to YooMoney for user {user.id}")
        logger.debug(f"YooMoney API request payload: {payment}")
        try:
            response = requests.post(YOOMONEY_API_URL,
                                     json=payment,
                                     headers=headers,
                                     auth=auth,
                                     timeout=10)  # Add a timeout to the request
            response.raise_for_status()  # Raise an exception for non-200 status codes
        except requests.exceptions.RequestException as e:
            logger.error(f"Error in YooMoney API request: {str(e)}")
            logger.error(f"YooMoney API response: {response.text if response else 'No response'}")
            if response:
                logger.error(f"YooMoney API status code: {response.status_code}")
                logger.error(f"YooMoney API headers: {response.headers}")
            await update.message.reply_text("There was an error processing your payment request. Please try again later or contact support.")
            return

        payment_info = response.json()
        logger.debug(f"YooMoney API response: {payment_info}")
        confirmation_url = payment_info.get('confirmation', {}).get('confirmation_url')
        if confirmation_url:
            logger.info(f"YooMoney payment created for user {user.id}: {confirmation_url}")
            await update.message.reply_text(
                f"Please complete your payment of {amount} XTR ({total_amount} RUB) by clicking the link below:\n{confirmation_url}"
            )
        else:
            logger.error(f"Failed to create YooMoney payment: {response.text}")
            error_code = payment_info.get('code')
            error_description = payment_info.get('description', 'Unknown error')
            logger.error(f"YooMoney error: {error_code} - {error_description}")
            await update.message.reply_text(
                f"Sorry, there was an error processing your payment (Error: {error_code}). Please try again later or contact support."
            )
    except Exception as e:
        logger.error(f"Unexpected error in buy_stars_yoomoney function: {str(e)}", exc_info=True)
        await update.message.reply_text(
            "An unexpected error occurred. Please try again later or contact support."
        )

async def pre_checkout_callback(update: Update, context):
    query = update.pre_checkout_query
    if query.invoice_payload != "Custom-Payload":
        await query.answer(ok=False, error_message="Something went wrong...")
    else:
        await query.answer(ok=True)

async def successful_payment_callback(update: Update, context):
    user_id = update.effective_user.id
    amount = update.message.successful_payment.total_amount // 100  # Convert cents to rubles

    user = db_session.query(User).filter_by(telegram_id=str(user_id)).first()
    if user:
        user.xtr_balance += amount
        db_session.commit()
        await update.message.reply_text(
            f'Thank you for your payment! {amount} XTR stars have been added to your balance.'
        )
    else:
        new_user = User(telegram_id=str(user_id),
                        username=update.effective_user.username,
                        xtr_balance=amount)
        db_session.add(new_user)
        db_session.commit()
        await update.message.reply_text(
            f'Thank you for your payment! A new account has been created for you with {amount} XTR stars.'
        )

def setup_bot() -> Application:
    global application
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        logger.error(
            "TELEGRAM_BOT_TOKEN is not set in the environment variables")
        raise ValueError(
            "TELEGRAM_BOT_TOKEN is not set in the environment variables")

    logger.info(
        f"Setting up bot with token: {bot_token[:5]}...{bot_token[-5:]}")

    application = Application.builder().token(bot_token).build()

    logger.info("Adding command handlers")
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('buy_stars', buy_stars))
    application.add_handler(CommandHandler('buy_stars_yoomoney', buy_stars_yoomoney))
    application.add_handler(PreCheckoutQueryHandler(pre_checkout_callback))
    application.add_handler(
        MessageHandler(filters.SUCCESSFUL_PAYMENT,
                       successful_payment_callback))

    logger.info("Bot setup completed")
    return application

async def send_notification(user_id: int, message: str):
    if application:
        try:
            await application.bot.send_message(chat_id=int(user_id),
                                               text=message)
            logger.info(f"Notification sent to user {user_id}")
        except BadRequest as e:
            logger.error(
                f"BadRequest when sending notification to user {user_id}: {str(e)}"
            )
        except Exception as e:
            logger.error(
                f"Error sending notification to user {user_id}: {str(e)}")
    else:
        logger.error("Telegram application is not initialized.")
