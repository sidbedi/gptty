__name__ = "gptty.context"
__author__ = "Sig Janoska-Bedi"
__credits__ = ["Sig Janoska-Bedi"]
__version__ = "0.2.4"
__license__ = "MIT"
__maintainer__ = "Sig Janoska-Bedi"
__email__ = "signe@atreeus.com"


import click
import tiktoken
from textblob import TextBlob
from collections import Counter, defaultdict
from nltk.corpus import stopwords


YELLOW = "\033[1;33m"
RESET = "\033[0m"


def get_token_count(s, model_name):
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(model_name)
    num_tokens = len(encoding.encode(s))
    return num_tokens

def return_most_common_phrases(text:str, weight_recent=True) -> list:

    # Extract noun phrases using TextBlob
    blob = TextBlob(text)
    noun_phrases = blob.noun_phrases

    # Remove stopwords from noun phrases
    stop_words = set(stopwords.words('english'))
    filtered_noun_phrases = []
    for np in noun_phrases:
        words = np.split()
        filtered_words = [word for word in words if word not in stop_words]
        if filtered_words:
            filtered_noun_phrases.append(' '.join(filtered_words))

    if not weight_recent:

        # Count the frequency of the noun phrases
        noun_phrase_counts = Counter(filtered_noun_phrases)

        # Get the most frequent key phrases
        return [phrase for phrase, count in noun_phrase_counts.most_common()]

    # Count the weighted frequency of the noun phrases
    noun_phrase_weighted_counts = defaultdict(int)
    total_phrases = len(filtered_noun_phrases)

    for i, phrase in enumerate(filtered_noun_phrases):
        weight = (i + 1) / total_phrases  # Assign a higher weight to phrases that appear later in the text
        noun_phrase_weighted_counts[phrase] += weight

    # Get the most frequent key phrases
    return [phrase for phrase, count in sorted(noun_phrase_weighted_counts.items(), key=lambda x: x[1], reverse=True)]

def get_context(tag: str, 
                max_context_length: int, 
                output_file: str, 
                model_name:str, 
                context_keywords_only: bool = True, 
                additional_context: str = None,
                model_type: str = None, 
                question: str = None, 
                debug: bool = False):

    if len(tag) < 1:
        if model_type == 'v1/chat/completions':

            content = [{"role": "user", "content": question}]

            if debug:
                click.echo(YELLOW + '-' * 25)
                click.echo(f'[debug]\nmodel: {model_name}\ntokens: {get_token_count(question, model_name)}\nwords: {len(question.split()) }\ntext: {question}') # debug - print the context to see what it looks like
                click.echo('-' * 25 + RESET)
                
            return content

        else:
            if debug:
                click.echo(YELLOW + '-' * 25)
                click.echo(f'[debug]\nmodel: {model_name}\ntokens: {get_token_count(question, model_name)}\nwords: {len(question.split())}\ntext: {question}') # debug - print the context to see what it looks like
                click.echo('-' * 25 + RESET)

            return question

    with open(output_file, 'r') as f:
        text = f.read().strip().split('\n')

    if model_type == 'v1/chat/completions':
        context = []

        for row in reversed(text):
            data = [item.strip() for item in row.split('|')]

            if (sum(len(item["content"].split()) for item in context) + len(data[2].split()) + len(data[3].split()) + len(question.split())) > max_context_length:
                break

            if data[1] == tag:
                context = [{"role": "assistant", "content": data[3]}] + context
                context = [{"role": "user", "content": data[2]}] + context

        context.append({"role": "user", "content": question})
        
        if debug:
            token_count = " ".join([x['content'] for x in context])
            click.echo(YELLOW + '-' * 25)
            click.echo(f'[debug]\nmodel: {model_name}\ntokens: {get_token_count(token_count, model_name)}\nwords: {sum(len(item["content"].split()) for item in context)}\ntext: {context}') # debug - print the context to see what it looks like
            click.echo('-' * 25 + RESET)


    else:
        context = ""
        for row in text:
            data = [item.strip() for item in row.split('|')]

            if data[1] == tag:
                context += ' ' + data[2] + ' ' + data[3]

        if context_keywords_only:
            phrases = return_most_common_phrases(context)
            context = ""

            for phrase in phrases:
                if (len(context.split()) + len(phrase.split()) + len(question.split())) > max_context_length:
                    break
                context += " " + phrase

        else:
            c = ""
            context_words = context.split()

            for i in range(len(context_words)):
                if (len(c.split()) + len(question.split())) >= max_context_length:
                    break
                c += ' ' + context_words[i]

            context = c.strip()

        context = context.strip() + ' ' + question
        
        if debug:
            click.echo(YELLOW + '-' * 25)
            click.echo(f'[debug]\nmodel: {model_name}\ntokens: {get_token_count(context, model_name)}\nwords: {len(context.split())}\ntext: {context}') # debug - print the context to see what it looks like
            click.echo('-' * 25 + RESET)

    return context