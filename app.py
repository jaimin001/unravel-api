import streamlit as st
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import DeepLake
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
import os
from dotenv import load_dotenv
from utils import create_database_for_link, load_documents, split_documents


load_dotenv()

# Set up DeepLake vector store
dataset_path = os.getenv('DATASET_PATH')
db = DeepLake(dataset_path=dataset_path, embedding_function=OpenAIEmbeddings(), overwrite=True)

# Set up OpenAI language model
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')


def generate_response(input_text):
    model = OpenAI(model_name='gpt-3.5-turbo', api_key=openai_api_key)
    response = model(input_text)
    st.info(response)

chat_history = []

###########
st.set_page_config(page_title='UnRavel APIs', layout='wide')
st.title('UnRavel APIs')

st.header('Enter the API Documentation Links')
api_link = st.text_area('API Documentation Link')

if st.button('Understand the API(s)'):
    if not api_link:
        st.warning('Please enter the API documentation links.')
    else:
        api_link = api_link.strip()
        
        st.info('Processing the API documentation...')
        st.info(f'Processing {api_link}')
        
        path = f"data/data"
        if not os.path.exists(path):
            os.makedirs(path)
            os.makedirs(path + "/files")
        
        max_attempts = int(os.getenv('MAX_ATTEMPTS', 5)) 
        succ_diff = create_database_for_link(api_link, path, max_attempts=max_attempts)
        
        docs = load_documents(path + "/files")
        texts = split_documents(docs)
        
        dataset_path = os.getenv('DATASET_PATH')
        db = DeepLake(dataset_path=dataset_path, embedding_function=OpenAIEmbeddings(), overwrite=True)
        db.add_documents(texts)
        print('Vector database updated.')
        
        if succ_diff or texts == False:
            st.success(f'API is Understood!')
        else:
            st.error(f'Some error occured while understanding API!')
            
###########

with st.form('my_form'):
    text = st.text_area('Enter text:', 'Ask a question or say something...')
    submitted = st.form_submit_button('Submit')

    if not openai_api_key.startswith('sk-'):
        st.warning('Please enter your OpenAI API key!', icon='⚠')

    if submitted and openai_api_key.startswith('sk-'):
        # Add input text to DeepLake vector store
        # db.add_documents([text])

        # Search for similar documents in the vector store
        retriever = db.as_retriever()
        retriever.search_kwargs.update({
                        'distance_metric': 'cos',
                        'fetch_k': 100,
                        'maximal_marginal_relevance': True,
                        'k': 10,
        })
        model = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.2) # gpt-3.5-turbo by default. Use gpt-4 for better and more accurate responses 

        qa = ConversationalRetrievalChain.from_llm(model, retriever=retriever)

        print(text, chat_history)
        result = qa({"question": text, "chat_history": chat_history})
        chat_history.append((text, result['answer']))
        st.write(f"Question: {text}")
        st.write(f"Response: \n {result['answer']}")
        print(result['answer'])