from os.path import exists, join
from pathlib import Path

import yaml
from box import Box
from box.box import Box
from tiktoken import encoding_for_model, get_encoding


def detect_is_work_device() -> bool:
    home_dir = Path.home().resolve().__str__()
    zprofile_work = join(home_dir, ".zprofile_aab")
    zshrc_work = join(home_dir, ".zshrc_aab")
    if (exists(zprofile_work)) or (exists(zshrc_work)):
        return True
    else:
        return False


def get_src_dir_path() -> Path:
    """Returns project root folder as an absolute path."""
    return Path(__file__).parent.resolve()


def get_root_dir_path() -> Path:
    """Returns project root folder as an absolute path."""
    return Path(__file__).parent.parent.resolve()


def read_yaml(input_path: str) -> Box:
    """Read YAML file from input path."""
    with open(input_path, "r") as stream:
        try:
            return Box(yaml.safe_load(stream))
        except yaml.YAMLError as exc:
            print(exc)
            return None


def num_tokens_from_string(
    string: str, model: str = None, encoding_name: str = None
) -> int:
    """Returns the number of tokens in a text string."""
    if sum([model is None, encoding_name is None]) != 1:
        raise ValueError("Exactly one of model or encoding_name must be specified.")
    if model is not None:
        encoding = encoding_for_model(model)
    else:
        encoding = get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613"):
    """
    Return the number of tokens used by a list of messages.
    Taken from: https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
    """
    try:
        encoding = encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = get_encoding("cl100k_base")
    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
    }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = (
            4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        )
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model:
        print(
            "Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613."
        )
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        print(
            "Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613."
        )
        return num_tokens_from_messages(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens
