# Auction Platform

An auction platform with Telegram authentication, built with Flask and JavaScript, using PostgreSQL for data storage.

## Features

- User authentication via Telegram
- Create and manage auctions
- Bidding system
- Watchlist functionality
- Telegram bot for notifications and star purchases
- Subscription system for extended features
- Multiple auction types (English, Dutch, Sealed-bid)
- YooMoney integration for payments

## Graceful Shutdown

The application implements a graceful shutdown process to ensure all components are properly closed when the application is terminated. This includes:

1. Stopping the web application
2. Shutting down the Telegram bot
3. Stopping the scheduler
4. Closing database connections
5. Cancelling any remaining tasks
6. Stopping the event loop

The graceful shutdown is triggered when the application receives a termination signal (SIGTERM, SIGINT, or SIGHUP).

## Setup and Installation

(Add setup and installation instructions here)

## Usage

(Add usage instructions here)

## Contributing

(Add contribution guidelines here)

## License

(Add license information here)
