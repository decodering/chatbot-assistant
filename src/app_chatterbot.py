# Inspired from: https://www.gradio.app/guides/creating-a-custom-chatbot-with-blocks#adding-markdown-images-audio-or-videos

import random
import time
from os.path import join

import gradio as gr
from pandas import DataFrame

from api_client import OAIClient
from utils import get_root_dir_path, get_src_dir_path

TEXT_BLOCKING_MODE = True
MOCK_PREDICT_MODE = False
DEFAULT_SYSTEM_PROMPT = "You are a helpful AI assistant."
TRANSLATOR_SYSTEM_PROMPT = "You are a translater helping a client translate his english questions to Indonesian. Translate all the questions and statements provided by the client, and output his statement back in Indonesian"

css = """
#warning {background-color: #FFCCCB !important}
.feedback textarea {font-size: 240px !important}
"""


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


def bot_predict(
    global_oai_client: OAIClient, system_prompt: str, chat_history: list, oai_messages_history: list
):
    global DEFAULT_SYSTEM_PROMPT
    user_input = chat_history[-1][0]

    system_prompt = DEFAULT_SYSTEM_PROMPT if system_prompt in [None, ""] else system_prompt
    global_oai_client = (
        OAIClient(config_file=join(get_src_dir_path(), "config.yaml"))
        if global_oai_client is None
        else global_oai_client
    )
    oai_messages_history = (
        [
            {
                "role": "system",
                "content": system_prompt,
            },
        ]
        if oai_messages_history is None
        else oai_messages_history
    )
    oai_messages_history[0] = {"role": "system", "content": system_prompt}
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
            df_accrued_costs = DataFrame(
                {
                    "Cost (USD)": [round(global_oai_client.pricing_cost, 2)],
                    "Tokens (In)": [global_oai_client.input_tokens_used],
                    "Tokens (Out)": [global_oai_client.output_tokens_used],
                }
            )
            yield global_oai_client, df_accrued_costs, chat_history, oai_messages_history


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
    global_oai_client = gr.State()
    f_textbox_normal = lambda: gr.Textbox(
        value="",
        interactive=True,
        lines=1,
        show_label=False,
        placeholder="Enter text and press enter, or upload an image",
        visible=True,
        container=False,
    )
    f_button_running_disabled = lambda: gr.Button(
        value="RUNNING...", size="lg", variant="stop", interactive=False
    )
    f_button_submit = lambda: gr.Button(
        value="Submit", size="lg", variant="primary", interactive=True
    )

    with gr.Tab(label="🤖 Chatterbot Demo", id="text2text"):
        with gr.Row():
            intro_msg = gr.Markdown(value="# CHATTERBOT Demo\nWelcome to the chatbot demo!")
        with gr.Row():
            with gr.Column(scale=1):
                with gr.Accordion(label="🎛️ Controls 🎚️", open=True):
                    system_prompt_title = gr.Markdown(
                        value='### System Prompt\nDefaults to: "_You are a helpful AI assistant._" if empty.'
                    )
                    system_prompt_display = gr.Textbox(
                        value="",
                        lines=2,
                        container=False,
                        interactive=True,
                        placeholder="Please enter a new system prompt!",
                        visible=True,
                    )
                    system_prompt_btn = gr.Button(
                        value="🔄 Reset chat + Apply new Sys Prompt",
                        size="sm",
                        interactive=True,
                        visible=True,
                    )
                # TODO: This should be refreshed at end of predict action, instead of as part of the yield line.
                accrued_cost_display = gr.DataFrame(
                    value=DataFrame(
                        {
                            "Cost (USD)": [0.0],
                            "Tokens (In)": [0.0],
                            "Tokens (Out)": [0.0],
                        }
                    ),
                    label="Accrued costs",
                    show_label="hidden",
                    interactive=False,
                    visible=True,
                )
                media_upload_btn = gr.UploadButton(
                    "📁", file_types=["image", "video", "audio"], interactive=False ,size="sm"
                )

            with gr.Column(scale=2):
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
                    with gr.Column(scale=5):
                        txt = f_textbox_normal()
                    with gr.Column(scale=1):
                        submit_btn = f_button_submit()

        with gr.Row():
            with gr.Column(scale=4):
                chatterbot_examples = gr.Examples(
                    label="chatterbot examples",
                    examples=[
                        "Hello!",
                        "How are you?",
                        "What is gradio, in 20 words?",
                        "What is your name?",
                        "What was your previous response?",
                    ],
                    inputs=[txt],
                )
            with gr.Column(scale=1):
                clear_btn = gr.Button(value="Clear", size="lg")
        with gr.Row():
            system_prompt_examples = gr.Examples(
                label="system prompt examples",
                examples=[
                    DEFAULT_SYSTEM_PROMPT,
                    "You are an english to spanish translator. Translate all subsequent user inputs from english to spanish.",
                ],
                inputs=[system_prompt_display],
            )

    with gr.Tab(label="📚 Chatterbot Demo (w Rag!)", id="text2textwrag"):
        gr.Markdown(value="# 🔨 Under construction 🚧")

    with gr.Tab(label="📊 Chat history and stats", id="chatstats"):
        gr.Markdown(value="# 🔨 Under construction 🚧")

    txt_msg = (
        txt.submit(add_text, [txt, chatbot], [txt, chatbot], queue=False)
        .then(f_button_running_disabled, None, submit_btn)
        .then(
            bot_predict,
            [global_oai_client, system_prompt_display, chatbot, oai_messages_state],
            [
                global_oai_client,
                accrued_cost_display,
                chatbot,
                oai_messages_state,
            ],
            api_name="bot_response",
            show_progress="hidden",
        )
        .then(f_button_submit, None, submit_btn)
    )
    # Need to reset button function as it's blocked during processing of user input
    txt_msg.then(f_textbox_normal, None, [txt], queue=False)
    submit_btn_msg = (
        submit_btn.click(add_text, [txt, chatbot], [txt, chatbot], queue=False)
        .then(f_button_running_disabled, None, submit_btn)
        .then(
            bot_predict,
            [global_oai_client, system_prompt_display, chatbot, oai_messages_state],
            [
                global_oai_client,
                accrued_cost_display,
                chatbot,
                oai_messages_state,
            ],
            api_name="bot_response",
        )
        .then(f_button_submit, None, submit_btn)
    )
    # Need to reset button function as it's blocked during processing of user input
    submit_btn_msg.then(f_textbox_normal, None, [txt], queue=False)

    system_prompt_btn.click(
        lambda: (None, None, None),
        None,
        [global_oai_client, chatbot, oai_messages_state],
        queue=False,
    )
    clear_btn.click(
        lambda: (None, None, None, None),
        None,
        [global_oai_client, chatbot, oai_messages_state, system_prompt_display],
        queue=False,
    )
    file_msg = media_upload_btn.upload(
        add_file, [chatbot, media_upload_btn], [chatbot], queue=False
    ).then(bot_mock_predict, chatbot, chatbot)

    chatbot.like(print_vote, None, None)

demo.queue()
if __name__ == "__main__":
    demo.launch(share=False)
