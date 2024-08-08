from langchain_community.document_loaders import TextLoader, CSVLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings import LlamafileEmbeddings
from langchain_chroma import Chroma

def store_csv_data(file_path):
    """
    A function to store csv data into the Chroma database, and save the data locally
    :param file_path: the path to the csv file
    """
    loader = CSVLoader(file_path)

    documents = loader.load()

    # Split the documents into chunks separated by newlines
    text_splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)

    # Use the LlamafileEmbeddings to embed the text
    embeddings = LlamafileEmbeddings()

    vector_store = Chroma(
        collection_name="v_db",
        embedding_function=embeddings,
        persist_directory="./chroma_langchain_db",
    )

    vector_store.add_documents(texts)

if __name__ == "__main__":
    store_csv_data("data/functionalDataBase_done.csv")
