import os
import openai
import streamlit as st
from utils import create_database_for_link, load_documents, split_documents, get_user_input, print_answer
from dotenv import load_dotenv
import asyncio
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import DeepLake
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.callbacks import get_openai_callback
import deeplake


def main():
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
    load_dotenv()
    # Set the OpenAI API key
    os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
    os.environ['ACTIVELOOP_TOKEN'] = os.getenv('ACTIVELOOP_TOKEN')
    language_model = os.getenv('LANGUAGE_MODEL')
    
    # Page layout and title
    st.set_page_config(page_title='UnRavel APIs', layout='wide')
    st.title('UnRavel APIs')

    # Input section
    st.header('Enter the API Documentation Links')
    api_links = st.text_area('API Documentation Links (one link per line)')

    # Process and display output
    if st.button('Understand the API(s)'):
        if not api_links:
            st.warning('Please enter the API documentation links.')
        else:
            # Split the input into separate links
            api_links_list = api_links.split('\n')
            # Remove empty elements
            api_links_list = [link.strip() for link in api_links_list if link.strip()]
            
            if len(api_links_list) == 0:
                st.warning('Please enter valid API documentation links.')
            else:
                st.info('Processing the API documentation...')
                # TODO: Replace with processing logic for the API documentations
                for i, link in enumerate(api_links_list):
                    st.info(f'Processing {link}')
                    
                    # path = f"data/data_{i}"
                    # if not os.path.exists(path):
                    #     os.makedirs(path)
                    #     os.makedirs(path + "/files")
                    
                    # max_attempts = int(os.getenv('MAX_ATTEMPTS', 5)) 
                    # succ_diff = create_database_for_link(link, path, max_attempts=max_attempts)
                    
                    # docs = load_documents(path + "/files")
                    # texts = split_documents(docs)
                    
                    dataset_path = os.getenv('DATASET_PATH')
                    db = DeepLake(dataset_path=dataset_path, embedding_function=OpenAIEmbeddings(), overwrite=True)
                    # db.add_documents(texts)
                    # print('Vector database updated.')
                    
                    # if succ_diff or texts == False:
                    #     st.success(f'API {i+1} is Understood!')
                    # else:
                    #     st.error(f'Some error occured while understanding API {i+1}!')
                    
                    
                st.success('All the API(s) are Understood!')

                # Chat interface
                # if st.button('Start Chatting'):
                st.subheader('Chat Interface')
                    # Initialize retriever and set search parameters
                # db = deeplake.load(dataset_path)
                retriever = db.as_retriever()
                retriever.search_kwargs.update({
                        'distance_metric': 'cos',
                        'fetch_k': 100,
                        'maximal_marginal_relevance': True,
                        'k': 10,
                })
                model = ChatOpenAI(model_name=language_model, temperature=0.2) # gpt-3.5-turbo by default. Use gpt-4 for better and more accurate responses 

                qa = ConversationalRetrievalChain.from_llm(model, retriever=retriever)

                    # Initialize chat history
                chat_history = []


                while True:
                    user_query = st.text_input('Enter your query...')
                    print(user_query)
                    if user_query.lower() == 'quit':
                        return None

                    # Display token usage and approximate costs
                    with get_openai_callback() as tokens_usage:
                        result = qa({"question": user_query, "chat_history": chat_history})
                        chat_history.append((user_query, result['answer']))
                        st.write(f"Question: {user_query}")
                        st.write(f"Response: \n {result['answer']}")


    # Footer
    st.markdown('---')
    st.markdown('<a href="https://www.buymeacoffee.com/jaiminsg" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me a Coffee" width="150" height="40"></a>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()