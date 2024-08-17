import re
import json
import time
import random
import base64
import requests
import random_strings
from datetime import datetime, timezone
from random_username.generate import generate_username
from concurrent.futures import ThreadPoolExecutor

import loguru
import modules.capbypass
import modules.mailtm as mailtm

# Input Webhook URL and number of accounts
webhook_url = input("Enter your Discord webhook URL: ").strip()
total_generate_count = int(input("How many accounts do you want to generate? ").strip())

# Load settings
with open("settings.json", "r") as f:
    settings_json = json.load(f)

class RobloxGen:
    def __init__(self):
        self.session = requests.Session()
        self.setup_headers()
        self.load_proxy()
        self.mailapi = mailtm.MailTM()
        self.setup_mail()
        self.account_passw = random_strings.random_string(12)

    def setup_headers(self):
        self.session.headers.update({
            'accept': '*/*',
            'accept-language': 'en-GB,en;q=0.9',
            'cache-control': 'no-cache',
            'origin': 'https://www.roblox.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://www.roblox.com/',
            'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        })

    def load_proxy(self):
        self.proxy = random.choice(open("proxy.txt", "r").readlines()).strip()
        self.session.proxies = {
            "http": "http://" + self.proxy,
            "https": "http://" + self.proxy,
        }

    def setup_mail(self):
        maildetails = self.mailapi.create_account(self.mailapi.get_domain())
        self.mail = maildetails["mail"]
        self.mailpassword = maildetails["password"]

    def get_csrf(self):
        response = self.session.get("https://www.roblox.com/home")
        self.csrf_token = response.text.split('"csrf-token" data-token="')[1].split('"')[0]
        self.session.headers["x-csrf-token"] = self.csrf_token

    def get_cookies(self):
        self.session.get('https://www.roblox.com/timg/rbx')
        self.session.cookies.update({"RBXcb": "RBXViralAcquisition=true&RBXSource=true&GoogleAnalytics=true"})
        params = {'name': 'ResourcePerformance_Loaded_funcaptcha_Computer', 'value': '2'}
        self.session.post('https://www.roblox.com/game/report-stats', params=params)

    def generate_birthday(self):
        return datetime(
            random.randint(1990, 2006),
            random.randint(1, 12),
            random.randint(1, 28),
            21,
            tzinfo=timezone.utc,
        ).isoformat(timespec="milliseconds").replace("+00:00", "Z")

    def verify_username(self):
        self.session.headers.update({
            "authority": "auth.roblox.com",
            "accept": "application/json, text/plain, */*"
        })
        self.birthdate = self.generate_birthday()
        nickname = generate_username(1)[0] + str(random.randint(10, 99))
        response = self.session.get(
            f"https://auth.roblox.com/v1/validators/username?Username={nickname}&Birthday={self.birthdate}"
        )
        try:
            self.nickname = random.choice(response.json()["suggestedUsernames"])
        except KeyError:
            self.nickname = nickname

    def purchase_free_items(self):
        params = {'category': 'Characters', 'minPrice': '0', 'maxPrice': '0', 'salesTypeFilter': '1', 'limit': '120'}
        response = self.session.get('https://catalog.roblox.com/v1/search/items', params=params)
        random_character = random.choice(response.json()["data"])["id"]

        for _ in range(2):  # Retry to handle purchase bugs
            self.random_character_id = self.session.get(f'https://catalog.roblox.com/v1/bundles/details?bundleIds[]={random_character}').json()[0]["product"]["id"]
            csrf_token = self.session.get(f'https://www.roblox.com/bundles/{random_character}').text.split('"csrf-token" data-token="')[1].split('"')[0]
            self.session.headers['x-csrf-token'] = csrf_token
            json_data = {'expectedPrice': 0}
            response = self.session.post(
                f'https://economy.roblox.com/v1/purchases/products/{self.random_character_id}',
                json=json_data
            )
            if response.json().get("purchased"):
                self.assetname = response.json().get('assetName')
        loguru.logger.success(f"[{self.assetname}] bundle purchased!")

    def humanize_avatar(self):
        self.purchase_free_items()
        csrftkn = self.session.get('https://www.roblox.com/my/avatar').text.split('"csrf-token" data-token="')[1].split('"')[0]
        self.session.headers.update({
            'authority': 'accountsettings.roblox.com',
            'x-csrf-token': csrftkn,
            'x-bound-auth-token': 'pro-roblox-uhq-encrypted'
        })
        for _ in range(2):  # Retry to handle avatar update bugs
            params = {'isEditable': 'false', 'itemsPerPage': '50', 'outfitType': 'Avatar'}
            response = self.session.get(f'https://avatar.roblox.com/v2/avatar/users/{self.userid}/outfits', params=params)
            outfit_id = response.json()["data"][0]["id"]
            response = self.session.get(f'https://avatar.roblox.com/v1/outfits/{outfit_id}/details')
            assets = response.json()["assets"]
            bodyscale = response.json()["scale"]
            playerAvatarType = response.json()["playerAvatarType"]
            json_data = {
                'height': int(bodyscale['height']),
                'width': int(bodyscale['width']),
                'head': int(bodyscale['head']),
                'depth': int(bodyscale['depth']),
                'proportion': int(bodyscale['proportion']),
                'bodyType': int(bodyscale['bodyType']),
            }
            self.session.post('https://avatar.roblox.com/v1/avatar/set-scales', json=json_data)
            json_data = {'assets': assets}
            self.session.post('https://avatar.roblox.com/v2/avatar/set-wearing-assets', json=json_data)
            json_data = {'playerAvatarType': playerAvatarType}
            self.session.post('https://avatar.roblox.com/v1/avatar/set-player-avatar-type', json=json_data)
        loguru.logger.success(f"[{self.mail}] avatar applied!")

        csrftkn = self.session.get(f"https://www.roblox.com/users/{self.userid}/profile").text.split('"csrf-token" data-token="')[1].split('"')[0]
        self.session.headers['x-csrf-token'] = csrftkn
        data = {'description': random.choice(open("bio.txt", "r", encoding="utf-8").readlines()).strip()}
        self.session.post('https://users.roblox.com/v1/description', data=data)
        loguru.logger.success(f"[{self.mail}] bio applied, humanization finished!")

    def signup_request(self):
        json_data = {
            "username": self.nickname,
            "password": self.account_passw,
            "birthday": self.birthdate,
            "gender": 2,
            "isTosAgreementBoxChecked": True,
            "agreementIds": [
                "adf95b84-cd26-4a2e-9960-68183ebd6393",
                "91b2d276-92ca-485f-b50d-c3952804cfd6",
            ],
            "secureAuthenticationIntent": {
                "clientPublicKey": "roblox sucks",
                "clientEpochTimestamp": str(time.time()).split(".")[0],
                "serverNonce": self.serverNonce,
                "saiSignature": "lol",
            },
        }
        return self.session.post("https://auth.roblox.com/v2/signup", json=json_data)

    def generate_account(self):
        self.session.headers["authority"] = "apis.roblox.com"
        response = self.session.get("https://apis.roblox.com/hba-service/v1/getServerNonce")
        self.serverNonce = response.text.split('"')[1]
        self.session.headers["authority"] = "auth.roblox.com"
        response = self.signup_request()

        if "Token Validation Failed" in response.text:
            self.session.headers["x-csrf-token"] = response.headers["x-csrf-token"]
            response = self.signup_request()
        if response.status_code == 429:
            loguru.logger.error("IP rate limit, retrying...")
            return ""
        
        captcha_response = json.loads(base64.b64decode(response.headers["rblx-challenge-metadata"].encode()).decode())
        unifiedCaptchaId = captcha_response["unifiedCaptchaId"]
        dataExchangeBlob = captcha_response["dataExchangeBlob"]
        genericChallengeId = captcha_response["sharedParameters"]["genericChallengeId"]

        solver = modules.capbypass.Solver(settings_json["capbypass_key"])
        captcha_solution = solver.solve(dataExchangeBlob, self.proxy)
        if not captcha_solution:
            return ""

        json_data = {
            "challengeId": genericChallengeId,
            "challengeType": "captcha",
            "challengeMetadata": json.dumps({
                "unifiedCaptchaId": genericChallengeId,
                "captchaToken": captcha_solution,
                "actionType": "Signup",
            }),
        }
        self.session.post("https://apis.roblox.com/challenge/v1/continue", json=json_data)

        self.session.headers.update({
            "rblx-challenge-id": unifiedCaptchaId,
            "rblx-challenge-type": "captcha",
            "rblx-challenge-metadata": base64.b64encode(
                json.dumps({
                    "unifiedCaptchaId": unifiedCaptchaId,
                    "captchaToken": captcha_solution,
                    "actionType": "Signup",
                }).encode()
            ).decode()
        })

        resp = self.signup_request()
        try:
            cookie = resp.cookies[".ROBLOSECURITY"]
        except KeyError:
            loguru.logger.error("Capbypass gives us wrong captcha token 😡..")
            return ""

        self.userid = resp.json()["userId"]
        loguru.logger.info(f"[https://www.roblox.com/users/{self.userid}] Account created!")

        del self.session.headers["rblx-challenge-id"]
        del self.session.headers["rblx-challenge-type"]
        del self.session.headers["rblx-challenge-metadata"]

        self.get_csrf()
        self.session.headers["authority"] = "accountsettings.roblox.com"

        json_data = {"emailAddress": self.mail}
        response = self.session.post("https://accountsettings.roblox.com/v1/email", json=json_data)
        if response.status_code == 200:
            loguru.logger.info(f"[{self.userid}] Mail set as {self.mail}")

            if settings_json["verify_mail"]:
                self.mailtoken = self.mailapi.get_account_token(self.mail, self.mailpassword)
                mail_timeout = 0
                while True:
                    mail_timeout += 1
                    time.sleep(1)
                    mailboxdetails = self.mailapi.get_mail(self.mailtoken)
                    if mailboxdetails["hydra:member"]:
                        message_id = mailboxdetails["hydra:member"][0]["id"]
                        mailcontent = self.mailapi.get_mail_content(self.mailtoken, message_id)
                        ticketid = re.search(r"http[s]*\S+", mailcontent["text"])[0].split("?ticket=")[1]
                        json_data = {"ticket": ticketid.strip()}
                        response = self.session.post("https://accountinformation.roblox.com/v1/email/verify", json=json_data)
                        loguru.logger.info(f"[{self.mail}] Mail verified and free prize claimed! - https://www.roblox.com/catalog/{response.json()['verifiedUserHatAssetId']}")
                        break
                    if mail_timeout == 30:
                        loguru.logger.error(f"[{self.mail}] Mail timeout, skipping...")
                        return ""
            else:
                loguru.logger.warning(f"[{self.mail}] Mail verification skipping...")

        else:
            loguru.logger.error(f"[{self.mail}] Can't set mail! {response.text}")

        if settings_json["humanize"]:
            self.humanize_avatar()
        else:
            loguru.logger.warning(f"[{self.mail}] Humanizing skipping...")

        loguru.logger.success(f"[{self.mail}] Account saved into txt!")
        with open("accgen.txt", "a") as f:
            f.write(f"{self.nickname}:{self.account_passw}:{self.mail}:{self.mailpassword}:{cookie}\n")

def generate():
    while True:
        try:
            gen = RobloxGen()
            gen.get_csrf()
            gen.get_cookies()
            gen.verify_username()
            gen.generate_account()
            break
        except KeyError as E:
            loguru.logger.error(f"{E}, retrying.")
            pass
        except Exception as E:
            loguru.logger.error(E)
            break

def send_to_discord(file_path):
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(webhook_url, files=files)
    if response.status_code == 204:
        loguru.logger.info("File sent to Discord successfully!")
    else:
        loguru.logger.error(f"Failed to send file to Discord. Status code: {response.status_code}")

proxy = open("proxy.txt", "r").readlines()
if not proxy:
    loguru.logger.error("proxy.txt is empty, fill it with proxies.")
    exit()

thread_count = settings_json["thread_count"]
generate_per_thread = total_generate_count / thread_count

with ThreadPoolExecutor(max_workers=thread_count) as executor:
    for _ in range(total_generate_count):
        executor.submit(generate)

send_to_discord("accgen.txt")
