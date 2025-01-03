import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

class CreateMeme:

    def __init__(self):
        # URL of the image you want to use as the background
        self.image_url = "https://thumbs.dreamstime.com/b/white-stone-words-positive-attitude-smile-face-color-glitter-boke-background-positive-attitude-stone-117351582.jpg"
        # Output path for the meme image
        self.output_path = r"C:\Users\User\Downloads\output_meme.jpg"   

    def create_photo(self, meme):
        # Download the image from URL
        text = meme
        response = requests.get(self.image_url)
        image = Image.open(BytesIO(response.content))
        
        # Prepare to draw text on the image
        draw = ImageDraw.Draw(image)
        
        # Set font and size
        font_path = "C:/Windows/Fonts/arial.ttf"  # Adjust this path to your system's font
        font_size = 40
        font = ImageFont.truetype(font_path, size=font_size)

        # Define text positioning using textbbox (corrected usage)
        bbox = draw.textbbox((0, 0), text, font=font)  # The starting position is (0, 0)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Define image dimensions
        image_width, image_height = image.size

        # Reduce font size until text fits within image
        while text_width > image_width - 40:  # 40 is padding
            font_size -= 2
            font = ImageFont.truetype(font_path, size=font_size)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        
        # Position text at the bottom center of the image
        x = (image_width - text_width) // 2
        y = image_height - text_height - 20  # Padding from the bottom

        # Add text to the image
        draw.text((x, y), text, font=font, fill="white", stroke_width=2, stroke_fill="black")

        # Save the resulting image
        image.save(self.output_path)



