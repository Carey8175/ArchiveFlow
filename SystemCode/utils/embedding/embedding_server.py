import asyncio
from sanic import Sanic
from sanic import response
from sanic.request import Request
from concurrent.futures import ThreadPoolExecutor
from BCEmbedding import EmbeddingModel

# ------------------ Embedding Server ------------------
# code list
# code 0: success
# code 101: no sentence provided
# code 102: sentence must be a list


app = Sanic("EmbeddingServer")


# Initialize the embedding model and move it to the GPU if available
model_path = "../../server/models/bce-embedding-base_v1"
model = EmbeddingModel(model_name_or_path=model_path)

# Create a thread pool executor
executor = ThreadPoolExecutor(max_workers=4)


# Function to extract embedding using the model
def get_embedding(sentences):
    # Convert sentence to tensor and move to GPU
    embeddings = model.encode(sentences)  # Assuming encode returns a list of embeddings
    return embeddings   # Move back to CPU and convert to list for JSON serialization


# Define an async function to wrap the blocking call to the thread pool
async def extract_embedding(sentence):
    loop = asyncio.get_event_loop()
    embedding = await loop.run_in_executor(executor, get_embedding, sentence)
    return embedding


@app.route("/embed", methods=["POST"])
async def embed_sentence(request: Request):
    # Extract the sentence from the request
    sentences = request.json.get('sentences')
    if not sentences:
        return response.json({"code": 101, "error": "No sentence provided"}, status=400)

    if not isinstance(sentences, list):
        return response.json({"code": 102, "error": "Sentences must be a list"}, status=400)

    # Get the embedding asynchronously
    embedding = await extract_embedding(sentences)

    # Return the embedding as a JSON response
    return response.json({"code": 0, "data": embedding.tolist()})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6006)
