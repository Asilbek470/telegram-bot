import asyncio
import json
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, WebAppInfo
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# ====== SOZLAMALAR ======
BOT_TOKEN = "8767035251:AAE-uGLTGklkxir2hDfkw9DmekIGVw6cG9w"  # BU YERGA TOKEN QO'YING
CHANNEL_ID = "@efootballtest"
CARD_NUMBER = "8600 1234 5678 9012"
CARD_OWNER = "MAXMUDOV UMIDJON"
WEB_APP_URL = "https://reliable-frangipane-93eb9e.netlify.app/"

ADMINS_LIST = [
    "@Sa1dov707",
    "@OTAWCEEK1",
    "@efnext_admin",
    "@eFnext_Garand",
    "@ef_Abdurahmonov",
    "@ef_am1rbek",
    "@esports_adm",
    "@saidabrolov_s"
]

EXAMPLE_PHOTO_SELL = "AgACAgIAAxkBAAICh2nifDr7zJi-e5VBZ1OPKZx2sSgrAAKYEmsb8DUJS5BsObvReK_mAQADAgADeQADOwQ"
EXAMPLE_PHOTO_BUY = "AgACAgIAAxkBAAICjmnifjkb8L2Ng9e2RobCUPxG4xsUAAK2FWsbavQJSw-8Fj2iT9MkAQADAgADeQADOwQ"
DB_FILE = "users_ads.json"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class AdStates(StatesGroup):
    choosing_type = State()
    sending_photo = State()
    google_gc = State()
    obmen = State()
    sell_or_obmen = State()
    entering_price = State()
    buying_account_type = State()
    adding_comment = State()
    confirming = State()

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_user_ad(user_id, ad_data):
    db = load_db()
    uid = str(user_id)
    if uid not in db:
        db[uid] = []
    db[uid].append(ad_data)
    save_db(db)

def parse_price(text):
    text = text.replace(",", "").replace(".", "").replace(" ", "")
    price_raw = int(text)
    if price_raw < 10000:
        price = price_raw * 1000
    else:
        price = price_raw
    return price

def format_price(price):
    return f"{price:,}".replace(",", ".") + " so'm"

def calc_fee(price):
    if price <= 1999000:
        return 5000
    else:
        return 10000

main_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📝 ELON BERISH"), KeyboardButton(text="📂 ELONLARIM")],
    [KeyboardButton(text="👮 ADMINLAR"), KeyboardButton(text="📜 QOIDALAR")],
    [KeyboardButton(text="💰 ELON NARXI")]
], resize_keyboard=True)

def ad_type_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Sotish eloni", callback_data="type_sell"),
         InlineKeyboardButton(text="🔎 Olish eloni", callback_data="type_buy")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="cancel")]
    ])

def yes_no_kb(prefix):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Ha", callback_data=f"{prefix}_yes"),
         InlineKeyboardButton(text="❌ Yo'q", callback_data=f"{prefix}_no")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="cancel")]
    ])

def sell_obmen_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Narxni kiritish", callback_data="action_price"),
         InlineKeyboardButton(text="🔄 Faqat obmen", callback_data="action_obmen")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="cancel")]
    ])

def account_type_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔓 Toza", callback_data="acc_clean"),
         InlineKeyboardButton(text="🔗 Google/Game Center", callback_data="acc_linked")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="cancel")]
    ])

def payment_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Karta raqamiga to'lov", callback_data="show_card")],
        [InlineKeyboardButton(text="✅ To'lov qildim", callback_data="paid")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")]
    ])

def comment_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Izohim yo'q", callback_data="no_comment")]
    ])

def admins_kb():
    buttons = []
    for i in range(0, len(ADMINS_LIST), 2):
        row = [InlineKeyboardButton(text=ADMINS_LIST[i], url=f"https://t.me/{ADMINS_LIST[i][1:]}")]
        if i + 1 < len(ADMINS_LIST):
            row.append(InlineKeyboardButton(text=ADMINS_LIST[i+1], url=f"https://t.me/{ADMINS_LIST[i+1][1:]}"))
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🎮 UZPES SALE BOT ga xush kelibsiz!\n\neFootball akkountlarini xavfsiz sotib olish va sotish platformasi.", reply_markup=main_menu)

