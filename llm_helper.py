import os
from dotenv import load_dotenv
from google import genai 
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings 

load_dotenv() 

MODEL_NAME = "gemini-2.5-flash" 

def get_vector_store():
    """Helper to connect to DB"""
    if not os.path.exists("chroma_db"):
        return None
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found.")
        return None

    embedding_model = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004", 
        google_api_key=api_key
    )
    return Chroma(persist_directory="chroma_db", embedding_function=embedding_model)

def ask_bot(query, api_key=None):
    """Phase 2: Test Case Generation"""
    try:
        client = genai.Client(api_key=api_key)
        vectorstore = get_vector_store()
        if not vectorstore:
            return "Knowledge Base not found. Please build it first."
        
        docs = vectorstore.similarity_search(query, k=3)
        context_text = "\n\n".join([doc.page_content for doc in docs])

        full_prompt = f"""
        Act as a QA Test Case Generator.
        Based on the Context provided, generate a Test Case table for the User Request.

        CONTEXT:
        {context_text}

        USER REQUEST:
        {query}

        STRICT OUTPUT RULES:
        1. Output ONLY a Markdown Table.
        2. Do NOT write any introductory text (like "Here are the test cases").
        3. Do NOT write any conclusion or explanations.
        4. The Table MUST have these exact columns: | Test_ID | Feature | Test_Scenario | Expected_Result | Grounded_In |
        5. Write all text in simple text format
        """

        response = client.models.generate_content(
            model=MODEL_NAME, 
            contents=full_prompt
        )
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def generate_selenium_script(test_case, html_code, api_key=None):
    """Phase 3: Selenium Script Generation"""
    try:
        client = genai.Client(api_key=api_key)
        
        vectorstore = get_vector_store()
        doc_context = ""
        if vectorstore:
            docs = vectorstore.similarity_search(test_case, k=2)
            doc_context = "\n\n".join([doc.page_content for doc in docs])
        
        prompt = f"""
        Act as a QA Automation Expert. Write a Python Selenium script.
        
        TEST CASE: "{test_case}"
        RULES: {doc_context}
        HTML:
        ```html
        {html_code}
        ```
        
        REQUIREMENTS:
        1. **Setup:** Use `webdriver_manager` with correct Selenium 4 syntax:
           ```python
           from selenium.webdriver.chrome.service import Service
           from webdriver_manager.chrome import ChromeDriverManager
           service = Service(ChromeDriverManager().install())
           driver = webdriver.Chrome(service=service)
           ```
        2. **Path:** Check if 'checkout.html' is in the current folder OR 'project_assets'.
        
        3. **Color Assertion:** Handle RGBA. Use this logic:
           `if "green" in color or "rgb(0, 128, 0)" in color or "rgba(0, 128, 0, 1)" in color:`
        
        4. **Slow Motion:** Add `import time` and insert `time.sleep(3)` after every major action.
        
        5. **Output:** Return ONLY the Python code block.
        """
        
        response = client.models.generate_content(
            model=MODEL_NAME, 
            contents=prompt
        )
        return response.text

    except Exception as e:
        return f"Error generating script: {str(e)}"