import os
import streamlit as st
from utils import create_database_for_link, load_documents, split_documents
from dotenv import load_dotenv
import asyncio
import nest_asyncio


def main():
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
    # nest_asyncio.apply()
    load_dotenv()
    # Set the OpenAI API key
    os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

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
                    
                    path = f"data/data_{i}"
                    if not os.path.exists(path):
                        os.makedirs(path)
                        os.makedirs(path + "/files")
                    
                    max_attempts = int(os.getenv('MAX_ATTEMPTS', 5)) 
                    succ_diff = create_database_for_link(link, path, max_attempts=max_attempts)
                    
                    docs = load_documents(path + "/files")
                    texts = split_documents(docs)
                    
                    if succ_diff or texts == False:
                        st.success(f'API {i+1} is Understood!')
                    else:
                        st.error(f'Some error occured while understanding API {i+1}!')
                    
                    
                    
                st.success('All the API(s) are Understood!')

                # Chat interface
                if st.button('Start Chatting'):
                    st.subheader('Chat Interface')
                    user_query = st.text_input('Enter your query')

                    if user_query:
                        # TODO: Replace with search logic
                        # TODO: Display search results
                        pass


    # Footer
    st.markdown('---')
    st.markdown('<a href="https://www.buymeacoffee.com/jaiminsg" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me a Coffee" width="150" height="40"></a>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()