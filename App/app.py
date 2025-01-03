import requests
from flask import Flask, request, jsonify, render_template, redirect, url_for
from PIL import Image, ImageDraw, ImageFont
import boto3
import os
from datetime import datetime
from flask import Flask, request, redirect, url_for
# from MongoDB.s3_utilities import S3Utilities
from MongoDB_and_S3.S3_MongoDB_jokemanager import S3AndMongoDBJokeManager
# from S3_MongoDB_jokemanager import S3AndMongoDBJokeManager
from GeminiApiApp.Gemini_GetApi_Class import GetApi


app = Flask(__name__)

# הגדרות S3
BUCKET_NAME = "my-jokes-bucket"
mongo_uri =  os.getenv('MONGO_URI')#, 'mongodb://localhost:27017/') #'mongodb://localhost:27017'  # MongoDB local connection URI
db_name = 'jokes_db'

# bucket_name = os.getenv("BUCKET_NAME", "my-jokes-bucket")
# mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
# db_name = os.getenv("DB_NAME", "blessings_db")

s3_client = boto3.client('s3')
manager = S3AndMongoDBJokeManager(BUCKET_NAME, mongo_uri, db_name)


# bucket_name = 'my-jokes-bucket'
# mongo_uri = 'mongodb://localhost:27017'  # MongoDB local connection URI
# db_name = 'blessings_db'

# Create a Blessing Manager instance
# manager = S3BlessingManager(bucket_name, mongo_uri, db_name)

# Create the S3 bucket if it does not exist
manager.create_bucket()


def create_gradient_background(img, color1, color2):
    """
    יוצר רקע עם מעבר צבעים (Gradient).
    """
    width, height = img.size
    draw = ImageDraw.Draw(img)
    for i in range(height):
        r = int(color1[0] + (color2[0] - color1[0]) * (i / height))
        g = int(color1[1] + (color2[1] - color1[1]) * (i / height))
        b = int(color1[2] + (color2[2] - color1[2]) * (i / height))
        draw.line([(0, i), (width, i)], fill=(r, g, b))



def split_text_into_lines(text, font, max_width):
    """
    פונקציה לחתוך טקסט לשורות שיתאימו לרוחב המקסימלי.
    """
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        # בודק את רוחב השורה הנוכחית עם המילה הנוספת
        test_line = ' '.join(current_line + [word])
        bbox = font.getbbox(test_line)
        width = bbox[2] - bbox[0]  # חישוב הרוחב מתוך ה-bbox
        if width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))
    return lines


