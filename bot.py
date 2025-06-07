from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# ⚙️ Адмін
ADMIN_USERNAME = "VladislavMorgan2"

# 🛒 Товари (зберігаються в оперативній пам'яті)
products = [
    {"name": "Флешка 32ГБ", "price": "150 грн", "color": "Золотистий, сріблястий"},
    {"name": "Липучка на телефон", "price": "50 грн", "color": "Чорний"}
]

# 🏁 /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Напиши /products, щоб переглянути товари.")

# 📦 /products
async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton(f"{p['name']}", callback_data=f"product_{i}")]
        for i in range(len(products))
    ]
    await update.message.reply_text("Ось доступні товари:", reply_markup=InlineKeyboardMarkup(buttons))

# 🛍 Відображення товару
async def show_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    index = int(query.data.split("_")[1])
    product = products[index]

    text = (
        f"📦 Назва: {product['name']}\n"
        f"💸 Ціна: {product['price']}\n"
        f"🎨 Колір: {product['color']}"
    )

    button = [[InlineKeyboardButton("✅ Замовити", callback_data=f"order_{index}")]]
    await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(button))

# ✅ Замовлення
async def order_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    username = user.username

    if not username:
        await query.edit_message_text("⚠️ Будь ласка, встанови username у налаштуваннях Telegram, щоб замовити товар.")
        return

    index = int(query.data.split("_")[1])
    product = products[index]

    # Повідомлення адміну
    admin_message = (
        f"🆕 Замовлення!\n"
        f"👤 Користувач: @{username}\n"
        f"📦 Товар: {product['name']}\n"
        f"💸 Ціна: {product['price']}"
    )

    await query.edit_message_text("✅ Замовлення прийнято! Ми з вами зв'яжемось.")
    await context.bot.send_message(chat_id=f"@{ADMIN_USERNAME}", text=admin_message)

# 🛠 Додати товар (admin only)
async def add_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if user.username != ADMIN_USERNAME:
        await update.message.reply_text("❌ Тільки адмін може додавати товари.")
        return

    try:
        data = ' '.join(context.args)
        name, price, color = data.split(";")
        products.append({"name": name.strip(), "price": price.strip(), "color": color.strip()})
        await update.message.reply_text(f"✅ Товар '{name}' додано.")
    except Exception as e:
        await update.message.reply_text("❌ Невірний формат. Використай /add Назва;Ціна;Колір")

# 🧹 Видалити товар (admin only)
async def delete_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if user.username != ADMIN_USERNAME:
        await update.message.reply_text("❌ Тільки адмін може видаляти товари.")
        return

    name = ' '.join(context.args).strip()
    for p in products:
        if p['name'].lower() == name.lower():
            products.remove(p)
            await update.message.reply_text(f"🗑 Товар '{name}' видалено.")
            return

    await update.message.reply_text("❌ Товар не знайдено.")

# 🚀 Головна функція
def main():
    app = Application.builder().token("YOUR_BOT_TOKEN").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("products", show_products))
    app.add_handler(CallbackQueryHandler(show_product, pattern="^product_"))
    app.add_handler(CallbackQueryHandler(order_product, pattern="^order_"))
    app.add_handler(CommandHandler("add", add_product))
    app.add_handler(CommandHandler("delete", delete_product))

    print("🟢 Бот працює!")
    app.run_polling()

if __name__ == "__main__":
    main()
