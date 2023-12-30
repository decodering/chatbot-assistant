# Inspired from: https://www.gradio.app/guides/creating-a-custom-chatbot-with-blocks#adding-markdown-images-audio-or-videos

import random
import time
from os.path import join

import gradio as gr

from api_client import OAIClient
from utils import get_root_dir_path

TEXT_BLOCKING_MODE = True


def add_text(user_message, chat_history):
    if TEXT_BLOCKING_MODE:
        return_msg = gr.Textbox(
            value="",
            interactive=False,
            placeholder=(" " * 20) + "Generating response...",
        )
    else:
        return_msg = ""
    return return_msg, chat_history + [[user_message, None]]


def bot(chat_history, progress=gr.Progress()):
    repeat_num = random.choice(range(3, 6))
    bot_message = f"{repeat_num}: " + ("A repeating sentence. " * repeat_num)
    chat_history[-1][1] = ""
    for ind, character in enumerate(bot_message):
        # progress(progress=0.05 * ind, desc="Processing")
        chat_history[-1][1] += character
        time.sleep(0.05)
        yield chat_history
    return chat_history


def add_file(history, file):
    history = history + [((file.name,), None)]
    return history


def print_vote(data: gr.LikeData):
    print(data.index, data.value, data.liked)


with gr.Blocks() as demo:
    f_passed = lambda: gr.Textbox(
        value="",
        interactive=True,
        placeholder="Enter text and press enter, or upload an image",
        visible=True,
    )
    f_button_stop = lambda: gr.Button("RUNNING...", size="sm", variant="stop", interactive=False)
    f_button_submit = lambda: gr.Button("Submit", size="sm", variant="secondary", interactive=True)

    intro_msg = gr.Markdown(value="# CHATTERBOT Demo\nWelcome to the chatbot demo!")
    chatbot = gr.Chatbot(
        label="CHATTERBOT-v1.0-BETA",
        elem_id="chatbot",
        bubble_full_width=False,
        avatar_images=(None, (join(get_root_dir_path(), "assets", "imgs", "avatar.png"))),
    )
    with gr.Row():
        with gr.Column(scale=4):
            txt = gr.Textbox(
                lines=1,
                show_label=False,
                placeholder="Enter text and press enter, or upload an image",
                container=False,
            )
        with gr.Column(scale=1):
            btn = gr.UploadButton("📁", file_types=["image", "video", "audio"], size="lg")
    with gr.Row():
        with gr.Column():
            submit_btn = gr.Button("Submit", size="sm")
        with gr.Column():
            clear_btn = gr.Button("Clear", size="sm")

    def say_hello():
        print("hello")

    txt_msg = (
        txt.submit(add_text, [txt, chatbot], [txt, chatbot], queue=False)
        .then(f_button_stop, None, submit_btn)
        .then(bot, chatbot, chatbot, api_name="bot_response")
        .then(f_button_submit, None, submit_btn)
    )
    if TEXT_BLOCKING_MODE:
        txt_msg.then(f_passed, None, [txt], queue=False)
    submit_btn_msg = (
        submit_btn.click(add_text, [txt, chatbot], [txt, chatbot], queue=False)
        .then(f_button_stop, None, submit_btn)
        .then(bot, chatbot, chatbot, api_name="bot_response")
        .then(f_button_submit, None, submit_btn)
    )
    if TEXT_BLOCKING_MODE:
        submit_btn_msg.then(f_passed, None, [txt], queue=False)
    clear_btn.click(lambda: None, None, chatbot, queue=False)

    file_msg = btn.upload(add_file, [chatbot, btn], [chatbot], queue=False).then(
        bot, chatbot, chatbot
    )

    chatbot.like(print_vote, None, None)
    examples = gr.Examples(
        examples=[
            "Hello!",
            "How are you?",
            "What is your name?",
        ],
        inputs=[txt],
    )

demo.queue()
if __name__ == "__main__":
    demo.launch(share=False)
