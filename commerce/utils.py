import qrcode

data = 'https://github.com/cyrax-1028/'

img = qrcode.make(data)

img.save('C:/Users/user/PycharmProjects/Alibaba/commerce/static/images/GitHUb.png')