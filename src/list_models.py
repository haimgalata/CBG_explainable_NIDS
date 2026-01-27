from google import genai

client = genai.Client(
    api_key="AIzaSyD0zjPA8f0XzZ7TM1_Kr1LRQGPLaEthPyA"
)

models = client.models.list()

for model in models:
    print(model.name)
