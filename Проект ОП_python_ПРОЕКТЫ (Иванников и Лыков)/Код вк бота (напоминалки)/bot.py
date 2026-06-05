#TOKEN = "vk1.a.tMl9Ywr6S0WrxCsic_eh2H5sVjWeJqdm1um5cRH5vxxnmkr9N87VSsWFo1OG5HPDVN0RjnksV52coWKEw6FSAvcEGya1VsLWAWVEKPHOSqv-4vNB6mxt6AgKVIJgMXVqYX_G2B8T7KQx_gimf7TI8Q-IUphosQxqeLcOPvk4_d6pP4Iv6hMKoPcELjaqfJb2q-8yMnPvRAB9i_zU4a3FPQ"  # ← ВСТАВЬТЕ ТОКЕН
#GROUP_ID = 237646765

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import time
import threading
import datetime
import json
import os
import pytz

TOKEN = "vk1.a.tMl9Ywr6S0WrxCsic_eh2H5sVjWeJqdm1um5cRH5vxxnmkr9N87VSsWFo1OG5HPDVN0RjnksV52coWKEw6FSAvcEGya1VsLWAWVEKPHOSqv-4vNB6mxt6AgKVIJgMXVqYX_G2B8T7KQx_gimf7TI8Q-IUphosQxqeLcOPvk4_d6pP4Iv6hMKoPcELjaqfJb2q-8yMnPvRAB9i_zU4a3FPQ"  # ← ВСТАВЬТЕ ТОКЕН
GROUP_ID = 237646765

MSK = pytz.timezone('Europe/Moscow')

vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, GROUP_ID)

print("Запущен")
print("Ожидаю сообщения")

#НАПОМИНАНИЯ
REMINDERS_FILE = "reminders.json"

