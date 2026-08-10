# RexPvP Welcome/Bye Telegram Bot

Guruhga yangi a'zo qo'shilganda **SmallCaps** shriftdagi tasodifiy "Xush
kelibsiz" matni + tasodifiy Premium stiker yuboradi. A'zo chiqib ketganda
esa tasodifiy "Xayr" matni + stiker yuboradi.

## 1. O'rnatish

```bash
python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Sozlash

`bot.py` faylini oching va tepasidagi ikkita qatorni to'ldiring:

```python
BOT_TOKEN = "SIZNING_BOT_TOKENINGIZ_BU_YERGA"
ADMIN_IDS = {123456789}
```

- **BOT_TOKEN**: Telegram'da [@BotFather](https://t.me/BotFather) ga yozib,
  `/newbot` orqali yangi bot yarating — u sizga token beradi.
- **ADMIN_IDS**: o'zingizning Telegram user_id raqamingiz. Uni bilish uchun
  [@userinfobot](https://t.me/userinfobot) ga `/start` yozing, u sizga
  ID raqamingizni ko'rsatadi. Bir nechta admin bo'lsa: `{111, 222, 333}`.

## 3. Botni guruhga qo'shish

1. Botni guruhingizga admin qilib qo'shing.
2. Bot sozlamalarida **"Group Privacy"** ni **OFF** qiling (@BotFather →
   Bot Settings → Group Privacy → Turn off). Aks holda bot a'zo
   kirish/chiqishlarini to'liq ko'ra olmasligi mumkin. (Aslida
   join/leave hodisalari privacy rejimidan qat'i nazar ko'rinadi, lekin
   xavfsizlik uchun o'chirib qo'yish tavsiya etiladi.)
3. Bot albatta guruhda **"Add members"/"a'zolarni boshqarish"** huquqiga
   ega admin bo'lishi kerak — aks holda kirish/chiqish hodisalarini
   to'liq kuzata olmaydi.

## 4. Ishga tushirish

```bash
python bot.py
```

Konsolda `Bot ishga tushmoqda...` degan xabarni ko'rsangiz — tayyor.

## 5. Admin buyruqlari (botga shaxsiy yoki guruhda yozing)

| Buyruq | Vazifasi |
|---|---|
| `/addwelcome <matn>` | Yangi "xush kelibsiz" matni qo'shadi |
| `/addbye <matn>` | Yangi "xayr" matni qo'shadi |
| `/addsticker` | Stikerga **reply** qilib yuboring — bot `welcome` yoki `bye` deb so'raydi, siz javob berasiz |
| `/listwelcome` | Barcha welcome matnlarini ID bilan ko'rsatadi |
| `/listbye` | Barcha bye matnlarini ID bilan ko'rsatadi |
| `/liststicker` | Barcha stikerlarni ID va turi bilan ko'rsatadi |
| `/delwelcome <id>` | Welcome matnini o'chiradi |
| `/delbye <id>` | Bye matnini o'chiradi |
| `/delsticker <id>` | Stikerni o'chiradi |

Matn ichida quyidagilarni ishlatishingiz mumkin:
- `{name}` → kirgan/chiqqan foydalanuvchi ismi
- `{chat}` → guruh nomi

**Misol:**
```
/addwelcome Salom {name}! {chat} ga xush kelibsiz, jang qilishga tayyormisiz? ⚔️
```
Bot buni avtomatik ravishda **sᴀʟᴏᴍ ᴏᴅᴀᴍ! ʀᴇxᴘᴠᴘ ɢᴀ xᴜꜱʜ ᴋᴇʟɪʙꜱɪᴢ...** shaklidagi
SmallCaps matnga aylantirib yuboradi.

## 6. Premium stikerlarni qo'shish

Premium (animatsion/Telegram Premium) stikerlarni ham xuddi oddiy stiker
kabi qo'shasiz — botga o'sha stikerni yuboring/forward qiling, unga reply
holida `/addsticker` yozing, so'ng `welcome` yoki `bye` deb javob bering.
Telegram API premium va oddiy stikerni bir xil tarzda `file_id` orqali
yuboradi, shuning uchun cheklov yo'q.

## 7. Railway.app'ga joylashtirish (deploy)

1. GitHub'da yangi bo'sh repository yarating (masalan `rexpvp-bot`).
2. Shu papkadagi barcha fayllarni (`bot.py`, `requirements.txt`, `Procfile`,
   `railway.json`, `runtime.txt`) o'sha repo'ga yuklang (push qiling).
3. [railway.app](https://railway.app) ga kiring, GitHub akkauntingiz bilan
   ro'yxatdan o'ting (karta talab qilinmaydi).
4. **"New Project" → "Deploy from GitHub repo"** ni tanlang, `rexpvp-bot`
   repo'ni tanlang.
5. Railway avtomatik `Procfile`ni tanib, botni **worker** turi sifatida
   ishga tushiradi (HTTP port ochishga hojat yo'q, chunki bot polling
   orqali ishlaydi).
6. Loyiha ochilgach, **"Variables"** bo'limiga o'ting va ikkita
   environment variable qo'shing:
   - `BOT_TOKEN` = @BotFather'dan olingan token
   - `ADMIN_IDS` = admin user_id(lar), vergul bilan ajratilgan
     (masalan: `123456789` yoki bir nechtasi: `123456789,987654321`)
7. Saqlang — Railway avtomatik qayta deploy qiladi va bot ishga tushadi.
   **"Deployments"** bo'limidagi loglardan `Bot ishga tushmoqda...`
   xabarini ko'rsangiz — tayyor.

⚠️ **Eslatma**: Railway'ning fayl tizimi har deploy'da tiklanishi (ephemeral)
mumkin bo'lgani uchun, agar bepul tarifda uzoq muddat ishlatsangiz, vaqti-
vaqti bilan `rexpvp_bot.db` fayli (matn/stiker ro'yxati) tozalanib qolishi
mumkin. Buning oldini olish uchun Railway'da **Volume** qo'shib, `DB_PATH`ni
o'sha volume ichiga ko'rsatishingiz mumkin (Settings → Volumes → Add Volume,
mount path: `/data`, so'ng kodda `DB_PATH`ni `/data/rexpvp_bot.db` qilib
o'zgartiring).

## 8. Bot uzluksiz ishlashi uchun (server / VPS)

`systemd` yoki `screen`/`tmux` yoki `pm2` kabi vositalar bilan fon
jarayoni sifatida ishga tushiring, masalan:

```bash
screen -S rexpvp_bot
source venv/bin/activate
python bot.py
# Ctrl+A keyin D bosib screen'dan chiqing (bot ishlashda davom etadi)
```

Ma'lumotlar `rexpvp_bot.db` (SQLite) faylida saqlanadi — bot qayta ishga
tushirilganda ham barcha matn va stikerlar saqlanib qoladi.
