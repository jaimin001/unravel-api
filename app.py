import streamlit as st
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import DeepLake
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
import os
from dotenv import load_dotenv


load_dotenv()

st.title('UnRavel APIs')

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