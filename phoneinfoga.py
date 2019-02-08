#!/usr/bin/env python3

__version__ = 'v1.0.0'

try:
    import sys
    from colorama import Fore, Style
    import atexit
    import argparse
    import random
except KeyboardInterrupt:
    print('[!] Çıkılması.')
    sys.exit()
except:
    print('[!] Eksik gereksinimler. Python3 -m pip install -r requirements.txt kurulumunu çalıştırmayı deneyin')
    sys.exit()


def banner():
    print(" AYYILDIZ.ORG - YUNUSEMRE_")
    print("Programi asla kotu amacla kullanmayiniz.")
    print("AYYILDIZ.ORG ICIN YAPILMISTIR.")
    print("forum.ayyildiz.org")
    print(" ayyildiz.org ver. {}".format(__version__))
    print(" Coded by yunusemre_")
    print("\n")


banner()

if sys.version_info[0] < 3:
    print("\033[1m\033[93m(!) Lutfen araci Python 3 kullanarak calistirin" + Style.RESET_ALL)
    sys.exit()

parser = argparse.ArgumentParser(description="Telefon numaraları için gelişmiş bilgi toplama aracı (https://github.com/croxamca0/telefonbilgi) version {}".format(__version__),
                                 usage='%(prog)s -n <number> [options]')

parser.add_argument('-n', '--number', metavar='number', type=str,
                    help='Taranacak telefon numarası (E164 veya uluslararası format)')

parser.add_argument('-i', '--input', metavar="input_file", type=argparse.FileType('r'),
                    help='Taranacak telefon numarası listesi (her satıra bir tane)')

parser.add_argument('-o', '--output', metavar="output_file", type=argparse.FileType('w'),
                    help='Tarama sonuçlarını kaydetmek için çıktı')

parser.add_argument('-s', '--scanner', metavar="scanner", default="all", type=str,
                    help='Kullanılacak tarayıcı')

parser.add_argument('--osint', action='store_true',
                    help='OSINT kesif kullan')

parser.add_argument('-u', '--update', action='store_true',
                    help='Projeyi güncelle')

parser.add_argument('--no-ansi', action='store_true',
                    help='Renkli çıktıyı devre dışı bırak')

args = parser.parse_args()


def resetColors():
    if not args.output:
        print(Style.RESET_ALL)


# Reset text color at exit
atexit.register(resetColors)

# If any param is passed, execute help command
if not len(sys.argv) > 1:
    parser.print_help()
    sys.exit()

try:
    import time
    import hashlib
    import json
    import re
    import requests
    import urllib3
    from bs4 import BeautifulSoup
    import html5lib
    import phonenumbers
    from phonenumbers import carrier
    from phonenumbers import geocoder
    from phonenumbers import timezone
    from urllib.parse import urlencode
except KeyboardInterrupt:
    print('\033[91m[!] Çıkılması.')
    sys.exit()
except:
    print('\033[91m[!] Eksik gereksinimler. Python3 -m pip install -r requirements.txt dosyasını çalıştırmayı deneyin')
    sys.exit()

requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'
try:
    requests.packages.urllib3.contrib.pyopenssl.DEFAULT_SSL_CIPHER_LIST += 'HIGH:!DH:!aNULL'
except AttributeError:
    # no pyopenssl support used / needed / available
    pass

if args.update:
    def download_file(url, target_path):
        response = requests.get(url, stream=True)
        handle = open(target_path, "wb")
        for chunk in response.iter_content(chunk_size=512):
            if chunk:  # filter out keep-alive new chunks
                handle.write(chunk)

    print('Tlfnbilgi güncelleniyor ...')
    print('Gerçek sürüm: {}'.format(__version__))

    # Fetching last github tag
    new_version = json.loads(requests.get(
        'https://api.github.com/repos/sundowndev/PhoneInfoga/tags').content)[0]['name']
    print('Last version: {}'.format(new_version))

    osintFiles = [
        'disposable_num_providers.json',
        'individuals.json',
        'reputation.json',
        'social_medias.json'
    ]

    try:
        print('[*] Updating OSINT files')

        for file in osintFiles:
            url = 'https://github.com/croxamca0/telefonbilgi'.format(
                file)
            output_directory = 'osint/{}'.format(file)
            download_file(url, output_directory)

        print('[*] Updating python script')

        url = 'https://github.com/croxamca0/telefonbilgi'
        output_directory = 'phoneinfoga.py'
        download_file(url, output_directory)
    except:
        print('Update failed. Try using git pull.')
        sys.exit()

    print('The tool was successfully updated.')
    sys.exit()

