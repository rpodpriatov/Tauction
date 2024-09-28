import os
import logging
from telegram import Update, LabeledPrice
from telegram.ext import (
    Application,
    CommandHandler,
    PreCheckoutQueryHandler,
    MessageHandler,
    filters,
    CallbackContext
)
from telegram.error import BadRequest
from models import User
from db import db_session

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

PAYMENT_PROVIDER_TOKEN = os.environ.get('PAYMENT_PROVIDER_TOKEN')

application = None

async def start(update: Update, context: CallbackContext):
    logger.info(f"User {update.effective_user.id} started the bot")
    await update.message.reply_text(
        'Welcome to the Auction Platform Bot! Use /buy_stars_yoomoney <amount> to purchase XTR stars.'
    )

async def buy_stars_yoomoney(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    amount = context.args[0] if context.args else "10"
    try:
        amount = int(amount)
        if amount < 1:
            await update.message.reply_text("Minimum purchase amount is 1 XTR.")
            return
        if amount > 100:
            await update.message.reply_text("Maximum purchase amount is 100 XTR for test payments.")
            return
    except ValueError:
        await update.message.reply_text("Please provide a valid number of XTR to purchase.")
        return

    price_in_kopecks = amount * 1000  # 1 XTR = 10 RUB, in kopecks

    invoice_params = {
        "chat_id": user_id,
        "title": "XTR Stars",
        "description": f"Purchase of {amount} XTR stars",
        "payload": f"xtr_stars_{amount}",
        "provider_token": PAYMENT_PROVIDER_TOKEN,
        "currency": "RUB",
        "prices": [LabeledPrice("XTR Stars", price_in_kopecks)],
        "start_parameter": "xtr-stars-payment"
    }

    try:
        await context.bot.send_invoice(**invoice_params)
    except BadRequest as e:
        logger.error(f"BadRequest error when sending invoice: {str(e)}")
        await update.message.reply_text("Sorry, there was an error processing your request. Please try again later.")
    except Exception as e:
        logger.error(f"Unexpected error when sending invoice: {str(e)}")
        await update.message.reply_text("An unexpected error occurred. Please try again later.")

async def pre_checkout_callback(update: Update, context: CallbackContext):
    query = update.pre_checkout_query
    if query.invoice_payload.startswith("xtr_stars_"):
        await query.answer(ok=True)
    else:
        await query.answer(ok=False, error_message="Something went wrong...")

async def successful_payment_callback(update: Update, context: CallbackContext):
    payment = update.message.successful_payment
    amount = int(payment.total_amount / 1000)  # Convert back from kopecks to XTR
    user_id = update.effective_user.id

    user = db_session.query(User).filter_by(telegram_id=str(user_id)).first()
    if user:
        user.xtr_balance += amount
        db_session.commit()
        await update.message.reply_text(
            f'Thank you for your payment! {amount} XTR stars have been added to your balance.'
        )
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
    global application
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN is not set in the environment variables")
        raise ValueError("TELEGRAM_BOT_TOKEN is not set in the environment variables")

    logger.info(f"Setting up bot with token: {bot_token[:5]}...{bot_token[-5:]}")

    application = Application.builder().token(bot_token).build()

    logger.info("Adding command handlers")
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('buy_stars_yoomoney', buy_stars_yoomoney))
    application.add_handler(PreCheckoutQueryHandler(pre_checkout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))

    logger.info("Bot setup completed")
    return application

async def send_notification(user_id: int, message: str):
    logger.info(f"send_notification called with user_id={user_id}, message={message}")
    if application:
        try:
            await application.bot.send_message(chat_id=int(user_id), text=message)
            logger.info(f"Notification sent to user {user_id}")
        except Exception as e:
            logger.error(f"Error sending notification to user {user_id}: {str(e)}")
    else:
        logger.error("Telegram application is not initialized.")
