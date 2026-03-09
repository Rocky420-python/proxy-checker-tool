import requests
import sys
import os
from fake_useragent import UserAgent
import random
import string
proxy_len_input = int(input('Enter the number of proxies you want to check: '))
proxy_url_api = f'https://api.proxyscrape.com/v4/free-proxy-list/get?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all&skip=0&limit={proxy_len_input}'

dead_proxy = []
working_proxy = []
total_proxy = 0


def progress_bar(current, total, bar_length=30):
    percent = current / total
    arrow = "█" * int(percent * bar_length)
    spaces = "░" * (bar_length - len(arrow))

    sys.stdout.write(f"\r📈 Checking proxies: [{arrow}{spaces}] {current}/{total}")
    sys.stdout.flush()


def get_proxy():
    global total_proxy

    res = requests.get(proxy_url_api, timeout=10)
    proxy_list = res.text.strip().split("\n")

    proxy_list = [p.strip() for p in proxy_list if p.strip()]
    total = len(proxy_list)

    print(f"\n🌐 Got {total} proxies\n")

    test_url = "http://httpbin.org/ip"

    for i, p in enumerate(proxy_list, start=1):

        proxy = {
            "http": f"http://{p}",
            "https": f"http://{p}"
        }

        try:
            r = requests.get(
                test_url,
                proxies=proxy,
                timeout=10
            )

            if r.status_code == 200:
                working_proxy.append(p)
            else:
                dead_proxy.append(p)

        except requests.exceptions.RequestException:
            dead_proxy.append(p)

        total_proxy += 1
        progress_bar(i, total)

    print("\n")

    print("╔══════════════════════════════════════╗")
    print("║           PROXY SCAN REPORT          ║")
    print("╠══════════════════════════════════════╣")
    print(f"║  ✔ WORKING PROXIES : {len(working_proxy):<15}║")
    print(f"║  ✖ DEAD PROXIES    : {len(dead_proxy):<15}║")
    print(f"║  ⚡ TOTAL CHECKED   : {total_proxy:<15}║")

    success_rate = (len(working_proxy) / total_proxy) * 100 if total_proxy else 0

    print("╠══════════════════════════════════════╣")
    print(f"║  📊 SUCCESS RATE   : {success_rate:.2f}%{' ' * 10}║")
    print("╚══════════════════════════════════════╝")

    return working_proxy

import zipfile

def zip_file(filename):
    zipname = "proxies.zip"

    with zipfile.ZipFile(zipname, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(filename, os.path.basename(filename))

    return zipname


def upload_file(filename):

    print("\n📦 Uploading proxy list...")

    # random bin name
    bin_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))

    upload_url = f"https://filebin.net/{bin_name}/{filename}"

    hader = {
        'User-Agent' : UserAgent().random
    }

    try:
        with open(filename, "rb") as f:
            r = requests.put(upload_url, data=f, timeout=30, headers=hader)

        if r.status_code in [200, 201]:

            download_link = upload_url + "?download=1"

            print("\n📥 Download Link")
            print("━━━━━━━━━━━━━━━━━━━━")
            print(download_link)
            print("━━━━━━━━━━━━━━━━━━━━")

        else:
            print("❌ Upload failed:", r.status_code)
            print(r.text)

    except Exception as e:
        print("Upload error:", e)



def save_proxies(proxies):

    filename = "proxies.txt"

    with open(filename, "w") as f:
        for p in proxies:
            f.write(p + "\n")

    zipfiles = zip_file(filename=filename)
    upload_file(zipfiles)

if __name__ == "__main__":
    proxy = get_proxy()
    save_proxies(proxy)

    os.remove('proxies.zip')
    os.remove("proxies.txt")
