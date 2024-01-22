from dotenv import load_dotenv
from pymongo import MongoClient
import base64
import io
import streamlit as st
import os
import google.generativeai as genai
from datetime import datetime
import cloudinary
import cloudinary.uploader

# Load environment variables
load_dotenv()

# Set up the frontend with Instagram-like accent color
st.set_page_config(page_title='Caption Generator', page_icon="📸", layout="wide")

# Header with Instagram-like styling
st.title('Caption Generator by @ashusnapx 📸')
st.write("Unleash the magic of AI to craft captivating Instagram captions!")

# Configure Google Gemini API
genai.configure(api_key=os.getenv('GOOGLE_GEMINI_KEY'))

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

# Set up MongoDB connection
mongo_uri = os.getenv('MONGODB_URI')
client = MongoClient(mongo_uri)
db = client.get_database('utube')

# Check if MongoDB is connected
try:
    client.server_info()
    st.success('Streamlit Working... 🚀')
except Exception as e:
    st.error(f'MongoDB Connection Error: {e}')

# Function to get Gemini responses
def get_gemini_responses(input, image_data, prompt):
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content([input, image_data[0], prompt])
    return response.text

# Function to get image uploaded
def get_image_uploaded(uploaded_image):
    if uploaded_image is not None:
        # Convert image to bytes
        image_byte_arr = io.BytesIO(uploaded_image.read()).read()

        image_parts = [
            {
                'mime_type': 'image/jpeg',  # Adjust the MIME type if necessary
                'data': base64.b64encode(image_byte_arr).decode()
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError('Please upload your image...')

# Job description input area
job_description = st.text_input('Any specific requirements for your caption:', key='input')

# Image upload area
uploaded_file = st.file_uploader('Upload your image (* JPEG or PNG allowed)', type=['jpg', 'jpeg', 'png'])

# Image uploaded success message
if uploaded_file is not None:
    st.success('🎉 Image uploaded successfully!')

# Button with Instagram-like styling
variant1 = st.button('Generate Captions', key='generate_button')

# Updated Input prompt
input_prompt1 = """
Act as a professional Instagram caption generator. Your task would be to analyze the image and generate the best, short, catchy, vibey, modern, poetic, Hindi, English, blend, bilingual, etc. variations possible. Generate as many captions as possible. Add better emojis in the end, add hashtags, and also add @ashusnapx at the end of the caption.
"""

# Button actions
if variant1:
    if uploaded_file is not None:
        image_data = get_image_uploaded(uploaded_file)
        response = get_gemini_responses(input_prompt1, image_data, job_description)
        st.subheader('Caption Ideas:')
        st.write(response)

        # Convert image data to bytes
        image_byte_arr = base64.b64decode(image_data[0]['data'])
        
        # Upload image to Cloudinary
        cloudinary_response = cloudinary.uploader.upload(image_byte_arr)

        # Insert data into MongoDB collection
        captions_collection = db.get_collection('captions')

        # Replace 'captions' with your collection name
        caption_data = {
            'image_url': cloudinary_response['secure_url'],
            'captions': response.split('\n'),
            'job_description': job_description,
            'timestamp': datetime.utcnow(),
        }
        captions_collection.insert_one(caption_data)
    else:
        st.warning('Please upload your image...')

# Footer with Instagram-like styling
st.markdown(
    """
<hr style="border:0.5px solid #808080">
<div style="display: flex; justify-content: space-between; align-items: center; padding-top: 10px; padding-bottom: 10px;">
    <div>
        <span style="font-size: 14px; font-weight: bold;">Ashutosh Kumar</span><br>
        <span style="font-size: 12px;">AI Caption Developer</span>
    </div>
    <div>
        <span style="font-size: 12px;">Twitter: x.com/ashusnapx: </span><br>
        <span style="font-size: 12px;">LinkedIn: linkedin.com/in/ashusnapx</span>
    </div>
</div>
""",
    unsafe_allow_html=True
)
