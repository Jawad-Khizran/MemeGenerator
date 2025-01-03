# pokemon_api.s
import google.generativeai as genai
from textblob import TextBlob
import re
from PIL import Image, ImageDraw, ImageFont


class GetApi:

    def __init__(self):
        # Set your API key
        self.configure = genai.configure(api_key="AIzaSyBab5VArMDK59FsdW9hNgR3_5ASaV_tpJU")
            # Create a model instance
        self.model = genai.GenerativeModel("gemini-pro")

    def get_meme(self):

        # Send a request to the model
        flag = 1
        while flag == 1:
            response = self.model.generate_content("give me a positive joke about peace")
            cleaned_text = self.clean_text(response.text) #using the clean_text function for clean text 
            blob = TextBlob(cleaned_text) #creating blob object of the text to analayze 
            sentiment = blob.sentiment.polarity #score of -1 to 1 by how negetive to positive
            print(sentiment) #print -1 to 1 score of sentiment
            if sentiment >= 0:  
                flag = 0      
                return cleaned_text
               
    
    #removing non relevant charecters form the text
    def clean_text(self,response):
        text = re.sub(r'[^a-zA-Z0-9\s\n]', '', response)
        return text


    def create_photo(self, text, output_path):
        image = image.open("https://thumbs.dreamstime.com/b/white-stone-words-positive-attitude-smile-face-color-glitter-boke-background-positive-attitude-stone-117351582.jpg")
        draw = ImageDraw.Draw(image)
            # Set font and size
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Adjust to your font path
        font = ImageFont.truetype(font_path, size=40)

        # Define text positioning
        image_width, image_height = image.size
        text_width, text_height = draw.textsize(text, font=font)
        x = (image_width - text_width) // 2
        y = image_height - text_height - 20  # Add padding at the bottom

        # Add text to the image
        draw.text((x, y), text, font=font, fill="white", stroke_width=2, stroke_fill="black")

        # Save the resulting image
        image.save(output_path)