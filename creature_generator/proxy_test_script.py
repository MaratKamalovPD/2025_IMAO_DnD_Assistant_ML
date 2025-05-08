import requests

# Прокси настройки (замени на свои при необходимости)
proxies = {
    'http': 'socks5h://127.0.0.1:10808',
    'https': 'socks5h://127.0.0.1:10808'
}

# Функция для получения IP и страны по IP
def get_ip_info(proxy=None):
    try:
        # Получаем IP
        ip_resp = requests.get('https://api.ipify.org?format=json', proxies=proxy, timeout=10)
        ip = ip_resp.json()['ip']

        # Получаем страну по IP
        geo_resp = requests.get(f'https://ipapi.co/{ip}/json/', timeout=10)
        geo_data = geo_resp.json()

        country = geo_data.get('country_name', 'Unknown')
        city = geo_data.get('city', 'Unknown')

        return {
            'ip': ip,
            'country': country,
            'city': city
        }

    except Exception as e:
        return {
            'error': str(e)
        }

# Получаем IP без прокси
print("🟢 Без прокси:")
no_proxy_info = get_ip_info()
print(no_proxy_info)

# Получаем IP через прокси
print("\n🟠 Через SOCKS5 прокси:")
proxy_info = get_ip_info(proxy=proxies)
print(proxy_info)
