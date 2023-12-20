from logging import PlaceHolder
from openai import OpenAI
import gradio as gr
import time

# Translation Bot
def translation(text, language):

    client = OpenAI()

    stream = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
        {"role": "system", "content": f"You are a localisation agent. You speak in real {language} as a {language} native speakers would speak. Step 1: Don't translate word by word. Read and understand the whole things. Step 2: Write it as {language} native speakers would do. The result should keep the format and tone of the original text. It should sounds natural and reflect the {language} culture."},
        {"role": "user", "content": text},
        ],
    )
    return stream.choices[0].message.content
    
# Summary Bot
def summary(prompt):

    client = OpenAI()

    stream = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
        {"role": "system", "content": f"Your task is summarising the given text in the way customers want in its provided language. Follow those steps to summarise:\nStep 1: Find all key sentences, don't choose any points without context. Step 2: Shorter all key sentences into key points. The sentences should be short and precise. Step 3: Do the step 1 and 2 again.\nStep4: Put two versions together, put the content of the output in triple quotes.\nStep 5: Always format it in the desired way mentioned in the text if it is given."},
        {"role": "user", "content": prompt},
        ],
    )

    output = stream.choices[0].message.content
    
    stream = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
        {"role": "system", "content": "You will be given a summary. Choose only the content inside the triple quotes precisely. Remove triple quotes."},
        {"role": "user", "content": f'{output}'},
        ],
    )
    return stream.choices[0].message.content
    
    
# Translation Bot
def rewrite(prompt):

    client = OpenAI()

    stream = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
        {"role": "system", "content": f"Your task is rewriting in the way customers want in their provided language."},
        {"role": "user", "content": prompt},
        ],
    )
    return stream.choices[0].message.content

# Base knowledge for chatbot
f = open("textBotData.txt", "r", encoding="utf-8")
data = f.read()
f.close()

f = open("textBotRules.txt", "r", encoding="utf-8")
rules = f.read()
f.close()

knowledge = f'\"""{data}\"""'

# Customer service agent chatbot
def user(message, history):
    return "", history + [[message, None]]
    
def agent(prompt, history):
    history_openai_format = []
    for human, assistant in history:
        history_openai_format.append(f"user: {human}")
        history_openai_format.append(f"user: {assistant}")
        
    client = OpenAI()

    stream = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
        {"role": "system", "content": "Act like you are a professional customer service agent providing accurate information to customers about the app.\n" + rules + "\n" + knowledge + "\n" + "\n".join(history_openai_format)},
        {"role": "user", "content": prompt},
        ],
    )
    
    bot_msg =  stream.choices[0].message.content
    
    history[-1][1] = ""
    for character in bot_msg:
        history[-1][1] += character
        time.sleep(0.01)
        yield history
    


# Implement UI using gradio   
with gr.Blocks() as demo:
    gr.Markdown("# TextAI")

    with gr.Tab("Summarise"):
        with gr.Row():
            with gr.Column():
                prompt = gr.Text(label= "Text input", lines=5)
            with gr.Column():
                output = gr.Text(label="Generated Text", lines=5)
        btn = gr.Button("Summarise", elem_classes="submit-button")
        btn.click(summary, inputs=[prompt], outputs=[output])

        
                
        gr.Examples(["Sherlock Holmes' quick eye took in my occupation, and he shook his head with a smile as he noticed my questioning glances. “Beyond the obvious facts that he has at some time done manual labour, that he takes snuff, that he is a Freemason, that he has been in China, and that he has done a considerable amount of writing lately, I can deduce nothing else.”"], inputs=[prompt])
        


        
    with gr.Tab("Translation"):
        with gr.Row():
            with gr.Column():
                prompt = gr.Text(label= "Text input", lines=5)
                lang = gr.Radio(label="Languange", choices=["Vietnamese", "English", "Japanese"])
            
            output = gr.Text(label="Generated Text", lines=5)
            
        btn = gr.Button("Translate", elem_classes="submit-button")
        btn.click(translation, inputs=[prompt, lang], outputs=[output])

        
        gr.Examples([["Sherlock Holmes' quick eye took in my occupation, and he shook his head with a smile as he noticed my questioning glances. “Beyond the obvious facts that he has at some time done manual labour, that he takes snuff, that he is a Freemason, that he has been in China, and that he has done a considerable amount of writing lately, I can deduce nothing else.”", "Vietnamese"]], inputs=[prompt, lang])

        
    with gr.Tab("Rewrite"):
        with gr.Row():
        
            prompt = gr.Text(label= "Text input", lines=5)
            output = gr.Text(label="Generated Text", lines=5)
            
        btn = gr.Button("Generate")
        btn.click(rewrite, inputs=[prompt], outputs=[output])
        
        gr.Examples(["Sherlock Holmes' quick eye took in my occupation, and he shook his head with a smile as he noticed my questioning glances. “Beyond the obvious facts that he has at some time done manual labour, that he takes snuff, that he is a Freemason, that he has been in China, and that he has done a considerable amount of writing lately, I can deduce nothing else.”"], inputs=[prompt])
     
        
    gr.Markdown("### Assistant")   
    
    chatbot = gr.Chatbot(value=[[None, "How can I help you today?"]], 
    elem_id="chatbot",
    bubble_full_width=False, height=200)
        
    with gr.Row():
        msg = gr.Textbox(placeholder="Enter your questions", scale=5, show_label=False, container=False)
        clear = gr.Button("Clear")
    
    msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(agent, [msg, chatbot], chatbot)
    clear.click(lambda: [[None, "How can I help you today?"]], None, chatbot, queue=False)
    
demo.queue()
demo.launch()