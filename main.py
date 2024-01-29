import gradio as gr
import pathlib
import textwrap
import os

import google.generativeai as genai
from dotenv import load_dotenv


from deepgram import DeepgramClient, PrerecordedOptions


load_dotenv()
# The API key we created in step 3
DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')
css = """
.container {
    padding: 40px;
}
"""

genai.configure(api_key = os.getenv('GOOGLE_API_KEY'))

txt_model = genai.GenerativeModel('gemini-pro')
initial_prompt = "You are a helpful chatbot that lets user chat with the audio file they uploaded. "

audio_text = ""



options = PrerecordedOptions(
        smart_format=True, model="nova-2", language="en-IN"
        )

def audio_transcribe(audio_file):
    deepgram = DeepgramClient(DEEPGRAM_API_KEY)
    global audio_text
    with open(audio_file, 'rb') as buffer_data:
        payload = { 'buffer': buffer_data }

        options = PrerecordedOptions(
      model="nova-2", 
      language="en", 
      smart_format=True, 
      paragraphs=True, 
      diarize=True, 
    ) 

        response = deepgram.listen.prerecorded.v('1').transcribe_file(payload, options)
        resp = response.to_dict()
        reply=resp['results']['channels'][0]['alternatives'][0]['paragraphs']['transcript']
        # print(resp.results.channels.alternatives.paragraphs.transcript)

        audio_text+= reply
    return audio_text


   
def query_message(history,txt):
    history += [(txt,None)]
    return history
def llm_response(history,text):
    
    response = txt_model.generate_content(initial_prompt+ audio_text+text)
    history += [(None,response.text)]
    return history

with gr.Blocks(css=css) as demo:
    with gr.Row():
        with gr.Column(elem_classes=["container"]):
            audio_file = gr.File(label="upload audio")
            btn_gen = gr.Button("Transcribe")
            transcribed_text = gr.TextArea()

        with gr.Column():
            chatbot = gr.Chatbot(scale = 2,
            height=550)
            msg = gr.Textbox()
            chat_btn = gr.Button("Send")
        
        clicked_audio = btn_gen.click(audio_transcribe,audio_file, transcribed_text)
        clicked_chat = chat_btn.click(query_message, [chatbot, msg], chatbot).then(llm_response,
                                [chatbot,msg],
                                chatbot)
        

demo.launch(share=True)