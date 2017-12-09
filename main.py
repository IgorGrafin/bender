import telebot
import constants
from PIL import Image, ImageDraw, ImageFont
import requests
import os

bot = telebot.TeleBot(constants.token)
print(bot.get_me())
orig_path = os.path.abspath(os.curdir) + "\\assets\\bender.jpg"
fnt_path = os.path.abspath(os.curdir) + "\\assets\\DejaVuSans.ttf"
out_path = os.path.abspath(os.curdir) + "\\assets\\out.bmp"


def image_compose(price_text):
    """
    Add text to the picture using PILLOW library (PIL fork) and save it
    it is almost a copy of the example from the documentation of the Pillow lib
    """
    # text to show
    text = price_text + "$"
    # get an original image
    # orig_path = os.path.abspath(os.curdir) + "\\assets\\bender.jpg"
    # fnt_path = os.path.abspath(os.curdir) + "\\assets\\DejaVuSans.ttf"
    # out_path = os.path.abspath(os.curdir) + "\\assets\\out.bmp"
    base = Image.open(orig_path).convert('RGBA')
    # make a blank image for the text, initialized to transparent text color
    txt = Image.new('RGBA', base.size, (255, 255, 255, 0))
    # get a font
    fnt = ImageFont.truetype(fnt_path, 40)
    # get a drawing context
    d = ImageDraw.Draw(txt)
    # draw text
    # find out the offset (because eth has 3 digest, btc - 5)
    offset = txt.size[1]/2 - len(text) * 10
    d.text((offset, 20), text, font=fnt, fill=(0, 0, 0, 250))
    out = Image.alpha_composite(base, txt)
    # out.show() # display the result
    out.save(out_path)


def get_bitcoin_price():
    """
    use blockchain.info api as URL which contains json of exchange rates
    """
    url = "https://blockchain.info/ru/ticker"
    req = requests.get(url)
    # convert to json
    dic = req.json()
    # recieve last deal of the USD
    bitcoin = dic['USD']['last']
    # it's float, convert it to the string
    return str(bitcoin)


def get_ethereum_price():
    """
    use yobit.net api as URL which contains json of exchange rates
    """
    url = "https://yobit.net/api/2/eth_usd/ticker"
    req = requests.get(url)
    # convert to json
    dic = req.json()
    # recieve last deal of the eth
    ethereum = dic['ticker']['last']
    # it's float, convert it to the string and round to 2 digests
    return str(float(round(ethereum, 2)))


# telegram:


@bot.message_handler(commands=["start"])
def handle_start(message):
    bot.send_message(message.chat.id, '/btc - Bitcoin, /eth - Ethereum')


@bot.message_handler(commands=['btc'])
def handle_btc(message):
    currency = 'BTC'
    currency_rate = get_bitcoin_price()
    process(currency, currency_rate, message)


@bot.message_handler(commands=['eth'])
def handle_btc(message):
    currency = 'ETH'
    currency_rate = get_ethereum_price()
    process(currency, currency_rate, message)


def process(currency, currency_rate, message):
    # show message "sending a photo"
    bot.send_chat_action(message.chat.id, "upload_photo")
    # print(currency, currency_rate)
    # make an image with bender and price and save it
    image_compose(currency_rate)
    # open it and send back via telegram
    with open(out_path, "rb") as photo:
        bot.send_photo(message.chat.id, photo)
    bot.send_message(message.chat.id, '1 {0} = {1}$'.format(currency, currency_rate))


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