scanners = ['any', 'all', 'numverify', 'ovh']

uagent = []
uagent.append("Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0) Opera 12.14")
uagent.append(
    "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:26.0) Gecko/20100101 Firefox/26.0")
uagent.append(
    "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.3) Gecko/20090913 Firefox/3.5.3")
uagent.append(
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3 (.NET CLR 3.5.30729)")
uagent.append("Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.7 (KHTML, like Gecko) Comodo_Dragon/16.1.1.0 Chrome/16.0.912.63 Safari/535.7")
uagent.append(
    "Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3 (.NET CLR 3.5.30729)")
uagent.append(
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.1) Gecko/20090718 Firefox/3.5.1")
uagent.append(
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0")

number = ''  # Full number format; e.g: 3312345678
localNumber = ''  # Local number format; e.g: 06 12 34 56 78
internationalNumber = ''  # International number format; e.g: +33 6 12 34 56 78
numberCountryCode = ''  # Dial code; e.g: 33
numberCountry = ''  # Country; e.g: fr

googleAbuseToken = ''
customFormatting = ''


def search(req, stop):
    global googleAbuseToken
    global uagent

    chosenUserAgent = random.choice(uagent)

    s = requests.Session()
    headers = {
        'User-Agent': chosenUserAgent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-us,en;q=0.5',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
        'Keep-Alive': '115',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache',
        'Cookie': 'Cookie: CGIC=Ij90ZXh0L2h0bWwsYXBwbGljYXRpb24veGh0bWwreG1sLGFwcGxpY2F0aW9uL3htbDtxPTAuOSwqLyo7cT0wLjg; CONSENT=YES+RE.fr+20150809-08-0; 1P_JAR=2018-11-28-14; NID=148=aSdSHJz71rufCokaUC93nH3H7lOb8E7BNezDWV-PyyiHTXqWK5Y5hsvj7IAzhZAK04-QNTXjYoLXVu_eiAJkiE46DlNn6JjjgCtY-7Fr0I4JaH-PZRb7WFgSTjiFqh0fw2cCWyN69DeP92dzMd572tQW2Z1gPwno3xuPrYC1T64wOud1DjZDhVAZkpk6UkBrU0PBcnLWL7YdL6IbEaCQlAI9BwaxoH_eywPVyS9V; SID=uAYeu3gT23GCz-ktdGInQuOSf-5SSzl3Plw11-CwsEYY0mqJLSiv7tFKeRpB_5iz8SH5lg.; HSID=AZmH_ctAfs0XbWOCJ; SSID=A0PcRJSylWIxJYTq_; APISID=HHB2bKfJ-2ZUL5-R/Ac0GK3qtM8EHkloNw; SAPISID=wQoxetHBpyo4pJKE/A2P6DUM9zGnStpIVt; SIDCC=ABtHo-EhFAa2AJrJIUgRGtRooWyVK0bAwiQ4UgDmKamfe88xOYBXM47FoL5oZaTxR3H-eOp7-rE; OTZ=4671861_52_52_123900_48_436380; OGPC=873035776-8:; OGP=-873035776:;'
    }

    try:
        REQ = urlencode({'q': req})
        URL = 'https://www.google.com/search?tbs=li:1&{}&amp;gws_rd=ssl'.format(
            REQ)
        r = s.get(URL + googleAbuseToken, headers=headers)

        while r.status_code == 503:
            print(code_warning + 'You are temporary blacklisted from Google search. Complete the captcha at the following URL and copy/paste the content of GOOGLE_ABUSE_EXEMPTION cookie : {}'.format(URL))
            print('\n' + code_info +
                  'Need help ? Read https://github.com/sundowndev/PhoneInfoga/wiki')
            token = input('\nGOOGLE_ABUSE_EXEMPTION=')
            googleAbuseToken = '&google_abuse=' + token
            r = s.get(URL + googleAbuseToken, headers=headers)

        soup = BeautifulSoup(r.content, 'html.parser')
        results = soup.find("div", id="search").find_all("div", class_="g")

        links = []
        counter = 0

        for result in results:
            counter += 1

            if int(counter) > int(stop):
                break

            url = result.find("a").get('href')
            url = re.sub(r'(?:\/url\?q\=)', '', url)
            url = re.sub(r'(?:\/url\?url\=)', '', url)
            url = re.sub(r'(?:\&sa\=)(?:.*)', '', url)
            url = re.sub(r'(?:\&rct\=)(?:.*)', '', url)

            if re.match(r"^(?:\/search\?q\=)", url) is not None:
                url = 'https://google.com' + url

            links.append(url)

        return links
    except:
        print(code_error + 'İstek başarısız oldu. Lütfen bir sorunu tekrar deneyin veya açın https://github.com/croxamca0/telefonbilgi')


def formatNumber(InputNumber):
    return re.sub("(?:\+)?(?:[^[0-9]*)", "", InputNumber)


def localScan(InputNumber):
    global number
    global localNumber
    global internationalNumber
    global numberCountryCode
    global numberCountry

    print(code_info + 'Running local scan...')

    FormattedPhoneNumber = "+" + formatNumber(InputNumber)

    try:
        PhoneNumberObject = phonenumbers.parse(FormattedPhoneNumber, None)
    except:
        return False
    else:
        if not phonenumbers.is_valid_number(PhoneNumberObject):
            return False

        number = phonenumbers.format_number(
            PhoneNumberObject, phonenumbers.PhoneNumberFormat.E164).replace('+', '')
        numberCountryCode = phonenumbers.format_number(
            PhoneNumberObject, phonenumbers.PhoneNumberFormat.INTERNATIONAL).split(' ')[0]

        try:
            countries = json.load(open('data/CountryCodes.json'))

            for country in countries:
                if (country['dial_code'].replace(' ', '') == numberCountryCode):
                    print(code_info + 'Country code found: {} ({})'.format(country['name'],country['code']))
                    numberCountry = country['code']
                    break
        except:
            print(code_error + 'Unable to find country code.')
            print(numberCountry)

        localNumber = phonenumbers.format_number(
            PhoneNumberObject, phonenumbers.PhoneNumberFormat.E164).replace(numberCountryCode, '')
        internationalNumber = phonenumbers.format_number(
            PhoneNumberObject, phonenumbers.PhoneNumberFormat.INTERNATIONAL)

        print(code_result + 'International format: {}'.format(internationalNumber))
        print(code_result + 'Local format: 0{}'.format(localNumber))
        print(code_result + 'Country code: {}'.format(numberCountryCode))
        print(code_result + 'Location: {}'.format(geocoder.description_for_number(PhoneNumberObject, "en")))
        print(code_result +
              'Carrier: {}'.format(carrier.name_for_number(PhoneNumberObject, 'en')))
        print(code_result + 'Area: {}'.format(geocoder.description_for_number(PhoneNumberObject, 'en')))
        for timezoneResult in timezone.time_zones_for_number(PhoneNumberObject):
            print(code_result + 'Timezone: {}'.format(timezoneResult))

        if phonenumbers.is_possible_number(PhoneNumberObject):
            print(code_info + 'The number is valid and possible.')
        else:
            print(code_warning + 'Bu numara geçerlidir ancak mümkün olmayabilir.')


def numverifyScan():
    global number

    if not args.scanner == 'numverify' and not args.scanner == 'all':
        return -1

    print(code_info + 'ayyildiz tim taramasi baslatiliyor...')

    requestSecret = ''
    resp = requests.get('https://numverify.com/')
    soup = BeautifulSoup(resp.text, "html5lib")
    for tag in soup.find_all("input", type="hidden"):
        if tag['name'] == "scl_request_secret":
            requestSecret = tag['value']
            break

    apiKey = hashlib.md5((number + requestSecret).encode('utf-8')).hexdigest()

    headers = {
        'Host': 'numverify.com',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:64.0) Gecko/20100101 Firefox/64.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://numverify.com/',
        'X-Requested-With': 'XMLHttpRequest',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'
    }

    try:
        response = requests.request(
            "GET", "https://numverify.com/php_helper_scripts/phone_api.php?secret_key={}&number={}".format(apiKey, number), data="", headers=headers)

        data = json.loads(response.content.decode('utf-8'))
    except:
        print(code_error + 'Numverify is not available')
        return -1

    if response.content == "Unauthorized" or response.status_code != 200:
        print((code_error + "API çağrılırken bir hata oluştu (hatalı istek veya yanlış api anahtarı)."))
        return -1

    if data["valid"] == False:
        print((code_error + "Hata: Lütfen geçerli bir telefon numarası belirtin. Örnek: +6464806649"))
        sys.exit()

    InternationalNumber = '({}){}'.format(
        data["country_prefix"], data["local_format"])

    print((code_result +
           "Number: ({}) {}").format(data["country_prefix"], data["local_format"]))
    print((code_result +
           "Country: {} ({})").format(data["country_name"], data["country_code"]))
    print((code_result + "Location: {}").format(data["location"]))
    print((code_result + "Carrier: {}").format(data["carrier"]))
    print((code_result + "Line type: {}").format(data["line_type"]))

    if data["line_type"] == 'landline':
        print((code_warning + "Bu büyük olasılıkla bir sabit hat, ancak yine de sabit bir VoIP numarası olabilir."))
    elif data["line_type"] == 'mobile':
        print((code_warning + "Bu büyük olasılıkla bir cep telefonu numarası, ancak yine de bir VoIP numarası olabilir."))


def ovhScan():
    global localNumber
    global numberCountry

    if not args.scanner == 'ovh' and not args.scanner == 'all':
        return -1

    print(code_info + 'OVH taraması çalıştırılıyor ...')

    querystring = {"country": numberCountry.lower()}

    headers = {
        'accept': "application/json",
        'cache-control': "no-cache"
    }

    try:
        response = requests.request(
            "GET", "https://api.ovh.com/1.0/telephony/number/detailedZones", data="", headers=headers, params=querystring)
        data = json.loads(response.content.decode('utf-8'))
    except:
        print(code_error + 'OVH API^sine erişilemiyor. Belki daha sonra tekrar deneyin.')
        return -1

    if isinstance(data, list):
        askedNumber = "0" + localNumber.replace(localNumber[-4:], 'xxxx')

        for voip_number in data:
            if voip_number['number'] == askedNumber:
                print((code_info + "OVH veritabanında 1 sonuç bulundu."))
                print(
                    (code_result + "Sayı aralığı: {}".format(voip_number['number'])))
                print((code_result + "Kent: {}".format(voip_number['city'])))
                print((code_result + "Posta kodu: {}".format(
                    voip_number['zipCode'] if voip_number['zipCode'] is not None else '')))
                askForExit()


def replaceVariables(string):
    global number
    global internationalNumber
    global localNumber

    string = string.replace('$n', number)
    string = string.replace('$i', internationalNumber)
    string = string.replace('$l', localNumber)

    return string


def osintIndividualScan():
    global number
    global internationalNumber
    global numberCountryCode
    global customFormatting

    dorks = json.load(open('osint/individuals.json'))

    for dork in dorks:
        if dork['dialCode'] is None or dork['dialCode'] == numberCountryCode:
            if customFormatting:
                dorkRequest = replaceVariables(
                    dork['request']) + ' | intext:"{}"'.format(customFormatting)
            else:
                dorkRequest = replaceVariables(dork['request'])

            print(
                (code_info + "Üzerinde ayak izleri aranıyor {}...".format(dork['site'])))
            for result in search(dorkRequest, stop=dork['stop']):
                if result:
                    print((code_result + "URL: " + result))
        else:
            return -1


def osintReputationScan():
    global number
    global internationalNumber
    global customFormatting

    dorks = json.load(open('osint/reputation.json'))

    for dork in dorks:
        if customFormatting:
            dorkRequest = replaceVariables(
                dork['request']) + ' | intext:"{}"'.format(customFormatting)
        else:
            dorkRequest = replaceVariables(dork['request'])

        print((code_info + "Searching for {}...".format(dork['title'])))
        for result in search(dorkRequest, stop=dork['stop']):
            if result:
                print((code_result + "URL: " + result))


def osintSocialMediaScan():
    global number
    global internationalNumber
    global customFormatting

    dorks = json.load(open('osint/social_medias.json'))

    for dork in dorks:
        if customFormatting:
            dorkRequest = replaceVariables(
                dork['request']) + ' | intext:"{}"'.format(customFormatting)
        else:
            dorkRequest = replaceVariables(dork['request'])

        print(
            (code_info + "Üzerinde ayak izleri aranıyor {}...".format(dork['site'])))
        for result in search(dorkRequest, stop=dork['stop']):
            if result:
                print((code_result + "URL: " + result))


def osintDisposableNumScan():
    global number

    dorks = json.load(open('osint/disposable_num_providers.json'))

    for dork in dorks:
        dorkRequest = replaceVariables(dork['request'])

        print(
            (code_info + "Üzerinde ayak izleri aranıyor {}...".format(dork['site'])))
        for result in search(dorkRequest, stop=dork['stop']):
            if result:
                print((code_result + "Sonuç bulundu: {}".format(dork['site'])))
                print((code_result + "URL: " + result))
                askForExit()


def osintScan():
    global number
    global localNumber
    global internationalNumber
    global numberCountryCode
    global customFormatting

    if not args.osint:
        return -1

    print(code_info + 'OSINT ayak izi kesif çalıştırılıyor ...')

    # Whitepages
    print((code_info + "tarama URL'si oluşturuluyor ..."))
    print(code_result + "Scan URL: https://www.411.com/phone/{}".format(
        internationalNumber.replace('+', '').replace(' ', '-')))

    askingCustomPayload = input(
        code_info + 'Bu numara için ek bir format kullanmak ister misiniz? (y/N) ')

    if askingCustomPayload == 'y' or askingCustomPayload == 'yes':
        customFormatting = input(code_info + 'Custom format: ')

    print((code_info + '---- Web sayfaları ayak izleri ----'))

    print((code_info + "Web sayfalarında ayak izleri aranıyor ... (limit=5)"))
    if customFormatting:
        req = '{} | intext:"{}" | intext:"{}" | intext:"{}"'.format(
            number, number, internationalNumber, customFormatting)
    else:
        req = '{} | intext:"{}" | intext:"{}"'.format(
            number, number, internationalNumber)
    for result in search(req, stop=5):
        if result:
            print((code_result + "Sonuç bulundu: " + result))

    # Documents
    print((code_info + "Belge aranıyor ... (limit=10)"))
    if customFormatting:
        req = '[ext:doc | ext:docx | ext:odt | ext:pdf | ext:rtf | ext:sxw | ext:psw | ext:ppt | ext:pptx | ext:pps | ext:csv | ext:txt | ext:xls] && [intext:"{}"]'.format(
            customFormatting)
    else:
        req = '[ext:doc | ext:docx | ext:odt | ext:pdf | ext:rtf | ext:sxw | ext:psw | ext:ppt | ext:pptx | ext:pps | ext:csv | ext:txt | ext:xls] && [intext:"{}" | intext:"{}"]'.format(
            internationalNumber, localNumber)
    for result in search(req, stop=10):
        if result:
            print((code_result + "Sonuç bulundu: " + result))

    print((code_info + '---- İtibar ayak izleri ----'))

    osintReputationScan()

    print((code_info + "URL oluşturuluyor ..."))
    print(code_result +
          'http://www.scamcallfighters.com/search-phone-{}.html'.format(number))

    tmpNumAsk = input(
        code_info + "Geçici numara sağlayıcıların ayak izlerini aramak ister misiniz? (Y/n) ")

    if tmpNumAsk.lower() != 'n' and tmpNumAsk.lower() != 'no':
        print((code_info + '---- Geçici numara sağlayıcıların ayak izleri ----'))

        try:
            print((code_info + "telefon numarası aranıyor ..."))
            response = requests.request(
                "GET", "https://tempophone.com/api/v1/phones")
            data = json.loads(response.content.decode('utf-8'))
            for voip_number in data['objects']:
                if voip_number['phone'] == formatNumber(number):
                    print(
                        (code_result + "Geçici bir numara sağlayıcı bulundu."))
                    askForExit()
        except:
            print((code_error + "API'sine ulaşılamıyor. Atlama."))

        osintDisposableNumScan()

    print((code_info + '---- Sosyal medya ayak izleri ----'))

    osintSocialMediaScan()

    print((code_info + '---- Telefon rehberleri ayak izleri ----'))

    if numberCountryCode == '+1':
        print((code_info + "Gerçek Kişilerde URL Üretiliyor ... "))
        print(code_result + 'https://www.truepeoplesearch.com/results?phoneno={}'.format(
            internationalNumber.replace(' ', '')))

    osintIndividualScan()

    retry_input = input(
        code_info + "OSINT taramasını tekrar başlatmak ister misiniz? (örneğin farklı bir format kullanmak için) (y/N) ")

    if retry_input.lower() == 'y' or retry_input.lower() == 'yes':
        osintScan()
    else:
        return -1


def askForExit():
    if not args.output:
        user_input = input(code_info + "Taramaya devam et. (y/N) ")

        if user_input.lower() == 'y' or user_input.lower() == 'yes':
            return -1
        else:
            print(code_info + "Güle güle!")
            sys.exit()


def scanNumber(InputNumber):
    print(code_title +
          "[!] ---- İçin bilgi alınıyor {} ---- [!]".format(formatNumber(InputNumber)))

    localScan(InputNumber)

    global number
    global localNumber
    global internationalNumber
    global numberCountryCode
    global numberCountry

    if not number:
        print((code_error + "Error: numara {} geçerli değil. Atlama.".format(formatNumber(InputNumber))))
        sys.exit()

    numverifyScan()
    ovhScan()
    osintScan()

    print(code_info + "Scan finished.")

    if not args.no_ansi and not args.output:
        print('\n' + Style.RESET_ALL)
    else:
        print('\n')


try:
    if args.no_ansi or args.output:
        code_info = '[*] '
        code_warning = '(!) '
        code_result = '[+] '
        code_error = '[!] '
        code_title = ''
    else:
        code_info = Fore.RESET + Style.BRIGHT + '[*] '
        code_warning = Fore.YELLOW + Style.BRIGHT + '(!) '
        code_result = Fore.GREEN + Style.BRIGHT + '[+] '
        code_error = Fore.RED + Style.BRIGHT + '[!] '
        code_title = Fore.YELLOW + Style.BRIGHT

    if args.output:
        if args.osint:
            print(
                '\033[91m[!] OSINT tarayıcı, çıkış seçeneği kullanılamıyor (üzgünüm).')
            sys.exit()

        sys.stdout = args.output
        banner()

    # Verify scanner option
    if not args.scanner in scanners:
        print((code_error + "Error: tarayıcı mevcut değil."))
        sys.exit()

    if args.number:
        scanNumber(args.number)
    elif args.input:
        for line in args.input.readlines():
            scanNumber(line)

    if args.output:
        args.output.close()
except KeyboardInterrupt:
    print(("\n" + code_error + "Tarama yarıda kesildi. Güle güle!!"))
    sys.exit()
