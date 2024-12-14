# blog/utils/article_utils.py
import openai
from django.conf import settings
    
openai.api_key = settings.OPENAI_API_KEY

def generate_article(prompt):
    
    response = openai.chat.completions.create(
        model='gpt-3.5-turbo', 
        messages=[
            {'role': 'system', 'content': 'You are a helpful assistant for generating blog articles.'},
            {'role': 'user', 'content': prompt}
        ],
        max_tokens=1500,
        temperature=0.7
    )

    return response
    