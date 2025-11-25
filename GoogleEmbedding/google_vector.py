import os
import tempfile
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings 
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import BSHTMLLoader
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004", 
    google_api_key=api_key
)

DB_DIR = "chroma_db"

def process_and_store_documents(uploaded_files):
    documents = []
    html_content = "" 
    
    for file in uploaded_files:
        file_extension = os.path.splitext(file.name)[1].lower()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file.read())
            temp_path = temp_file.name

        loader = None
        try:
            if file_extension == ".pdf":
                loader = PyPDFLoader(temp_path)
            elif file_extension == ".md":
                loader = TextLoader(temp_path, encoding="utf-8")
            elif file_extension == ".txt":
                loader = TextLoader(temp_path, encoding="utf-8")
            elif file_extension == ".json":
                loader = TextLoader(temp_path, encoding="utf-8")
            elif file_extension == ".html":
                loader = BSHTMLLoader(temp_path)
                with open(temp_path, "r", encoding="utf-8") as f:
                    html_content = f.read()

            if loader:
                docs = loader.load()
                for doc in docs:
                    doc.metadata["source_document"] = file.name
                documents.extend(docs)
        
        except Exception as e:
            print(f"Error processing {file.name}: {e}")
        finally:
            try:
                os.remove(temp_path)
            except:
                pass

    if not documents:
        return "No documents processed.", None

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)

    vector_store = Chroma.from_documents(
        documents=chunks, 
        embedding=embedding_model, 
        persist_directory=DB_DIR
    )
    
    return f"Success! Processed {len(documents)} documents.", html_content