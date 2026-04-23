# 🏴‍☠️ Sentry-Bot

Sentry-Bot is a Discord bot that automates onboarding for AMFOSS.

It verifies new members using Google Sheets data, assigns roles and balanced factions, and guides users through a smooth onboarding experience.

---

## ⚙️ Features

- ✅ Verifies users via Google Sheets (Discord ID match)  
- 🎭 Assigns S1/S3 roles automatically  
- ⚔️ Balances and assigns faction roles  
- 💬 Sends welcome messages (DM + fallback)  
- 📢 Announces new members in faction channels  
- 📝 Logs activity in a dedicated `#bot-logs` channel  

---

## 🚀 How It Works

1. User fills the Google Form  
2. User joins the Discord server  
3. Bot verifies their Discord ID  
4. Roles and faction are assigned  
5. User receives onboarding message  

---

## 🛠️ Tech Stack

- Python (`discord.py`)  
- Google Sheets API (`gspread`)  

---

## 📌 Note

- Users must enter the correct Discord ID in the form  
- Bot requires proper role permissions in the server  

---

## ⚓ Status

Actively built for AMFOSS onboarding automation.
