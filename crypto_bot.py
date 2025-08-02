import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes


TOKEN = "7732549589:AAGNdhJtverkwj0fRSTFvcJpGo8oxXdhV-k"

 # <-- Replace with your bot token

COINGECKO_API = "https://api.coingecko.com/api/v3/coins/markets"
VS_CURRENCY = "usd"

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to CryptoBot!\n"
        "Commands:\n"
        "/price <coin_id> - Get price info (e.g. /price bitcoin)\n"
        "/search <name> - Search coins by name\n"
        "/top <sort_by> - Top coins sorted by: market_cap, volume, price_change_percentage_24h (e.g. /top market_cap)\n"
    )

# /price command
async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /price <coin_id> (e.g. /price bitcoin)")
        return
    coin = context.args[0].lower()
    params = {
        "vs_currency": VS_CURRENCY,
        "ids": coin,
        "price_change_percentage": "1h,24h,7d"
    }
    try:
        response = requests.get(COINGECKO_API, params=params)
        data = response.json()
        if not data:
            await update.message.reply_text("Coin not found. Try /search <name>.")
            return
        coin_data = data[0]
        msg = (
            f"**{coin_data['name']} ({coin_data['symbol'].upper()})**\n"
            f"Current Price: ${coin_data['current_price']}\n"
            f"1h Change: {coin_data.get('price_change_percentage_1h_in_currency', 0):.2f}%\n"
            f"24h Change: {coin_data.get('price_change_percentage_24h_in_currency', 0):.2f}%\n"
            f"7d Change: {coin_data.get('price_change_percentage_7d_in_currency', 0):.2f}%"
        )
        await update.message.reply_text(msg, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# /search command
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /search <name>")
        return
    query = " ".join(context.args).lower()
    try:
        response = requests.get("https://api.coingecko.com/api/v3/coins/list")
        coins = response.json()
        results = [c for c in coins if query in c['name'].lower()]
        if not results:
            await update.message.reply_text("No coins found.")
            return
        msg = "\n".join([f"{c['name']} (id: {c['id']})" for c in results[:10]])
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# /top command
async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sort_by = context.args[0] if context.args else "market_cap"
    order_map = {
        "market_cap": "market_cap_desc",
        "volume": "volume_desc",
        "price_change_percentage_24h": "price_change_percentage_24h_desc"
    }
    order = order_map.get(sort_by, "market_cap_desc")
    params = {
        "vs_currency": VS_CURRENCY,
        "order": order,
        "per_page": 100,
        "page": 1,
        "price_change_percentage": "1h,24h,7d"
    }
    try:
        response = requests.get(COINGECKO_API, params=params)
        data = response.json()
        msg = ""
        for coin in data:
            msg += (
                f"{coin['name']} (${coin['current_price']}) | "
                f"24h: {coin.get('price_change_percentage_24h_in_currency', 0):.2f}%\n"
            )
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# Main function to run the bot
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("search", search))
    app.add_handler(CommandHandler("top", top))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()