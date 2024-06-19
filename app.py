import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

# Load environment variables
load_dotenv()

# Configure Google Generative AI
api_key = os.getenv("API_KEY")
if not api_key:
    st.error("API_KEY not found in environment variables. Please set it in the .env file.")
    st.stop()

genai.configure(api_key=api_key)

# Prompt for the generative model
prompt = """
You are a YouTube video summarizer. You will take the transcript text
and summarize the entire video, providing the important summary in points
within 250 words. Please provide the summary of the text given here: 
"""

# Function to extract transcript from YouTube
def extraction_from_youtube(youtube_video_url):
    try:
        video_id = youtube_video_url.split("v=")[1]
        transcripted_text = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([item["text"] for item in transcripted_text])
        return transcript
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        st.error(f"Transcripts are disabled or not found for video ID: {video_id}")
        return None
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# Function to generate summary using generative AI
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt + transcript_text)
    return response.text

# Streamlit app layout
st.title("YouTube Transcript to Detailed Notes Converter")

youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    try:
        video_id = youtube_link.split("v=")[1]
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)
    except IndexError:
        st.error("Invalid YouTube link. Please enter a valid link.")

if st.button("Get Detailed Notes"):
    transcript_text = extraction_from_youtube(youtube_link)

    if transcript_text:
        response = generate_gemini_content(transcript_text, prompt)
        st.markdown("## Detailed Notes")
        st.write(response)
