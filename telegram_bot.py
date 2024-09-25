# telegram_bot.py

import os
import logging
from telegram import Update, LabeledPrice
from telegram.ext import (
    Application, CommandHandler, PreCheckoutQueryHandler,
    MessageHandler, filters
)
from telegram.error import BadRequest
from models import User, Auction
from db import db_session
from datetime import datetime

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context):
    logger.info(f"User {update.effective_user.id} started the bot")
    await update.message.reply_text(
        'Welcome to the Auction Platform Bot! Use /register to create an account and /buy_stars to purchase XTR stars.'
    )

async def register(update: Update, context):
    user_id = update.effective_user.id
    username = update.effective_user.username

    user = db_session.query(User).filter_by(telegram_id=str(user_id)).first()
    if user:
        await update.message.reply_text('You are already registered!')
    else:
        new_user = User(telegram_id=str(user_id), username=username)
        db_session.add(new_user)
        db_session.commit()
        await update.message.reply_text('Registration successful! You can now use the bot features.')

async def buy_stars(update: Update, context):
    logger.info(f"buy_stars function called by user {update.effective_user.id}")
    try:
        chat_id = update.effective_chat.id
        title = "XTR Stars Purchase"
        description = "Purchase XTR stars for use in auctions"
        payload = "Custom-Payload"
        provider_token = os.environ.get('PAYMENT_PROVIDER_TOKEN')
        if not provider_token:
            logger.error("PAYMENT_PROVIDER_TOKEN is not set")
            await update.message.reply_text("Sorry, star purchases are not available at the moment.")
            return
        currency = "USD"  # или "RUB", в зависимости от вашего платежного провайдера
        price = 1000  # Цена в копейках (10 USD)
        prices = [LabeledPrice("XTR Stars", price)]

        await context.bot.send_invoice(
            chat_id=chat_id,
            title=title,
            description=description,
            payload=payload,
            provider_token=provider_token,
            currency=currency,
            prices=prices
        )
        logger.info(f"Invoice sent to user {update.effective_user.id}")
    except Exception as e:
        logger.error(f"Error in buy_stars function: {str(e)}")
        await update.message.reply_text("Sorry, there was an error processing your request. Please try again later.")

async def pre_checkout_callback(update: Update, context):
    query = update.pre_checkout_query
    if query.invoice_payload != "Custom-Payload":
        await query.answer(ok=False, error_message="Something went wrong...")
    else:
        await query.answer(ok=True)

async def successful_payment_callback(update: Update, context):
    user_id = update.effective_user.id
    amount = update.message.successful_payment.total_amount // 100  # Конвертация копеек в доллары

    user = db_session.query(User).filter_by(telegram_id=str(user_id)).first()
    if user:
        user.xtr_balance += amount
        db_session.commit()
        await update.message.reply_text(f'Thank you for your payment! {amount} XTR stars have been added to your balance.')
    else:
        new_user = User(
            telegram_id=str(user_id),
            username=update.effective_user.username,
            xtr_balance=amount
        )
        db_session.add(new_user)
        db_session.commit()
        await update.message.reply_text(
            f'Thank you for your payment! A new account has been created for you with {amount} XTR stars.'
        )

def setup_bot() -> Application:
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN is not set in the environment variables")
        raise ValueError("TELEGRAM_BOT_TOKEN is not set in the environment variables")

    logger.info(f"Setting up bot with token: {bot_token[:5]}...{bot_token[-5:]}")

    application = Application.builder().token(bot_token).build()

    logger.info("Adding command handlers")
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('register', register))
    application.add_handler(CommandHandler('buy_stars', buy_stars))
    application.add_handler(PreCheckoutQueryHandler(pre_checkout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))

    logger.info("Bot setup completed")
    return application

async def send_notification(application: Application, user_id: int, message: str):
    user = db_session.query(User).filter_by(id=user_id).first()
    if user and user.telegram_id:
        try:
            await application.bot.send_message(chat_id=int(user.telegram_id), text=message)
            logger.info(f"Notification sent to user {user_id}")
        except BadRequest as e:
            logger.error(f"BadRequest when sending notification to user {user_id}: {str(e)}")
        except Exception as e:
            logger.error(f"Error sending notification to user {user_id}: {str(e)}")
