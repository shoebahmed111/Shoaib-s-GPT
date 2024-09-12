import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import google.generativeai as genai
import os

# Initialize the speech recognition and TTS engine
recognizer = sr.Recognizer()

# Sidebar for inputting Gemini API key and selecting input method
with st.sidebar:
    gemini_api_key = st.text_input("Google Gemini API Key", key="gemini_api_key", type="password")
    st.markdown("[Get a Gemini API key](https://developers.generativeai.google/api-key)")
    
    st.write("## Input Method")
    input_method = st.radio("Choose input method:", ("Text", "Voice"))

# Title and description of the chatbot
st.title("🤖 Shoaib GPT ")
st.caption("🚀 Shoaib GPT is a powerful language model that lets you engage through both voice and text, offering seamless conversations and intelligent responses for your tasks.")

# CSS for gradient text
gradient_text_html = """
<style>
.gradient-text {
    font-weight: bold;
    background: -webkit-linear-gradient(left, #FF6347, #FFA07A);
    background: linear-gradient(to right, #FF6347, #FFA07A);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 3em;
}
</style>
"""
st.markdown(gradient_text_html, unsafe_allow_html=True)

# Initialize session state for chat messages
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

# Display chat history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Function to convert text to speech using gTTS
def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    tts.save("response.mp3")
    audio_file = open("response.mp3", "rb")
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format="audio/mp3")

# Function to capture voice input and convert to text
def voice_to_text():
    with sr.Microphone() as source:
        st.write("Listening...")
        audio = recognizer.listen(source)
        try:
            st.write("Recognizing...")
            voice_input = recognizer.recognize_google(audio)
            st.write(f"User said: {voice_input}")
            return voice_input
        except sr.UnknownValueError:
            st.error("Sorry, I could not understand your voice.")
        except sr.RequestError:
            st.error("Could not request results from Google Speech Recognition service.")
        return ""

# Handle input (text or voice)
prompt = None
if input_method == "Text":
    prompt = st.chat_input("Enter your message")  # Text input from user
else:
    if st.sidebar.button("Start Voice Input"):
        prompt = voice_to_text()  # Voice input converted to text

# Process the input if there is a prompt (either text or voice)
if prompt:
    if not gemini_api_key:
        st.info("Please add your Google Gemini API key to continue.")
        st.stop()

    # Configure the Gemini API with the provided key
    genai.configure(api_key=gemini_api_key)

    # Add user message to the chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Create a response using the Gemini API
    model = genai.GenerativeModel("gemini-1.5-flash")  # Update model as per availability
    response = model.generate_content(prompt)
    msg = response.text

    # Add assistant response to the chat history
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)

    # Convert the Gemini response to speech and play it
    text_to_speech(msg)