@dp.message(F.text == "📝 ELON BERISH")
async def elon_berish(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(AdStates.choosing_type)
    await message.answer("📋 E'lon turini tanlang:", reply_markup=ad_type_kb())

@dp.message(F.text == "👮 ADMINLAR")
async def adminlar(message: Message):
    await message.answer("👮 Garant adminlar:\n\n✅ Xavfsiz savdo uchun quyidagi adminlarga murojaat qiling:", reply_markup=admins_kb())

@dp.message(F.text == "📜 QOIDALAR")
async def qoidalar(message: Message):
    await message.answer("📜 QOIDALAR:\n\n⚠️ Qoida kiritilmagan.")

@dp.message(F.text == "💰 ELON NARXI")
async def elon_narxi(message: Message):
    await message.answer("💰 <b>Akkauntlarga e'lon berish narxlari:</b>\n\n<code>0 dan 1 999 000 gacha — 5 000 so'm</code>\n<code>2 000 000 dan yuqori — 10 000 so'm</code>\n\n♻️ <i>Botda avto tolov qilish imkoniyati mavjud!</i>\n\n❗ <i>Akkount olaman deb reklama berishingiz ham mumkin!</i>", parse_mode="HTML")

@dp.message(F.text == "📂 ELONLARIM")
async def elonlarim(message: Message):
    db = load_db()
    uid = str(message.from_user.id)
    ads = db.get(uid, [])
    if not ads:
        await message.answer("📂 Sizda hali e'lonlar yo'q.", reply_markup=main_menu)
        return
    ads_reversed = list(reversed(ads))
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for i, ad in enumerate(ads_reversed):
        btn_text = f"📦 {ad['type']} | {ad['price']}" if ad['type'] == "SOTISH" else f"🔎 {ad['type']} | {ad['price']}"
        original_index = len(ads) - 1 - i
        kb.inline_keyboard.append([InlineKeyboardButton(text=btn_text, callback_data=f"view_ad_{original_index}")])
    kb.inline_keyboard.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="cancel")])
    await message.answer("📂 <b>Sizning e'lonlaringiz:</b>\n\nQuyidagilardan birini tanlang:", reply_markup=kb, parse_mode="HTML")

@dp.callback_query(F.data.startswith("view_ad_"))
async def view_ad(callback: CallbackQuery, state: FSMContext):
    idx = int(callback.data.split("_")[-1])
    db = load_db()
    uid = str(callback.from_user.id)
    ads = db.get(uid, [])
    if idx >= len(ads):
        await callback.answer("❌ E'lon topilmadi!", show_alert=True)
        return
    ad = ads[idx]
    photo_id = ad.get("photo_id")
    caption = ad.get("caption", "").strip()
    msg_id = ad.get("channel_msg_id")
    channel_username = CHANNEL_ID.replace("@", "")
    channel_link = f"https://t.me/{channel_username}/{msg_id}" if msg_id else f"https://t.me/{channel_username}"
    if not photo_id and not caption:
        await callback.answer("❌ Ushbu elon ma'lumotlari yo'q!", show_alert=True)
        return
    try:
        if photo_id:
            await callback.message.answer_photo(photo=photo_id, caption=caption, parse_mode="HTML") if caption else await callback.message.answer_photo(photo=photo_id)
        else:
            await callback.message.answer(caption, parse_mode="HTML")
    except Exception as e:
        await callback.message.answer(f"❌ Xatolik: {str(e)}")
    meta_text = f"📊 <b>E'lon ma'lumotlari:</b>\n{ad['type']} | {ad['price']} | {ad['date']}"
    view_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📢 Kanalda ko'rish", url=channel_link)]])
    await callback.message.answer(meta_text, reply_markup=view_kb, parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "cancel")
async def cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("❌ Jarayon bekor qilindi.", reply_markup=main_menu)
    await callback.answer()

