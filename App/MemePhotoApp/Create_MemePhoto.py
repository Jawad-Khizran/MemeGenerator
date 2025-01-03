from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import random
import os
from pathlib import Path

class CreateMeme:

    def __init__(self):
        self.image_id = random.randint(1, 1048) # image IDs range from 1 - 1084
        # URL of the image you want to use as the background
        self.image_url = f'https://picsum.photos/id/{self.image_id}/1080/720/' 
        # Output path for the meme image
        self.output_path = self.output_path = os.path.join(str(Path.home()), "Downloads", "output_meme.jpg")

    def create_photo(self, meme_text):
        # Download the image from URL
        text = meme_text
        response = requests.get(self.image_url)
        image = Image.open(BytesIO(response.content))
        
        # Prepare to draw text on the image
        draw = ImageDraw.Draw(image)
        
        # Set font and size
        font_path = "C:/Windows/Fonts/arial.ttf"  # Adjust this path to your system's font
        font_size = 40
        text_font = ImageFont.truetype(font_path, size=font_size)

        # Define text positioning using textbbox (corrected usage)
        bbox = draw.textbbox((0, 0), text, font=text_font)  # The starting position is (0, 0)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Define image dimensions
        image_width, image_height = image.size

        # Reduce font size until text fits within image
        while text_width > image_width - 40:  # 40 is padding
            font_size -= 2
            font = ImageFont.truetype(font_path, size=font_size)
            bbox = draw.textbbox((0, 0), text, font=text_font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        
        # Position text at the bottom center of the image
        x = (image_width - text_width) // 2
        y = image_height - text_height - 20  # Padding from the bottom

        # Add text to the image
        draw.text((x, y), text, font=text_font, fill="white", stroke_width=2, stroke_fill="black")

        # Save the resulting image
        image.save(self.output_path)
