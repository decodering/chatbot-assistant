from openai import OpenAI
from dotenv import load_dotenv

# https://platform.openai.com/docs/guides/images


PREFIX_FOR_NO_PROMPT_AUGMENTING = "I NEED to test how the tool works with extremely simple prompts. DO NOT add any detail, just use it AS-IS:"
IMAGE_SIZE_STD = "1024x1024"
IMAGE_SIZE_LRG_TALL = "1024x1792"
IMAGE_SIZE_LRG_WIDE = "1792x1024"

PROMPT = "a wooden king chess piece wearing sunglasses"

load_dotenv()
client = OpenAI()

# num of outputs (n) has to be =1 for dall-e-3
response = client.images.generate(
    model="dall-e-3",
    prompt=PROMPT,
    size=IMAGE_SIZE_STD,
    quality="standard",
    n=1,
)

image_url, revised_prompt = response.data[0].url, response.data[0].revised_prompt
print(image_url)
print(revised_prompt)

# RESPONSE EXAMPLE
# ===
# ImagesResponse(
#     created=1704670785,
#     data=[
#         Image(
#             b64_json=None,
#             revised_prompt="Create an image of a white Siamese cat. The cat should have striking blue eyes, distinctive pointed features such as ears, paws, nose, and tail. The feline is sitting in a relaxed position, its fur is soft and fluffy, and there's a curious expression on its face.",
#             url="https://oaidalleapiprodscus.blob.core.windows.net/private/org-eP45OI0kgXFujhdLoWaODaUh/user-5uYw7cB17bnGGT5A4eqAQSBc/img-r5wp9MlZwIZFrgHLuOt6m449.png?st=2024-01-07T22%3A39%3A45Z&se=2024-01-08T00%3A39%3A45Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2024-01-07T02%3A03%3A02Z&ske=2024-01-08T02%3A03%3A02Z&sks=b&skv=2021-08-06&sig=thaRLq4bg0y7zTUR15s/mB/8QRT8stlD9wuMca0JGX8%3D",
#         )
#     ],
# )

# Previous generations
# ===
# siamese cat: https://oaidalleapiprodscus.blob.core.windows.net/private/org-eP45OI0kgXFujhdLoWaODaUh/user-5uYw7cB17bnGGT5A4eqAQSBc/img-r5wp9MlZwIZFrgHLuOt6m449.png?st=2024-01-07T22%3A39%3A45Z&se=2024-01-08T00%3A39%3A45Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2024-01-07T02%3A03%3A02Z&ske=2024-01-08T02%3A03%3A02Z&sks=b&skv=2021-08-06&sig=thaRLq4bg0y7zTUR15s/mB/8QRT8stlD9wuMca0JGX8%3D
# chess peice: https://oaidalleapiprodscus.blob.core.windows.net/private/org-eP45OI0kgXFujhdLoWaODaUh/user-5uYw7cB17bnGGT5A4eqAQSBc/img-d770zZB0uDyMZ1yw1spyMMup.png?st=2024-01-07T22%3A53%3A31Z&se=2024-01-08T00%3A53%3A31Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2024-01-07T03%3A16%3A52Z&ske=2024-01-08T03%3A16%3A52Z&sks=b&skv=2021-08-06&sig=vO3Z8oK%2Bya2KNVsgI56GH1TJHtWTkV/Z1Vl3JoeeQi4%3D