@dp.callback_query(F.data == "no_comment")
async def no_comment(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data.get("ad_type") == "SOTISH":
        await send_confirmation(callback.message, state, "Yo'q")
    else:
        await callback.message.answer("❌ Iltimos, izoh yozing. Bu maydon majburiy:")
    await callback.answer()

@dp.callback_query(F.data.in_(["acc_clean", "acc_linked"]))
async def account_type_selected(callback: CallbackQuery, state: FSMContext):
    gc_type = "Toza" if callback.data == "acc_clean" else "Ulangan"
    await state.update_data(google_gc=gc_type)
    await state.set_state(AdStates.adding_comment)
    await callback.message.edit_text("✏️ Qo'shimcha izoh yozing (majburiy):")
    await callback.answer()

async def send_confirmation(message_obj, state, comment_text):
    data = await state.get_data()
    user_id = message_obj.from_user.id
    username = "@" + message_obj.from_user.username if message_obj.from_user.username else f"ID: {user_id}"
    obmen_text = data.get("obmen", "Yoq")
    gc_text = data.get("google_gc", "Toza")
    fee_val = data.get("fee", 5000)
    price_text = data.get("price_text", "Noma'lum")
    ad_type = data.get("ad_type", "SOTISH")
    is_obmen_only = data.get("is_obmen_only", False)
    photo_id = data.get("photo_id")
    admins_formatted = "\n".join([f"▪️ {admin}" for admin in ADMINS_LIST])
    hashtags = []
    if ad_type == "SOTISH":
        if not is_obmen_only:
            hashtags.append("#SOTILADI")
        if obmen_text == "Bor" or is_obmen_only:
            hashtags.append("#OBMEN")
        hashtags.append("#ULANGAN" if gc_text == "Ulangan" else "#TOZA")
    else:
        hashtags.append("#OLINADI")
        hashtags.append("#GOOGLE_GAMECENTER" if gc_text == "Ulangan" else "#TOZA")
    hashtags_str = " ".join(hashtags)
    if ad_type == "SOTISH":
        caption = f"{hashtags_str}\n\n💰 <b>Narx:</b> {price_text}\n🔄 <b>Obmen:</b> {obmen_text}\n📱 <b>Google & Game Center:</b> {gc_text}\n👤 <b>Murojaat:</b> {username}\n\n📋 <b>Qo'shimcha ma'lumot:</b>\n{comment_text}\n\n━━━━━━━━━━━━━━━━━━━━\n🔄 <b>OLDI SOTDI GARANT ADMINLAR</b>\n{admins_formatted}\n\n🤖 <b>ELON BERISH UCHUN BOTIMIZ</b>\n@uzpes_sale_bot"
    else:
        caption = f"{hashtags_str}\n\n💰 <b>Byudjet:</b> {price_text}\n👤 <b>Murojaat:</b> {username}\n\n📋 <b>Qo'shimcha ma'lumot:</b>\n{comment_text}\n\n━━━━━━━━━━━━━━━━━━━━\n🔄 <b>OLDI SOTDI GARANT ADMINLAR</b>\n{admins_formatted}\n\n🤖 <b>ELON BERISH UCHUN BOTIMIZ</b>\n@uzpes_sale_bot"
    await state.update_data(caption=caption, username=username, comment=comment_text)
    await state.set_state(AdStates.confirming)
    try:
        if ad_type == "SOTISH" and photo_id:
            await message_obj.answer_photo(photo=photo_id, caption=caption, parse_mode="HTML")
        elif ad_type == "OLISH" and EXAMPLE_PHOTO_BUY:
            await message_obj.answer_photo(photo=EXAMPLE_PHOTO_BUY, caption=caption, parse_mode="HTML")
        else:
            await message_obj.answer(caption, parse_mode="HTML")
    except Exception as e:
        print(f"Post preview xatolik: {e}")
        await message_obj.answer(caption, parse_mode="HTML")
    await message_obj.answer("✅ <b>Elon kanalga yuborish uchun tayyor!</b>\n\n💰 Xizmat haqi: {} so'm\n💳 Quyidagi tugma orqali to'lov qiling va tasdiqlang.".format(fee_val), reply_markup=payment_kb(), parse_mode="HTML")

@dp.callback_query(F.data.in_(["type_sell", "type_buy"]))
async def choose_type(callback: CallbackQuery, state: FSMContext):
    ad_type = "SOTISH" if callback.data == "type_sell" else "OLISH"
    await state.update_data(ad_type=ad_type)
    if ad_type == "SOTISH":
        await state.set_state(AdStates.sending_photo)
        if EXAMPLE_PHOTO_SELL:
            await callback.message.answer_photo(photo=EXAMPLE_PHOTO_SELL, caption="📱 Shu ko'rinishda asosiy tarkib (squad) rasmini yuboring:")
        else:
            await callback.message.answer("📱 Shu ko'rinishda asosiy tarkib (squad) rasmini yuboring:")
    else:
        await state.update_data(photo_id=None, obmen="Yoq", fee=5000)
        await state.set_state(AdStates.entering_price)
        await callback.message.answer("💰 Qancha narxgacha akkount qidiryapsiz?")
    await callback.answer()

@dp.message(AdStates.sending_photo, F.photo)
async def get_photo(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(photo_id=photo_id)
    await state.set_state(AdStates.google_gc)
    await message.delete()
    await message.answer("📱 Akkountga Google yoki Game Center ulanganmi?", reply_markup=yes_no_kb("google"))

@dp.callback_query(F.data.in_(["google_yes", "google_no"]))
async def google_answer(callback: CallbackQuery, state: FSMContext):
    val = "Ulangan" if callback.data == "google_yes" else "Toza"
    await state.update_data(google_gc=val)
    await state.set_state(AdStates.obmen)
    await callback.message.edit_text("🔄 Obmen ko'rasizmi?", reply_markup=yes_no_kb("obmen"))
    await callback.answer()

@dp.callback_query(F.data.in_(["obmen_yes", "obmen_no"]))
async def obmen_answer(callback: CallbackQuery, state: FSMContext):
    val = "Bor" if callback.data == "obmen_yes" else "Yoq"
    await state.update_data(obmen=val)
    await state.set_state(AdStates.sell_or_obmen)
    await callback.message.edit_text("💡 Akkount sotiladimi yoki faqat obmen uchunmi?", reply_markup=sell_obmen_kb())
    await callback.answer()

@dp.callback_query(F.data.in_(["action_price", "action_obmen"]))
async def sell_or_obmen_handler(callback: CallbackQuery, state: FSMContext):
    if callback.data == "action_obmen":
        await state.update_data(price_text="Obmen", fee=5000, is_obmen_only=True)
        await state.set_state(AdStates.adding_comment)
        await callback.message.edit_text("✏️ Qo'shimcha izoh yozing (ixtiyoriy):\nAgar izohingiz bo'lmasa, \"Izohim yo'q\" tugmasini bosing yoki - yuboring.", reply_markup=comment_kb())
    else:
        await state.update_data(is_obmen_only=False)
        await state.set_state(AdStates.entering_price)
        await callback.message.edit_text("💰 Akkount narxini yuboring.")
    await callback.answer()

@dp.message(AdStates.entering_price)
async def get_price(message: Message, state: FSMContext):
    data = await state.get_data()
    ad_type = data.get("ad_type")
    text = message.text.replace(",", "").replace(".", "").replace(" ", "")
    try:
        price = parse_price(text)
        if price < 10000:
            await message.answer("❌ Narx juda kam! Qayta kiriting:")
            return
        await message.delete()
        fee = calc_fee(price)
        price_formatted = format_price(price)
        await state.update_data(price_text=price_formatted, fee=fee, price_int=price)
        if ad_type == "OLISH":
            await state.set_state(AdStates.buying_account_type)
            await message.answer("📱 Qanday akkount qidiryapsiz?", reply_markup=account_type_kb())
        else:
            await state.set_state(AdStates.adding_comment)
            await message.answer("✏️ Qo'shimcha izoh yozing (ixtiyoriy):\nAgar izohingiz bo'lmasa, \"Izohim yo'q\" tugmasini bosing yoki - yuboring.", reply_markup=comment_kb())
    except ValueError:
        await message.answer("❌ Faqat raqam kiriting!")

@dp.message(AdStates.adding_comment)
async def get_comment(message: Message, state: FSMContext):
    data = await state.get_data()
    ad_type = data.get("ad_type")
    if ad_type == "OLISH":
        if message.text == "-" or message.text.lower() == "izohim yo'q":
            await message.answer("❌ Iltimos, izoh yozing. Bu maydon majburiy:")
            return
        comment = message.text
    else:
        comment = "Yo'q" if message.text == "-" or message.text.lower() == "izohim yo'q" else message.text
    await message.delete()
    await send_confirmation(message, state, comment)

# ====== WEB APP BILAN TO'LOV ======
@dp.callback_query(F.data == "show_card")
async def show_card(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    fee_val = data.get("fee", 5000)
    clean_card = CARD_NUMBER.replace(" ", "")
    app_url = f"{WEB_APP_URL}?price={fee_val}&card={clean_card}&owner={CARD_OWNER}"
    
    # Web App tugmasi
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 To'lovni amalga oshirish", web_app=WebAppInfo(url=app_url))]
    ])
    
    await callback.message.answer(
        f"💰 <b>To'lov summasi:</b> {fee_val} so'm\n\n"
        f"👇 Quyidagi tugmani bosing va to'lovni amalga oshiring:",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await callback.answer()

@dp.message(F.web_app_data)
async def web_app_payment(message: Message, state: FSMContext):
    if message.web_app_data.data == "paid":
        data = await state.get_data()
        try:
            caption = data.get("caption", "Elon")
            photo_id = data.get("photo_id")
            ad_type = data.get("ad_type", "SOTISH")
            if ad_type == "OLISH":
                sent_msg = await bot.send_photo(CHANNEL_ID, photo=EXAMPLE_PHOTO_BUY, caption=caption, parse_mode="HTML") if EXAMPLE_PHOTO_BUY else await bot.send_message(CHANNEL_ID, caption, parse_mode="HTML")
            elif photo_id:
                sent_msg = await bot.send_photo(CHANNEL_ID, photo=photo_id, caption=caption, parse_mode="HTML")
            else:
                sent_msg = await bot.send_message(CHANNEL_ID, caption, parse_mode="HTML")
            msg_id = sent_msg.message_id
            save_user_ad(message.from_user.id, {
                "type": ad_type,
                "price": data.get("price_text", "Noma'lum"),
                "date": datetime.now().strftime("%d.%m.%Y %H:%M"),
                "comment": data.get("comment", "Yo'q"),
                "photo_id": photo_id if ad_type == "SOTISH" else EXAMPLE_PHOTO_BUY,
                "channel_msg_id": msg_id,
                "caption": caption
            })
            await message.answer("✅ <b>To'lov tasdiqlandi!</b>\nElon kanalga joylandi!\n\n📢 Kanalimiz: " + CHANNEL_ID, reply_markup=main_menu, parse_mode="HTML")
        except Exception as e:
            await message.answer(f"❌ Xatolik: {str(e)}")
        await state.clear()

@dp.callback_query(F.data == "paid")
async def payment_done(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    try:
        caption = data.get("caption", "Elon")
        photo_id = data.get("photo_id")
        ad_type = data.get("ad_type", "SOTISH")
        if ad_type == "OLISH":
            sent_msg = await bot.send_photo(CHANNEL_ID, photo=EXAMPLE_PHOTO_BUY, caption=caption, parse_mode="HTML") if EXAMPLE_PHOTO_BUY else await bot.send_message(CHANNEL_ID, caption, parse_mode="HTML")
        elif photo_id:
            sent_msg = await bot.send_photo(CHANNEL_ID, photo=photo_id, caption=caption, parse_mode="HTML")
        else:
            sent_msg = await bot.send_message(CHANNEL_ID, caption, parse_mode="HTML")
        msg_id = sent_msg.message_id
        save_user_ad(callback.from_user.id, {
            "type": ad_type,
            "price": data.get("price_text", "Noma'lum"),
            "date": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "comment": data.get("comment", "Yo'q"),
            "photo_id": photo_id if ad_type == "SOTISH" else EXAMPLE_PHOTO_BUY,
            "channel_msg_id": msg_id,
            "caption": caption
        })
        await callback.message.answer("✅ <b>To'lov tasdiqlandi!</b>\nElon kanalga joylandi!\n\n📢 Kanalimiz: " + CHANNEL_ID, reply_markup=main_menu, parse_mode="HTML")
    except Exception as e:
        await callback.message.answer(f"❌ Xatolik: {str(e)}")
    await state.clear()
    await callback.answer()

async def main():
    print("✅ Bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())