import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

i = 0
while True:
    font = PIL.ImageFont.truetype("C:\\Windows\\Fonts\\Arial.ttf", 12)
    image = PIL.Image.new("RGBA", (10, 10))
    draw = PIL.ImageDraw.Draw(image)
    if i % 100 == 0:
        print(i)

    i += 1
    # print(draw.multiline_textsize("Sample", font=font))