from os.path import join
from typing import Any, Dict, List, Optional, Union

from box.box import Box
from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletion

from utils import get_src_dir_path, num_tokens_from_messages, num_tokens_from_string, read_yaml


class OAIClient:
    # Default params (will be overwritten if config file specified)
    MODEL: str = "gpt-3.5-turbo-1106"
    TEMPERATURE: float = 0.2
    SEED: int = 12345
    TOP_P: float = 1.0

    # Session state params
    input_tokens_used: int = 0
    output_tokens_used: int = 0
    pricing_cost: float = 0.0

    # Hardcoded
    # Cost of model calls (per 1000 tokens) (input, output costs)
    cost_mapping = {
        "gpt-3.5-turbo-1106": (0.0010, 0.0020),
        "gpt-3.5-turbo-0613": (0.0015, 0.0020),
        "gpt-3.5-turbo-16k-0613": (0.0030, 0.0040),
    }

    def __init__(
        self,
        api_key: str = None,
        config: Box = None,
        client: OpenAI = None,
    ) -> None:
        """
        Models list: https://platform.openai.com/docs/models
        Models pricing: https://openai.com/pricing // https://platform.openai.com/docs/deprecations/2023-11-06-chat-model-updates
        Nice costcalculating library: https://www.reddit.com/r/Python/comments/12lec2s/openai_pricing_logger_a_python_package_to_easily/
        """
        self._parse_config(config_path=config)
        self.client = client if client else self._init_client(api_key=api_key)

    def __call__(self, *args, **kwargs):
        return self.query(*args, **kwargs)

    def query(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        temperature: float = None,
        seed: int = None,
        top_p: float = None,
        max_tokens: int = None,
        return_raw_response: bool = False,
        **kwargs,
    ) -> Union[str, ChatCompletion]:
        # Defaults
        model = model if model is not None else self.MODEL
        temperature = temperature if temperature is not None else self.TEMPERATURE
        seed = seed if seed is not None else self.SEED
        top_p = top_p if top_p is not None else self.TOP_P

        response = self.client.chat.completions.create(
            messages=messages,
            model=model,
            temperature=temperature,
            seed=seed,
            top_p=top_p,
            max_tokens=max_tokens,
            **kwargs,
        )
        self._postprocess(messages=messages, model=model, response=response)
        if return_raw_response:
            return response
        else:
            return response.choices[0].message.content

    def _postprocess(
        self,
        messages: List[Dict[str, str]],
        model: str,
        response: str,
    ) -> None:
        """Postprocess response."""
        self._track_tokens_used_in_call(messages=messages, model=model, response=response)
        self._track_cost_of_call(model=model)

    def _track_cost_of_call(self, model: str) -> None:
        """
        Calculate cost of call.
        """
        input_token_cost, output_token_cost = self.cost_mapping[model]  # per 1000 token
        self.pricing_cost += input_token_cost * (
            self.input_tokens_used / 1000
        ) + output_token_cost * (self.output_tokens_used / 1000)

    def _track_tokens_used_in_call(
        self,
        messages: List[Dict[str, str]],
        model: str,
        response: str,
        manual_calculation: bool = False,
    ):
        """Calculate number of tokens used in call."""
        self.output_tokens_used += (
            num_tokens_from_string(string=response.choices[0].message.content, model=model)
            if manual_calculation
            else response.usage.completion_tokens
        )
        self.input_tokens_used += (
            num_tokens_from_messages(messages=messages, model=model)
            if manual_calculation
            else response.usage.prompt_tokens
        )

    def _test_connection(self, print_output: bool = False) -> bool:
        try:
            response = self.client.query(
                messages=[
                    {
                        "role": "user",
                        "content": "say hi",
                    },
                ],
                return_raw_response=True,
            )
            if print_output:
                print(response)
                print(response.choices[0].message.content)
            return True
        except Exception as e:
            print(e)
            return False

    def _close_client(self) -> None:
        """Close OpenAI client."""
        if not self.client.is_closed:
            self.client.close()

    def _parse_config(self, config_path: str) -> None:
        """Parse config file from input path."""
        if self.config is None:
            self.config = None
        else:
            self.config = read_yaml(config_path=config_path) if config_path is not None else None
            for key, value in self.config.items():
                if key in self.__dict__:
                    setattr(self, key, value)

    @staticmethod
    def _init_client(api_key: str, **kwargs) -> OpenAI:
        """Initialize OpenAI client."""
        if api_key is None:
            try:
                load_dotenv()
            except Exception as e:
                pass
            return OpenAI(**kwargs)
        else:
            return OpenAI(api_key=api_key, **kwargs)


if __name__ == "__main__":
    CONFIG_FILE_PATH = join(get_src_dir_path(), "config.yaml")
    config = read_yaml(config_path=CONFIG_FILE_PATH)

    client = OAIClient(api_key=config.OPENAI_API_KEY)
    _ = client._test_connection(print_output=True)
    print(client.pricing_cost)
    print(client.input_tokens_used, client.output_tokens_used)