def create_joke_image(message, sentiment, output_path):
    # יצירת תמונה
    img = Image.new('RGB', (800, 400), color=(255, 255, 255))

    # קביעת רקע עם Gradient
    if sentiment >= 0:
        create_gradient_background(img, (173, 216, 230), (135, 206, 250))  # תכלת בהיר לכחול
    else:
        create_gradient_background(img, (255, 182, 193), (255, 105, 180))  # ורוד בהיר לורוד כהה

    draw = ImageDraw.Draw(img)

    # קביעת גופנים
    font_path = "arial.ttf"  # ודא שהקובץ קיים בתיקיית הפרויקט שלך
    try:
        title_font = ImageFont.truetype(font_path, size=50)
        text_font = ImageFont.truetype(font_path, size=28)
        sentiment_font = ImageFont.truetype(font_path, size=24)
    except IOError:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        sentiment_font = ImageFont.load_default()

    # כותרת
    title_text = "GEMINI Joke:"
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width, title_height = title_bbox[2] - title_bbox[0], title_bbox[3] - title_bbox[1]
    title_x = (img.width - title_width) // 2

    # טקסט הברכה
    max_width = img.width - 40
    lines = split_text_into_lines(message, text_font, max_width)
    text_height = sum(text_font.getbbox(line)[3] - text_font.getbbox(line)[1] + 10 for line in lines) - 10

    # חישוב גובה של סנטימנט
    sentiment_text = f"Sentiment: {'Positive' if sentiment >= 0 else 'Negative'}"
    sentiment_bbox = draw.textbbox((0, 0), sentiment_text, font=sentiment_font)
    sentiment_width, sentiment_height = sentiment_bbox[2] - sentiment_bbox[0], sentiment_bbox[3] - sentiment_bbox[1]

    # חישוב המיקום ההתחלתי של הטקסט כך שיתפוס מקום נכון
    total_height = title_height + text_height + sentiment_height + 40  # 40 זה רווח נוסף
    start_y = (img.height - total_height) // 2

    # מיקום הכותרת
    title_y = start_y
    draw.text((title_x, title_y), title_text, fill="black", font=title_font)

    # מיקום הטקסט
    y_offset = title_y + title_height + 20
    for line in lines:
        line_bbox = draw.textbbox((0, 0), line, font=text_font)
        line_width, line_height = line_bbox[2] - line_bbox[0], line_bbox[3] - line_bbox[1]
        x_offset = (img.width - line_width) // 2
        draw.text((x_offset, y_offset), line, fill="black", font=text_font)
        y_offset += line_height + 10

    # מיקום ה-Sentiment
    sentiment_x = (img.width - sentiment_width) // 2
    sentiment_y = y_offset + 20
    sentiment_color = "green" if sentiment >= 0 else "red"
    draw.text((sentiment_x, sentiment_y), sentiment_text, fill=sentiment_color, font=sentiment_font)

    # הוספת מסגרת
    border_color = "black"
    border_width = 5
    draw.rectangle(
        [border_width // 2, border_width // 2, img.width - border_width // 2, img.height - border_width // 2],
        outline=border_color,
        width=border_width
    )

    # שמירת התמונה
    img.save(output_path)
    print(f"Image saved to {output_path}")

# def split_text_into_lines(text, font, max_width):
#     """
#     פונקציה לחתוך טקסט לשורות שיתאימו לרוחב המקסימלי.
#     """
#     words = text.split()
#     lines = []
#     current_line = []
#     for word in words:
#         # בודק את רוחב השורה הנוכחית עם המילה הנוספת
#         test_line = ' '.join(current_line + [word])
#         bbox = font.getbbox(test_line)
#         width = bbox[2] - bbox[0]  # חישוב הרוחב מתוך ה-bbox
#         if width <= max_width:
#             current_line.append(word)
#         else:
#             if current_line:
#                 lines.append(' '.join(current_line))
#             current_line = [word]
#     if current_line:
#         lines.append(' '.join(current_line))
#     return lines
#
#
# def create_blessing_image(message, sentiment, output_path):
#     # יצירת תמונה
#     img = Image.new('RGB', (800, 400), color=(255, 255, 255))
#
#     # קביעת רקע עם Gradient
#     if sentiment >= 0:
#         create_gradient_background(img, (173, 216, 230), (135, 206, 250))  # תכלת בהיר לכחול
#     else:
#         create_gradient_background(img, (255, 182, 193), (255, 105, 180))  # ורוד בהיר לורוד כהה
#
#     draw = ImageDraw.Draw(img)
#
#     # קביעת גופנים
#     font_path = "arial.ttf"  # ודא שהקובץ קיים בתיקיית הפרויקט שלך
#     try:
#         title_font = ImageFont.truetype(font_path, size=50)
#         text_font = ImageFont.truetype(font_path, size=28)
#         sentiment_font = ImageFont.truetype(font_path, size=24)
#     except IOError:
#         title_font = ImageFont.load_default()
#         text_font = ImageFont.load_default()
#         sentiment_font = ImageFont.load_default()
#
#     # כותרת
#     title_text = "GEMINI Blessing:"
#     title_width, title_height = draw.textsize(title_text, font=title_font)
#     title_x = (img.width - title_width) // 2
#     # title_y = 20
#     # draw.text((title_x, title_y), title_text, fill="black", font=title_font)
#
#     # טקסט הברכה
#     max_width = img.width - 40
#     lines = split_text_into_lines(message, text_font, max_width)
#     text_height = sum(text_font.getsize(line)[1] + 10 for line in lines) - 10
#
#     # חישוב גובה של סנטימנט
#     sentiment_text = f"Sentiment: {'Positive' if sentiment >= 0 else 'Negative'}"
#     sentiment_width, sentiment_height = draw.textsize(sentiment_text, font=sentiment_font)
#
#     # חישוב המיקום ההתחלתי של הטקסט כך שיתפוס מקום נכון
#     total_height = title_height + text_height + sentiment_height + 40  # 40 זה רווח נוסף
#     start_y = (img.height - total_height) // 2
#
#     # מיקום הכותרת
#     title_y = start_y
#     draw.text((title_x, title_y), title_text, fill="black", font=title_font)
#
#     # מיקום הטקסט
#     y_offset = title_y + title_height + 20
#     for line in lines:
#         line_width, line_height = draw.textsize(line, font=text_font)
#         x_offset = (img.width - line_width) // 2
#         draw.text((x_offset, y_offset), line, fill="black", font=text_font)
#         y_offset += line_height + 10
#
#     # מיקום ה-Sentiment
#     sentiment_x = (img.width - sentiment_width) // 2
#     sentiment_y = y_offset + 20
#     sentiment_color = "green" if sentiment >= 0 else "red"
#     draw.text((sentiment_x, sentiment_y), sentiment_text, fill=sentiment_color, font=sentiment_font)
#
#     # הוספת מסגרת
#     border_color = "black"
#     border_width = 5
#     draw.rectangle(
#         [border_width // 2, border_width // 2, img.width - border_width // 2, img.height - border_width // 2],
#         outline=border_color,
#         width=border_width
#     )
#
#     # שמירת התמונה
#     img.save(output_path)
#     print(f"Image saved to {output_path}")


# פונקציה להעלאת קובץ ל-S3
def upload_to_s3(file_path, object_key):
    try:
        # בדוק אם הקובץ קיים
        if not os.path.exists(file_path):
            print(f"File {file_path} does not exist.")
            return None

        # העלאת הקובץ לבאקט, ללא ACL ציבורי
        s3_client.upload_file(file_path, BUCKET_NAME, object_key)


        # השגת המיקום של ה-S3 כדי ליצור את ה-URL
        location = s3_client.get_bucket_location(Bucket=BUCKET_NAME)["LocationConstraint"]
        if location is None:
            location = "us-east-1"

        return f"https://{BUCKET_NAME}.s3.{location}.amazonaws.com/{object_key}"
    except Exception as e:
        print(f"Error uploading file: {e}")
        return None

# פונקציה להפיק URL חתום מראש לגישה מוגבלת בזמן
def generate_presigned_url(object_key, expiration=3600):
    try:
        # יצירת URL חתום מראש שיתפוס את האובייקט
        url = s3_client.generate_presigned_url('get_object',
                                               Params={'Bucket': BUCKET_NAME, 'Key': object_key},
                                               ExpiresIn=expiration)
        return url
    except Exception as e:
        print(f"Error generating pre-signed URL: {e}")
        return None

def generate_response(success, message, data=None):
    return jsonify({"success": success, "message": message, "data": data}), (200 if success else 500)

# פונקציה לוודא שספריית ברכות קיימת
def ensure_jokes_directory_exists():
    if not os.path.exists('jokes'):
        os.makedirs('jokes')

def call_gemini_api():
    response = requests.get("http://<EC2_IP_ADDRESS>:5000/api")
    if response.status_code == 200:
        data = response.json()
        print(data)
        return data.get("message"), data.get("sentiment")
    else:
        print("Failed to connect to the Gemini API")
        return None, None


@app.route("/generate-joke", methods=["POST"])
def generate_joke():
    joke = GetApi()
    try:
        # joke_text, sentiment = call_gemini_api()

        joke_text, sentiment = joke.get_meme()  # worked well


    except ValueError as e:
        # Handle the error gracefully, maybe fallback to a default message
        print(f"Error generating joke: {e}")


    # blessing_text, sentiment = blessing.get_meme() #"Some predefined blessing"  # תוכל לקבל את הברכה מהמשתמש אם תבחר
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')
    image_filename = f"joke_{timestamp}.png"
    file_path = f"jokes/{image_filename}"

    # יצירת תיקיית jokes אם היא לא קיימת
    ensure_jokes_directory_exists()

    # צור את התמונה
    try:
        create_joke_image(joke_text, sentiment, file_path)
    except Exception as e:
        return jsonify({"error": f"Failed to create joke image: {str(e)}"}), 500

    # העלה ל-S3
    s3_key = f"jokes/joke_{timestamp}.png"
    try:
        image_url = upload_to_s3(file_path, s3_key)
        if image_url:
            presigned_url = generate_presigned_url(s3_key)
            if presigned_url:
                try:

                    # שמירה ב- MongoDB
                    manager.upload_joke(image_filename, joke_text, timestamp, presigned_url)
                    print(f"Joke saved to MongoDB with image filename {image_filename}")

                    # מחיקת הקובץ המקומי לאחר ההעלאה ל-S3
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        print(f"Local File {file_path} deleted successfully.")

                    return jsonify({"image_url": presigned_url, "message": "Joke created successfully!"})

                except Exception as e:
                    print(f"Error saving joke to database: {e}")
                    return jsonify({"error": "Failed to save joke to database"}), 500

            else:
                return jsonify({"error": "Failed to generate pre-signed URL"}), 500

    except Exception as e:
        return jsonify({"error": f"Failed to upload image: {str(e)}"}), 500


# דף ראשי
@app.route("/")
def index():
    return render_template("index.html")


# # פונקציה לקבלת ברכות קיימות
def get_jokes_from_s3_to_delete(unique_one=None):
    try:
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
        if 'Contents' in response:
            print([obj['Key'] for obj in response['Contents']])
            for obj in response['Contents']:
                if obj['Key']==unique_one:
                    return obj['Key']


            return [obj['Key'] for obj in response['Contents']]
            # return [obj['Key'] for obj in response['Contents']]
        else:
            return []
    except Exception as e:
        print(f"Error fetching jokes from S3: {e}")
        return []


def get_jokes_from_s3():
    try:
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
        if 'Contents' in response:
            jokes = []
            for obj in response['Contents']:
                object_key = obj['Key']
                pre_signed_url = generate_presigned_url(object_key)  # קבלת ה-URL החתום
                jokes.append({ 'key': object_key,'url': pre_signed_url })
                # jokes.append(url)  # הוספת ה-URL לרשימה
                print(f"Generated URL for {obj['Key']}: {pre_signed_url}")  # הדפסה לצורך ניפוי שגיאות
            return jokes
        else:
            return []
    except Exception as e:
        print(f"Error fetching jokes from S3: {e}")
        return []


@app.route('/show-existing-jokes', methods=['GET'])
def show_existing_jokes():
    # הגדרת שמות קבצים מה-S3
    jokes = get_jokes_from_s3()  # פונקציה שמחזירה את רשימת הברכות ב-S3
    return render_template('existing_jokes.html', jokes=jokes, BUCKET_NAME=BUCKET_NAME)#, BUCKET_NAME='your-bucket-name')


@app.route('/delete_all_jokes', methods=['POST'])
def delete_all_jokes():
    try:
        # קבלת רשימת כל הקבצים ב-S3
        jokes = get_jokes_from_s3_to_delete()  # פונקציה שמחזירה את רשימת הברכות ב-S3

        # אם אין ברכות, החזרת הודעה
        if not jokes:
            return "No jokes to delete", 400

        # manager = S3BlessingManager(bucket_name, mongo_uri, db_name)
        # מחיקת כל הקבצים
        for joke in jokes:
            print(f"Deleting: {joke}")  # הדפסת שם הקובץ כדי לדעת מה נמחק
            s3_client.delete_object(Bucket=BUCKET_NAME, Key=joke)
            manager.delete_joke_from_db(joke)

        # Deleted successfully
        print("All jokes deleted successfully from S3 and MongoDB.")
        return redirect('/show-existing-jokes')
    except Exception as e:
        print(f"Error deleting jokes: {str(e)}")
        return f"Error deleting jokes: {str(e)}", 500

# @app.route('/delete_all_blessings', methods=['POST'])
# def delete_all_blessings():
#     try:
#         # מחיקת כל הברכות מ-S3
#         response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
#         if 'Contents' in response:
#             for obj in response['Contents']:
#                 s3_client.delete_object(Bucket=BUCKET_NAME, Key=obj['Key'])
#             print("All jokes have been deleted from S3.")
#             return jsonify({"message": "All jokes have been deleted successfully!"}), 200
#         else:
#             return jsonify({"message": "No jokes found to delete."}), 200
#     except Exception as e:
#         print(f"Error deleting jokes: {e}")
#         return jsonify({"error": "Failed to delete jokes"}), 500

# פונקציה לבדוק גישה לבאקט
def check_bucket_access(bucket_name):
    try:
        response = s3_client.list_objects(Bucket=bucket_name)
        print(f"Bucket is accessible. Found {len(response.get('Contents', []))} objects.")
    except Exception as e:
        print(f"Access Denied or Bucket not found: {e}")


@app.route('/delete_one_joke', methods=['POST'])
def delete_one_joke():
    filename = request.form.get('filename')
    app.logger.info(f"Attempting to delete: {filename}")
    if not filename:
        return "Filename not provided", 400

    try:
        delete_file_from_s3(filename)
        # manager.delete_blessing_from_db(filename)
        return redirect(url_for('show_existing_jokes'))
    except Exception as e:
        app.logger.error(f"Error deleting file: {e}")
        return f"An error occurred: {e}", 500

def delete_file_from_s3(filename):
    try:

        joke = get_jokes_from_s3_to_delete(filename)  # פונקציה שמחזירה את רשימת הברכות ב-S3

        # אם אין ברכות, החזרת הודעה
        if not joke:
            return "No such joke to delete, File wasn't found", 400
        else:
            print(f"File was found: {joke}")


        if joke == filename:
            print(f"Deleting: {joke}")  # הדפסת שם הקובץ כדי לדעת מה נמחק
            s3_client.delete_object(Bucket=BUCKET_NAME, Key=joke)
            print(f"File {filename} deleted successfully from S3.")
            manager.delete_joke_from_db(joke)
    except Exception as e:
        print(f"File not found: {e}")
        # raise


if __name__ == "__main__":
    check_bucket_access(BUCKET_NAME)
    app.run(debug=True)