def load_reminders():
    """Загружает напоминания из файла"""
    if os.path.exists(REMINDERS_FILE):
        try:
            with open(REMINDERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_reminders(reminders):
    """Сохраняет напоминания в файл"""
    with open(REMINDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(reminders, f, ensure_ascii=False, indent=2)

# Глобальная переменная с напоминаниями
reminders = load_reminders()

def check_reminders():
    """Функция проверки напоминаний (работает в отдельном потоке)"""
    global reminders
    
    while True:
        try:
            now_msk = datetime.datetime.now(MSK)
            current_time = now_msk.strftime("%H:%M")
            current_date = now_msk.strftime("%d.%m.%Y")
            # Перебираем всех пользователей
            for user_id, user_reminders in reminders.items():
                for reminder in user_reminders[:]:  # [:] - копия для безопасного удаления
                    if reminder["time"] == current_time and reminder["date"] == current_date:
                        try:
                            # Отправляем напоминание
                            vk.messages.send(
                                peer_id=int(user_id),
                                message=f"🔔 НАПОМИНАНИЕ!\n\n{reminder['text']}\n\n⏰ {reminder['time']} (МСК)",
                                random_id=0
                            )
                            print(f"✅ Отправлено напоминание пользователю {user_id}: {reminder['text']}")
                            
                            # Удаляем отправленное напоминание
                            user_reminders.remove(reminder)
                            save_reminders(reminders)
                            
                        except Exception as e:
                            print(f"❌ Ошибка отправки пользователю {user_id}: {e}")
            
            time.sleep(30)  # Проверяем каждые 30 секунд
            
        except Exception as e:
            print(f"❌ Ошибка в check_reminders: {e}")
            time.sleep(60)

# Запускаем поток проверки напоминаний
reminder_thread = threading.Thread(target=check_reminders, daemon=True)
reminder_thread.start()
print("Система напоминаний активирована")

#ОСНОВНОЙ ЦИКЛ ОБРАБОТКИ СООБЩЕНИЙ
for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        message = event.object.message
        text = message['text'].lower().strip()
        user_id = str(message['from_id'])
        peer_id = message['peer_id']
        
        print(f"Сообщение от {user_id}: {text}")
 
        #КОМАНДА /start
        if text == "/start":
            vk.messages.send(
                peer_id=peer_id,
                message="🌟 Привет! Я бот-напоминалка!\n\n"
                        "⏰ Время указано по МОСКВЕ\n\n"
                        "📝 КОМАНДЫ:\n"
                        "▪️ /add ДД.ММ.ГГГГ ЧЧ:ММ Напоминание/Событие — добавить напоминание\n"
                        "▪️ /list — показать все напоминания\n"
                        "▪️ /del [номер] — удалить напоминание\n"
                        "▪️ /delall — удалить ВСЕ напоминания\n"
                        "▪️ /help — показать это сообщение\n\n"
                        "📌 ПРИМЕР: /add 15.05.2026 14:30 Позвонить маме",
                random_id=0
            )
        
        #КОМАНДА /help
        elif text == "/help":
            vk.messages.send(
                peer_id=peer_id,
                message="📚 СПРАВКА\n\n"
                        "▪️ /add ДД.ММ.ГГГГ ЧЧ:ММ текст\n"
                        "   ➜ Добавить напоминание\n\n"
                        "▪️ /list\n"
                        "   ➜ Показать список напоминаний\n\n"
                        "▪️ /del 1\n"
                        "   ➜ Удалить напоминание под номером 1\n\n"
                        "▪️ /delall\n"
                        "   ➜ Удалить все напоминания\n\n"
                        "⚠️ Время указывайте по МОСКВЕ!",
                random_id=0
            )
        
        #КОМАНДА /add 
        elif text.startswith("/add"):
            try:
                parts = text.split(maxsplit=3)
                if len(parts) < 4:
                    vk.messages.send(
                        peer_id=peer_id,
                        message="❌ Неправильный формат!\n"
                                "Используй: /add ДД.ММ.ГГГГ ЧЧ:ММ текст\n"
                                "Пример: /add 15.05.2024 14:30 Позвонить маме",
                        random_id=0
                    )
                else:
                    date_str = parts[1]
                    time_str = parts[2]
                    reminder_text = parts[3]
                    
                    #Проверка формата даты
                    try:
                        datetime.datetime.strptime(date_str, "%d.%m.%Y")
                    except:
                        vk.messages.send(peer_id=peer_id, message="❌ Неверный формат даты! Используй ДД.ММ.ГГГГ", random_id=0)
                        continue
                    
                    #Проверка формата времени
                    try:
                        datetime.datetime.strptime(time_str, "%H:%M")
                    except:
                        vk.messages.send(peer_id=peer_id, message="❌ Неверный формат времени! Используй ЧЧ:ММ (например, 14:30)", random_id=0)
                        continue
                    
                    #Сохраняем напоминание
                    if user_id not in reminders:
                        reminders[user_id] = []
                    
                    reminders[user_id].append({
                        "date": date_str,
                        "time": time_str,
                        "text": reminder_text
                    })
                    save_reminders(reminders)
                    
                    vk.messages.send(
                        peer_id=peer_id,
                        message=f"✅ Напоминание ДОБАВЛЕНО!\n\n"
                                f"📅 Дата: {date_str}\n"
                                f"⏰ Время: {time_str} (МСК)\n"
                                f"📝 Текст: {reminder_text}",
                        random_id=0
                    )
                    
            except Exception as e:
                vk.messages.send(peer_id=peer_id, message=f"❌ Ошибка: {e}", random_id=0)
        
        #КОМАНДА /list
        elif text == "/list":
            if user_id not in reminders or not reminders[user_id]:
                vk.messages.send(
                    peer_id=peer_id,
                    message="📭 У вас НЕТ активных напоминаний.\n\n"
                            "➕ Добавьте командой /add",
                    random_id=0
                )
            else:
                msg = "📋 ВАШИ НАПОМИНАНИЯ:\n\n"
                for i, rem in enumerate(reminders[user_id], 1):
                    msg += f"{i}. 📅 {rem['date']} ⏰ {rem['time']} (МСК)\n"
                    msg += f"   📝 {rem['text']}\n\n"
                msg += "🗑 Для удаления: /del [номер]"
                
                #Если сообщение слишком длинное, разбиваем на части
                if len(msg) > 4000:
                    vk.messages.send(peer_id=peer_id, message="📋 У вас слишком много напоминаний! Используйте /delall или /del", random_id=0)
                else:
                    vk.messages.send(peer_id=peer_id, message=msg, random_id=0)
        
        #КОМАНДА /del
        elif text.startswith("/del"):
            try:
                parts = text.split()
                if len(parts) != 2:
                    vk.messages.send(peer_id=peer_id, message="❌ Используй: /del [номер]\nПример: /del 1", random_id=0)
                else:
                    num = int(parts[1]) - 1
                    if user_id in reminders and 0 <= num < len(reminders[user_id]):
                        deleted = reminders[user_id].pop(num)
                        save_reminders(reminders)
                        vk.messages.send(
                            peer_id=peer_id,
                            message=f"✅ УДАЛЕНО напоминание:\n"
                                    f"📅 {deleted['date']} ⏰ {deleted['time']} (МСК)\n"
                                    f"📝 {deleted['text']}",
                            random_id=0
                        )
                    else:
                        vk.messages.send(peer_id=peer_id, message="❌ Напоминание с таким номером НЕ НАЙДЕНО!\n\nПроверьте список командой /list", random_id=0)
            except:
                vk.messages.send(peer_id=peer_id, message="❌ Введи номер команды: /del 1", random_id=0)
        
        #КОМАНДА /delall
        elif text == "/delall":
            if user_id in reminders and reminders[user_id]:
                reminders[user_id] = []
                save_reminders(reminders)
                vk.messages.send(
                    peer_id=peer_id,
                    message="✅ ВСЕ ваши напоминания УДАЛЕНЫ!",
                    random_id=0
                )
            else:
                vk.messages.send(
                    peer_id=peer_id,
                    message="📭 У вас нет активных напоминаний!",
                    random_id=0
                )
        
        #НЕИЗВЕСТНАЯ КОМАНДА
        else:
            vk.messages.send(
                peer_id=peer_id,
                message=f"Я бот-напоминалка!\n\n"
                        f"Ты написал: {text}\n\n"
                        f"Напиши /help для списка команд",
                random_id=0
            )
