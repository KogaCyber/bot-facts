import telebot
import schedule
import time
import requests
from datetime import datetime
import json
import os
from anthropic import Anthropic
import random
import pytz
from dotenv import load_dotenv

load_dotenv()

TIMEZONE = pytz.timezone('Asia/Tashkent')

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

if not all([BOT_TOKEN, CHANNEL_ID, PEXELS_API_KEY, ANTHROPIC_API_KEY]):
    print("Error: Missing API keys. Please set all required API keys.")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)
client = Anthropic(api_key=ANTHROPIC_API_KEY)

COST_PER_1K_TOKENS = 0.002
INITIAL_BALANCE = 5.0

STATS_FILE = 'bot_stats.json'

PORT = int(os.environ.get('PORT', 8080))

def load_stats():
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'r') as f:
            return json.load(f)
    return {
        'total_tokens': 0,
        'total_cost': 0,
        'start_date': datetime.now().strftime('%Y-%m-%d'),
        'facts_generated': 0
    }

def save_stats(stats):
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=4)

stats = load_stats()

def update_stats(tokens_used):
    stats['total_tokens'] += tokens_used
    stats['total_cost'] += (tokens_used / 1000) * COST_PER_1K_TOKENS
    stats['facts_generated'] += 1
    save_stats(stats)
    
    remaining_balance = INITIAL_BALANCE - stats['total_cost']
    days_running = (datetime.now() - datetime.strptime(stats['start_date'], '%Y-%m-%d')).days or 1
    
    print('\nSTATISTIKA:')
    print(f"💰 Qolgan balans: ${remaining_balance:.3f}")
    print(f"📊 Jami tokenlar: {stats['total_tokens']}")
    print(f"💵 Jami xarajat: ${stats['total_cost']:.3f}")
    print(f"📝 Jami faktlar: {stats['facts_generated']}")
    print(f"📅 Kunlik o'rtacha: {stats['facts_generated'] / days_running:.1f} faktlar")
    print(f"💸 Kunlik xarajat: ${stats['total_cost'] / days_running:.4f}")
    
    if remaining_balance < 1:
        print("\n⚠️ OGOHLANTIRISH: Balans $1 dan kam qoldi!")

def normalize_fact(fact):
    normalized = fact.lower().strip()
    normalized = normalized.replace('mlrd', 'milliard')
    normalized = ''.join(c for c in normalized if c.isalnum() or c.isspace())
    normalized = ' '.join(normalized.split())
    return normalized

def get_ai_fact():
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=80,
            messages=[
                {
                    "role": "user", 
                    "content": """Generate one fascinating and 100% VERIFIED scientific fact in Uzbek with a clear explanation. Focus on well-documented scientific phenomena that can be easily visualized.

IMPORTANT RULES:
1. First line: scientific fact (max 50 characters)
2. Second line: detailed explanation with "Chunki" (max 80 characters)
3. Use simple but precise Uzbek words
4. ONLY use facts that have clear scientific evidence
5. Explanation MUST be detailed enough to fully understand the fact
6. Each fact should be visually representable with a photo
7. NO unverified or questionable facts
8. NO oversimplified or misleading explanations
9. Focus on facts that can be clearly explained
10. Prefer facts about visible phenomena or structures
11. Include specific details in the explanation
12. If fact requires complex explanation - choose different fact

GOOD EXAMPLES:
- Fact: Kolibri yuragining urishi minutiga 1200 marta
  Chunki juda tez harakat qilish uchun yuqori energiya talab qilinadi
  [keywords: hummingbird, heart, speed]

- Fact: Ayiq bir kunda 40 kg gacha asalni yeya oladi
  Chunki uning oshqozoni katta hajmda oziq-ovqatni hazm qila oladi
  [keywords: bear, honey, eating]

BAD EXAMPLES:
- Fact: Toshbaqalar orqali nafas oladi
  Chunki ular qishda muzli suvda uxlaydi
  (Wrong fact + poor explanation)

- Fact: Hayvonlar ovqat yeydi
  Chunki ularga energiya kerak
  (Too obvious + too simple explanation)

FORMAT:
[Scientific fact]
[Detailed explanation]

[keywords: main_subject, action, detail, visual_element]"""
                }
            ]
        )
        
        total_tokens = response.usage.input_tokens + response.usage.output_tokens
        update_stats(total_tokens)
        
        text = response.content[0].text.strip()
        text = text.replace('"', '')
        text = text.split('(')[0].strip()
        
        parts = text.split('[keywords:')
        fact_text = parts[0].strip()
        keywords = parts[-1].replace(']', '').strip() if len(parts) > 1 else 'interesting fact, world, nature'
        
        fact_parts = [p.strip() for p in fact_text.split('\n') if p.strip()]
        
        if len(fact_parts) >= 2:
            main_fact = fact_parts[0]
            explanation = fact_parts[1]
            
            if not explanation.lower().startswith('chunki'):
                explanation = 'Chunki ' + explanation
            
            fact = f"{main_fact}\n{explanation}"
        else:
            text_parts = fact_text.split('Chunki')
            if len(text_parts) == 2:
                main_fact = text_parts[0].strip()
                explanation = 'Chunki ' + text_parts[1].strip()
                fact = f"{main_fact}\n{explanation}"
            else:
                fact = fact_text
        
        keywords = keywords.split('\n')[0].strip()
        
        return fact, keywords
    except Exception as e:
        print(f"Fakt generatsiyasida xatolik: {e}")
        return """Asalarilar ultrabinafsha nur ko'radi.
Chunki ularda maxsus ko'z tuzilishi bor.""", "bee, vision, ultraviolet"

