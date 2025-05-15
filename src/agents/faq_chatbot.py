
from langchain_openai import AzureChatOpenAI
from langchain.schema import SystemMessage
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory, FileChatMessageHistory
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_text_splitters import CharacterTextSplitter
from pinecone import Pinecone
from openai import AzureOpenAI
from itertools import cycle
from shutil import get_terminal_size
from threading import Thread
from time import sleep
 
 
import warnings                         #warning code
warnings.filterwarnings("ignore")
 
print("\033[31m!!!!!!ALL WARNINGS ARE DISABLED!!!!!!!!\033[0m")
 
#Following is the code to create a loading wheel
class Loader:
    def __init__(self, desc="Loading...", timeout=0.1):
        self.desc = desc
        self.timeout = timeout
 
        self._thread = Thread(target=self._animate, daemon=True)
        self.steps = ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]
        self.done = False
 
    def start(self):
        self._thread.start()
        return self
 
    def _animate(self):
        for c in cycle(self.steps):
            if self.done:
                break
            print(f"\r{self.desc} {c}", flush=True, end="")
            sleep(self.timeout)
 
    def __enter__(self):
        self.start()
 
    def stop(self):
        self.done = True
        cols = get_terminal_size((80, 20)).columns
        print("\r" + " " * cols, end="", flush=True)
 
    def __exit__(self, exc_type, exc_value, tb):
        # handle exceptions with those variables ^
        self.stop()
############################################################################################################
 
pinecone_api_key = "e1495398-1144-4887-8d02-f5d85998ca3d"
openai_api_type_local = "azure"
openai_api_base_local = "https://eygenaistudio-openai-dev.openai.azure.com/"
openai_api_version_local = "2024-05-01-preview"
openai_api_key_local = "07362a79cd45421b99f245cda89c71fb"
 
client = AzureOpenAI(
  api_key = openai_api_key_local,  
  api_version = openai_api_version_local,
  azure_endpoint = openai_api_base_local
)
 
def langchain_classes(system_message, answer):
    my_llm = AzureChatOpenAI(
    deployment_name="gpt-4",
    model_name="gpt-4",
    openai_api_key=openai_api_key_local,
    openai_api_type=openai_api_type_local,
    openai_api_version=openai_api_version_local,
    azure_endpoint=openai_api_base_local
    )
    my_history = FileChatMessageHistory('chat_history.json')
 
    my_memory = ConversationBufferMemory(
        memory_key='chat_history',
        chat_memory=my_history,
        return_messages=True
    )
 
 
    my_prompt = ChatPromptTemplate(
        input_variables=['chat_history', 'content'],
        messages=[
            #Add an intermediate step to compare user question with DB question and ask AI to respond accordingly.
            SystemMessage(content = system_message + answer),
            MessagesPlaceholder(variable_name = 'chat_history'),
            HumanMessagePromptTemplate.from_template('{content}')
        ]
    )
    chain = LLMChain(
        llm=my_llm,
        prompt=my_prompt,
        memory=my_memory,
        verbose=False
    )
    return chain
 
def nohistory(system_message, answer):
    my_llm = AzureChatOpenAI(
    deployment_name="gpt-35-turbo",
    model_name="gpt-35-turbo",
    openai_api_key=openai_api_key_local,
    openai_api_type=openai_api_type_local,
    openai_api_version=openai_api_version_local,
    azure_endpoint=openai_api_base_local
    )
 
 
    my_prompt = ChatPromptTemplate(
        input_variables=['content'],
        messages=[
            #Add an intermediate step to compare user question with DB question and ask AI to respond accordingly.
            SystemMessage(content = system_message + answer),
            HumanMessagePromptTemplate.from_template('{content}')
        ]
    )
    chain = LLMChain(
        llm=my_llm,
        prompt=my_prompt,
        verbose=False
    )
    return chain
 
def chunk_loader():
    loader = CSVLoader(
        file_path="FAQs.csv",
        csv_args={
            "delimiter": ",",
            "quotechar": '"',
            "fieldnames": ["index","question", "answer", "rating", "seprator"],
        },
    )
    data = loader.load()
   
    text_splitter = CharacterTextSplitter(separator='|')  
    chunks = text_splitter.split_documents(data)
    return chunks
 
def get_embedding(text_to_embed):
  response = client.embeddings.create(
      model= "text-embedding-ada-002",
      input=[text_to_embed]
  )
  embedding = response.data[0].embedding
  return embedding
 
#def Chathistory():
    #history
 
def prompt_and_response(result, user_prompt, bool):
    pc = Pinecone(api_key=pinecone_api_key, ssl_verify=False)
    index = pc.Index("csai")
    query_result = index.query(vector=result, top_k=1, include_metadata=True)
    first_id = query_result['matches'][0]['id']
    id = int(first_id)
    chunks = chunk_loader()
    page_content = chunks[id].page_content
    answer_start = page_content.find('answer:') + len('answer:')
    rating_start = page_content.find('\nrating:', answer_start)
    answer = page_content[answer_start:rating_start].strip()
    system_message ="You are an Expert Chatbot for EY Bank whose primary goal is to analyze all the questions asked to you and provide all relevant answers in details." \
                    "Provide concise replies that are polite and professional." \
                    "Answer questions truthfully based on provided contextual data only." \
                    "Do not answer questions that are not provided in the contextual data and respond with I can only help with given context related questions you may have. Contextual data: "
    if bool==True:
        chain = langchain_classes(system_message, answer)
    else:
        chain =  nohistory(system_message, answer)
    response = chain.invoke({'content':user_prompt})
    return(response["text"])
 
def main_chat(user_prompt,bool):
 
    result = get_embedding(user_prompt)
    excel_response = prompt_and_response(result, user_prompt, bool)
    return excel_response
 
def Testing():
    while True:
        content =input('Your prompt: ')
        if content in ['quit', 'exit', 'bye']:
            print('Bye Bye!')
            break
        if __name__ == "__main__":
            loader = Loader("Generating response...", 0.05).start()
            p= main_chat(content,True)
            loader.stop()
        print(p)
 
#Enable Testing() for prompts
#Testing()