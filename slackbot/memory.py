import  pinecone
import openai
import os
from openai.embeddings_utils import get_embedding
from typing import List, Dict, Union

PINECONE_API_KEY = os.environ["PINECONE_API_KEY"]
PINECONE_ENVIRONMENT = os.environ["PINECONE_ENVIRONMENT"]

# Initialize Pinecone client with your API key
pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)

def create_index_name(channel_name:str, bot_name:str) -> str:
    return f"{channel_name}_{bot_name}"

def create_index(index_name:str) -> pinecone.Index:
    # Create a new Pinecone index
    if index_name not in pinecone.list_indexes():
        pinecone.create_index(index_name, dimension=300)
    return pinecone.Index(index_name)


# Function to vectorize a conversation using a suitable embedding model
def vectorize_conversation(conversation: str) -> List[Dict[str,Union[str,List[float]]]]:
    chunks_with_embeddings = []
    embedding = get_embedding(conversation, engine='text-embedding-ada-002')
    chunks_with_embeddings.append({"text": conversation, "embedding": embedding})
    return chunks_with_embeddings

# Function to add a conversation to the index
def add_conversation_to_index(conversation, conversation_id, bot_name, channel_name):
    index_name = create_index_name(channel_name, bot_name)
    vector = vectorize_conversation(conversation)
    pinecone.upsert_items(index_name, [{"id": conversation_id, "vector": vector}])

# Function to search for similar conversations given a new input
def search_similar_conversations(query, index: pinecone.Index, top_k=5):
    query_vector = vectorize_conversation(query)
    response = pinecone.query(index, query_vector, top_k=top_k)
    similar_conversations = response["items"]
    return similar_conversations

def search_docs(query, index: pinecone.Index):
  xq = openai.Embedding.create(input=query, engine="text-embedding-ada-002")['data'][0]['embedding']
  res = index.query([xq], top_k=5, include_metadata=True)
  chosen_text = []
  for match in res['matches']:
    chosen_text = match['metadata']
  return res['matches']     

def construct_prompt(query, index: pinecone.Index):
  matches = search_docs(query, index)

  chosen_text = []
  for match in matches:
    chosen_text.append(match['metadata']['text'])

  prompt = """Answer the question as truthfully as possible using the context below, and if the answer is no within the context, say 'I don't know.'"""
  prompt += "\n\n"
  prompt += "Context: " + "\n".join(chosen_text)
  prompt += "\n\n"
  prompt += "Question: " + query
  prompt += "\n"
  prompt += "Answer: "
  return prompt


def answer_question(query, index: pinecone.Index):
  prompt = construct_prompt(query, index)
  res = openai.Completion.create(
      prompt=prompt,
      model="text-davinci-003",
      max_tokens=500,
      temperature=0.0,
  )
  
  return res.choices[0].message