def get_image(keywords):
    try:
        keywords_list = [word.strip().lower() for word in keywords.split(',')]
        main_subject = keywords_list[0] if keywords_list else ''
        action = keywords_list[1] if len(keywords_list) > 1 else ''
        detail = keywords_list[2] if len(keywords_list) > 2 else ''
        visual = keywords_list[3] if len(keywords_list) > 3 else ''
        
        search_queries = [
            f"{main_subject} {action} {detail}",
            f"{main_subject} {visual} closeup",
            f"{main_subject} {action} nature",
            f"{main_subject} {detail} photography",
            f"{main_subject} wildlife professional",
            f"{main_subject} high quality nature",
            "nature science photography"
        ]

        search_queries = [q for q in search_queries if len(q.strip()) > 10]

        for query in search_queries:
            response = requests.get(
                'https://api.pexels.com/v1/search',
                headers={'Authorization': PEXELS_API_KEY},
                params={
                    'query': query,
                    'per_page': 15,
                    'orientation': 'landscape',
                    'size': 'large',
                    'locale': 'en-US'
                }
            )
            response.raise_for_status()
            photos = response.json().get('photos', [])
            
            if photos:
                quality_photos = [p for p in photos 
                                if (p.get('width', 0) >= 3000 and 
                                    p.get('liked', False) or 
                                    'nature' in p.get('url', '').lower() or
                                    'wildlife' in p.get('url', '').lower())]
                if quality_photos:
                    return random.choice(quality_photos)['src']['large']
                return random.choice(photos[:5])['src']['large']
        
        return "https://images.pexels.com/photos/2387418/pexels-photo-2387418.jpeg"
    except Exception as e:
        print(f"Rasmni olishda xatolik: {e}")
        return "https://images.pexels.com/photos/2387418/pexels-photo-2387418.jpeg"

def get_tashkent_time():
    return datetime.now(TIMEZONE)

def send_facts(time_slot):
    try:
        sent_facts = set()
        facts_to_send = []
        attempts = 0
        max_attempts = 20
        
        while len(facts_to_send) < 4 and attempts < max_attempts:
            fact, keywords = get_ai_fact()
            normalized_fact = normalize_fact(fact)
            
            is_duplicate = any(normalize_fact(existing_fact) == normalized_fact 
                             for existing_fact, _ in facts_to_send)
            
            if not is_duplicate:
                facts_to_send.append((fact, keywords))
            
            attempts += 1
            if attempts >= max_attempts:
                print("Достигнуто максимальное количество попыток при сборе уникальных фактов")
        
        for fact, keywords in facts_to_send:
            try:
                image_url = get_image(keywords)
                fact_parts = fact.split('\n')
                if len(fact_parts) == 2:
                    message = f"{fact_parts[0]}\n👉 {fact_parts[1]}\n\n@bilim_faktlar"
                else:
                    message = f"{fact}\n\n@bilim_faktlar"
                    
                bot.send_photo(CHANNEL_ID, image_url, caption=message)
                time.sleep(3)
            except Exception as e:
                print(f"Fakt yuborishda xatolik: {e}")
                continue
    except Exception as e:
        print(f"Xatolik: {e}")

def schedule_facts():
    schedule.every().day.at("04:00").do(send_facts, "09:00")
    schedule.every().day.at("08:00").do(send_facts, "13:00")
    schedule.every().day.at("12:00").do(send_facts, "17:00")
    schedule.every().day.at("16:00").do(send_facts, "21:00")

def create_requirements():
    requirements = [
        'pyTelegramBotAPI',
        'schedule',
        'requests',
        'anthropic',
        'pytz'
    ]
    with open('requirements.txt', 'w') as f:
        for req in requirements:
            f.write(f"{req}\n")

if __name__ == "__main__":
    if not os.path.exists('requirements.txt'):
        create_requirements()
    
    schedule_facts()
    print(f"\nBot ishga tushdi. Port: {PORT}")
    print("Faktlar Toshkent vaqti bilan 09:00, 13:00, 17:00 va 21:00 da yuboriladi")
    print("Har bir vaqtda 4 ta noyob fakt yuboriladi")
    
    remaining_balance = INITIAL_BALANCE - stats['total_cost']
    print(f"\nJoriy balans: ${remaining_balance:.3f}")
    print(f"Jami faktlar: {stats['facts_generated']}")
    
    current_time = get_tashkent_time().strftime("%H:%M")
    send_facts(f"Test ishga tushishi - {current_time}")
    
    # Start the bot
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
    
    while True:
        schedule.run_pending()
        time.sleep(60)
