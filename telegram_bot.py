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
YOOMONEY_API_URL = 'https://api.yookassa.ru/v3/payments'


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
    logger.info(
        f"buy_stars_yoomoney function called by user {update.effective_user.id}"
    )
    try:
        user_id = update.effective_user.id
        user = db_session.query(User).filter_by(
            telegram_id=str(user_id)).first()
        if not user:
            # Создаём пользователя, если его ещё нет
            user = User(telegram_id=str(user_id),
                        username=update.effective_user.username,
                        xtr_balance=0)
            db_session.add(user)
            db_session.commit()

        amount = 10  # Количество XTR, которое пользователь хочет купить
        total_amount = amount * 10  # Примерная цена, можно изменить по необходимости (например, 100 RUB)

        # Создание платежа в YooMoney
        payment = {
            "amount": {
                "value": f"{total_amount}",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url":
                f"{os.getenv('BASE_URL')}/yoomoney_success"  # Замените BASE_URL на ваш домен
            },
            "capture": True,
            "description":
            f"Purchase of {amount} XTR stars for user {user.id}",
            "metadata": {
                "user_id": user.id,
                "amount": amount
            }
        }

        # Использование HTTP Basic Auth
        auth = (YOOMONEY_SHOP_ID, YOOMONEY_SECRET_KEY)

        headers = {"Content-Type": "application/json"}

        response = requests.post(YOOMONEY_API_URL,
                                 json=payment,
                                 headers=headers,
                                 auth=auth)
        if response.status_code == 201:
            payment_info = response.json()
            confirmation_url = payment_info['confirmation']['confirmation_url']
            logger.info(
                f"YooMoney payment created for user {user.id}: {confirmation_url}"
            )
            await update.message.reply_text(
                f"Please complete your payment by clicking the link below:\n{confirmation_url}"
            )
        else:
            logger.error(f"Failed to create YooMoney payment: {response.text}")
            await update.message.reply_text(
                "Sorry, there was an error processing your payment. Please try again later."
            )
    except Exception as e:
        logger.error(f"Error in buy_stars_yoomoney function: {str(e)}")
        await update.message.reply_text(
            "Sorry, there was an error processing your request. Please try again later."
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
    application.add_handler(
        CommandHandler('buy_stars_yoomoney',
                       buy_stars_yoomoney))  # Новая команда
    application.add_handler(PreCheckoutQueryHandler(pre_checkout_callback))
    application.add_handler(
        MessageHandler(filters.SUCCESSFUL_PAYMENT,
                       successful_payment_callback))

    logger.info("Bot setup completed")
    return application


async def send_notification(application: Application, user_id: int,
                            message: str):
    user = db_session.query(User).filter_by(id=user_id).first()
    if user and user.telegram_id:
        try:
            await application.bot.send_message(chat_id=int(user.telegram_id),
                                               text=message)
            logger.info(f"Notification sent to user {user_id}")
        except BadRequest as e:
            logger.error(
                f"BadRequest when sending notification to user {user_id}: {str(e)}"
            )
        except Exception as e:
            logger.error(
                f"Error sending notification to user {user_id}: {str(e)}")
