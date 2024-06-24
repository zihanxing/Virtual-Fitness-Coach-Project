# Configure LlamaIndex
from llama_index.core import Settings
from llama_index.embeddings.llamafile import LlamafileEmbedding
from llama_index.llms.llamafile import Llamafile
from llama_index.core.node_parser import SentenceSplitter

Settings.embed_model = LlamafileEmbedding(base_url="http://localhost:8080")

Settings.llm = Llamafile(
	base_url="http://localhost:8080",
	temperature=0,
	seed=0
)

# Also set up a sentence splitter to ensure texts are broken into semantically-meaningful chunks (sentences) that don't take up the model's entire
# context window (2048 tokens). Since these chunks will be added to LLM prompts as part of the RAG process, we want to leave plenty of space for both
# the system prompt and the user's actual question.
Settings.transformations = [
	SentenceSplitter(
    	chunk_size=256,
    	chunk_overlap=5
	)
]