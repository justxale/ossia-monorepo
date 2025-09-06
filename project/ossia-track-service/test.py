from PIL import Image

img = Image.open('logo.png')
img.save('favicon.ico', 'ICO')