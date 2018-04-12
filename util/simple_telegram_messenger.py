import urllib2


def send_telegram_message(telegram_token, chat_id, message):
    url = 'https://api.telegram.org/bot{telegram_token}/sendMessage?chat_id={chat_id}&text={message}'.format(
        **{"chat_id": chat_id, "telegram_token": telegram_token, "message": message})
    print(url)
    urllib2.urlopen(url)
    return
