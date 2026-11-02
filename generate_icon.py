from PIL import Image, ImageDraw, ImageFont

def create_icon():
    size = (256, 256)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Outer border rounded square
    draw.rounded_rectangle([8, 8, 248, 248], radius=52, fill="#0c0c0f", outline="#d90429", width=6)

    # Inner crimson gradient box
    draw.rounded_rectangle([32, 32, 224, 224], radius=40, fill="#d90429")

    # Sleek stylized "M" / Studio symbol
    # Left pillar of M
    draw.rounded_rectangle([66, 68, 92, 188], radius=6, fill="#ffffff")
    # Right pillar of M
    draw.rounded_rectangle([164, 68, 190, 188], radius=6, fill="#ffffff")
    
    # Diagonal chevrons meeting in center
    draw.polygon([(92, 70), (128, 134), (112, 134), (76, 70)], fill="#ffffff")
    draw.polygon([(164, 70), (128, 134), (144, 134), (180, 70)], fill="#ffffff")

    # Center video play badge (triangle in dark)
    draw.polygon([(118, 146), (144, 160), (118, 174)], fill="#ffffff")

    # Save as .ico
    img.save("app_icon.ico", format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print("MerVid Studio icon generated successfully!")

if __name__ == '__main__':
    create_icon()
