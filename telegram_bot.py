import os
import logging
from telegram import Update, LabeledPrice
from telegram.ext import Application, CommandHandler, CallbackContext, PreCheckoutQueryHandler, MessageHandler, filters
from telegram.error import BadRequest
from models import User, Auction
from db import async_session
from sqlalchemy.future import select

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext):
    logger.info(f"User {update.effective_user.id} started the bot")
    await update.message.reply_text('Welcome to the Auction Platform Bot! Use /register to create an account and /buy_stars to purchase XTR stars.')

async def register(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    username = update.effective_user.username

    async with async_session() as session:
        result = await session.execute(select(User).filter_by(telegram_id=str(user_id)))
        user = result.scalar_one_or_none()
        if user:
            await update.message.reply_text('You are already registered!')
        else:
            new_user = User(telegram_id=str(user_id), username=username)
            session.add(new_user)
            await session.commit()
            await update.message.reply_text('Registration successful! You can now use the bot features.')

async def buy_stars(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    title = "XTR Stars Purchase"
    description = "Purchase XTR stars for use in auctions"
    payload = "Custom-Payload"
    provider_token = os.environ.get('PAYMENT_PROVIDER_TOKEN')
    currency = "RUB"
    price = 10000  # Price in kopecks (100 RUB)
    prices = [LabeledPrice("XTR Stars", price)]

    try:
        await context.bot.send_invoice(
            chat_id, title, description, payload, provider_token, currency, prices
        )
    except BadRequest as e:
        logger.error(f"Error sending invoice: {e}")
        await update.message.reply_text("Sorry, there was an error processing your request. Please try again later.")

async def pre_checkout_callback(update: Update, context: CallbackContext):
    query = update.pre_checkout_query
    if query.invoice_payload != "Custom-Payload":
        await query.answer(ok=False, error_message="Something went wrong...")
    else:
        await query.answer(ok=True)

async def successful_payment_callback(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    amount = update.message.successful_payment.total_amount // 100  # Convert kopecks to rubles

    async with async_session() as session:
        result = await session.execute(select(User).filter_by(telegram_id=str(user_id)))
        user = result.scalar_one_or_none()
        if user:
            user.xtr_balance += amount
            await session.commit()
            await update.message.reply_text(f'Thank you for your payment! {amount} XTR stars have been added to your balance.')
        else:
            new_user = User(telegram_id=str(user_id), username=update.effective_user.username, xtr_balance=amount)
            session.add(new_user)
            await session.commit()
            await update.message.reply_text(f'Thank you for your payment! A new account has been created for you with {amount} XTR stars.')

def setup_bot(app):
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN is not set in the environment variables")
        raise ValueError("TELEGRAM_BOT_TOKEN is not set in the environment variables")
    
    try:
        application = Application.builder().token(bot_token).build()
        logger.info("Telegram bot initialized successfully")

        application.add_handler(CommandHandler('start', start))
        application.add_handler(CommandHandler('register', register))
        application.add_handler(CommandHandler('buy_stars', buy_stars))
        application.add_handler(PreCheckoutQueryHandler(pre_checkout_callback))
        application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))

        return application
    except Exception as e:
        logger.error(f"Error initializing Telegram bot: {str(e)}")
        raise

async def send_notification(user_id, message):
    async with async_session() as session:
        result = await session.execute(select(User).filter_by(id=user_id))
        user = result.scalar_one_or_none()
        if user and user.telegram_id:
            bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
            if not bot_token:
                logger.error("TELEGRAM_BOT_TOKEN is not set in the environment variables")
                return
            try:
                bot = Application.builder().token(bot_token).build().bot
                await bot.send_message(chat_id=user.telegram_id, text=message)
                logger.info(f"Notification sent to user {user_id}")
            except Exception as e:
                logger.error(f"Error sending notification to user {user_id}: {str(e)}")
