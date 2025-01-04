import boto3
import botocore
from datetime import datetime
from pymongo import MongoClient

class S3AndMongoDBJokeManager:
    def __init__(self, bucket_name, mongo_uri, db_name):
        # Connect to S3 - Initialize the S3 client
        self.bucket_name = bucket_name
        self.s3_client = boto3.client('s3')

        # Connect to MongoDB
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db['jokes']

    def create_bucket(self):
        """
        Create a bucket if it does not already exist.
        """
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            print(f"Bucket '{self.bucket_name}' already exists.")
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                print(f"Creating bucket '{self.bucket_name}'...")
                try:
                    region = boto3.session.Session().region_name
                    if region == 'us-west-2':
                        self.s3_client.create_bucket(Bucket=self.bucket_name)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=self.bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': region}
                        )
                    print(f"Bucket '{self.bucket_name}' created successfully.")
                except botocore.exceptions.ClientError as ce:
                    print(f"Error creating bucket: {ce}")
            else:
                print(f"Unexpected error: {e}")

    def delete_joke_from_db(self, filename):
        """
        Delete a joke from the database by filename.
        :param filename: The filename of the joke to delete.
        :return: True if deletion was successful, False otherwise.
        """
        try:
            filename = filename.split('/')[-1]
            result = self.collection.delete_one({'filename': filename})
            if result.deleted_count > 0:
                print(f"Joke with filename {filename} successfully deleted from the database.")
                return True
            else:
                print(f"Joke with filename {filename} not found in the database.")
                return False
        except Exception as e:
            print(f"Error deleting Joke from database: {e}")
            return False

    # def delete_blessing(self, blessing_key):
    #     try:
    #         # מחיקת ברכה ממסד הנתונים
    #         result = self.collection.delete_one({"key": blessing_key})
    #         if result.deleted_count == 0:
    #             raise Exception(f"No blessing found with key {blessing_key}")
    #         print(f"Deleted blessing with key {blessing_key} from MongoDB.")
    #     except Exception as e:
    #         print(f"Error deleting blessing from MongoDB: {e}")
    #         raise

    # def delete_all_blessings(self):
    #     """
    #     Delete all jokes from the database.
    #     :return: The number of deleted documents.
    #     """
    #     try:
    #         result = self.collection.delete_many({})
    #         print(f"All jokes deleted. Total deleted: {result.deleted_count}")
    #         return result.deleted_count
    #     except Exception as e:
    #         print(f"Error deleting all jokes from database: {e}")
    #         return 0

    def upload_joke(self, image_filename, joke_text, timestamp, presigned_url):
        """Upload a blessing to S3 and store it in the database"""
        try:
            Joke_data = {
                'filename': image_filename,
                'text': joke_text,
                'timestamp': timestamp,
                's3_link': presigned_url
            }
            self.collection.insert_one(Joke_data)
            return image_filename  # Return the filename of the uploaded joke
        except Exception as e:
            print(f"Error uploading joke: {e}")
            return None

    # def download_blessing(self, filename):
    #     """Fetch a blessing from S3 by filename"""
    #     try:
    #         # Get the file from S3
    #         response = self.s3_client.get_object(Bucket=self.bucket_name, Key=filename)
    #         blessing_content = response['Body'].read().decode('utf-8')  # Read the content
    #         return blessing_content
    #     except Exception as e:
    #         print(f"Error fetching file {filename}: {e}")
    #         return None

    # def get_blessing_from_db(self, filename):
    #     """Fetch a blessing from the database by filename"""
    #     try:
    #         blessing = self.collection.find_one({'filename': filename})
    #         if blessing:
    #             return blessing['text']
    #         else:
    #             print(f"Blessing with filename {filename} not found in database.")
    #             return None
    #     except Exception as e:
    #         print(f"Error fetching blessing from database: {e}")
    #         return None
