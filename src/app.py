# Inspired from: https://www.gradio.app/guides/creating-a-custom-chatbot-with-blocks#adding-markdown-images-audio-or-videos

import random
import time
from os.path import join

import gradio as gr

from api_client import OAIClient
from utils import get_root_dir_path, get_src_dir_path

TEXT_BLOCKING_MODE = True
MOCK_PREDICT_MODE = False
global_oai_client = OAIClient(config_file=join(get_src_dir_path(), "config.yaml"))


def say_hello():
    print("hello")


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


def bot_predict(chat_history: list, oai_messages_history: list):
    user_input = chat_history[-1][0]

    if oai_messages_history is None:
        oai_messages_history = [
            {
                "role": "system",
                "content": "You are a helpful AI assistant.",
            },
        ]
    oai_messages_history.append({"role": "user", "content": user_input})

    stream = global_oai_client(
        messages=oai_messages_history,
        return_raw_response=True,
        stream=True,
    )

    chat_history[-1][1] = ""
    oai_messages_history.append({"role": "assistant", "content": None})
    for chunk in stream:
        new_msg_chunk = chunk.choices[0].delta
        finish_flag = chunk.choices[0].finish_reason

        # TODO: Consider incorporating this as part of stream object. WIP in api_client.py as well.
        if finish_flag == "stop":
            finished_response = chat_history[-1][1]
            global_oai_client._postprocess(
                messages=oai_messages_history,
                model="gpt-3.5-turbo-1106"
                if global_oai_client.MODEL == "zeroshot-exploration"
                else global_oai_client.MODEL,  # TODO: Special work flag
                response=finished_response,
            )
            print(f"INPUT tokens used: {global_oai_client.input_tokens_used}")
            print(f"OUTPUT tokens used: {global_oai_client.output_tokens_used}")
            print(f"Cumulative cost so far: $ {global_oai_client.pricing_cost}")

        if new_msg_chunk.content is not None:
            chat_history[-1][1] += new_msg_chunk.content
            oai_messages_history[-1]["content"] = chat_history[-1][1]

            time.sleep(0.02)
            yield chat_history, oai_messages_history


def bot_mock_predict(chat_history, progress=gr.Progress()):
    repeat_num = random.choice(range(3, 6))
    bot_message = f"{repeat_num}: " + ("A repeating sentence. " * repeat_num)
    chat_history[-1][1] = ""
    for ind, character in enumerate(bot_message):
        # progress(progress=0.05 * ind, desc="Processing")
        chat_history[-1][1] += character
        time.sleep(0.05)
        yield chat_history


def add_file(history, file):
    history = history + [((file.name,), None)]
    return history


def print_vote(data: gr.LikeData):
    print(data.index, data.value, data.liked)


with gr.Blocks() as demo:
    oai_messages_state = gr.State()
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
        avatar_images=(
            None,
            (join(get_root_dir_path(), "assets", "imgs", "avatar.png")),
        ),
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

    txt_msg = (
        txt.submit(add_text, [txt, chatbot], [txt, chatbot], queue=False)
        .then(f_button_stop, None, submit_btn)
        .then(
            bot_predict,
            [chatbot, oai_messages_state],
            [chatbot, oai_messages_state],
            api_name="bot_response",
        )
        .then(f_button_submit, None, submit_btn)
    )
    # Need to reset button function as it's blocked during processing of user input
    txt_msg.then(f_passed, None, [txt], queue=False)
    submit_btn_msg = (
        submit_btn.click(add_text, [txt, chatbot], [txt, chatbot], queue=False)
        .then(f_button_stop, None, submit_btn)
        .then(
            bot_predict,
            [chatbot, oai_messages_state],
            [chatbot, oai_messages_state],
            api_name="bot_response",
        )
        .then(f_button_submit, None, submit_btn)
    )
    # Need to reset button function as it's blocked during processing of user input
    submit_btn_msg.then(f_passed, None, [txt], queue=False)

    clear_btn.click(lambda: None, None, chatbot, queue=False)
    file_msg = btn.upload(add_file, [chatbot, btn], [chatbot], queue=False).then(
        bot_mock_predict, chatbot, chatbot
    )

    chatbot.like(print_vote, None, None)
    examples = gr.Examples(
        examples=[
            "Hello!",
            "How are you?",
            "What is gradio, in 20 words?",
            "What is your name?",
            "What was your previous response?",
        ],
        inputs=[txt],
    )

demo.queue()
if __name__ == "__main__":
    demo.launch(share=False)
