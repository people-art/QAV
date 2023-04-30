import openai
import random
import re

# Set default role names
Role_Q = "Q"
Role_A = "A"
Role_V = "V"


def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]


# 多种模式的再提问方式

def get_thoughts(answer, mode):
    if mode == "summarize":
        # summarize answer into a single sentence
        prompt = f"""
        Summarize the answer into a single sentence: ```{answer}```.
        """
        thoughts = get_completion(prompt)
        return thoughts
    elif mode == "paraphrase":
        # paraphrase answer into different words
        prompt = f"""
        Paraphrase the answer: ```{answer}```.
        """
        thoughts = get_completion(prompt)
        return thoughts
    elif mode == "generate_response":
        # generate a new response based on the answer
        prompt = f"""
        Generate a new response based on the answer: ```{answer}```.
        """
        thoughts = get_completion(prompt)
        return thoughts
    elif mode == "ask_details":
        # ask for more details about the answer
        prompt = f"""
        Ask for more details about the answer: ```{answer}```.
        """
        thoughts = get_completion(prompt)
        return thoughts
    elif mode == "ask_reason":
        # ask for the reason behind the answer
        prompt = f"""
        Ask for the reason behind the answer: ```{answer}```.
        """
        thoughts = get_completion(prompt)
        return thoughts
    elif mode == "challenge":
        prompt = f"""
        Challenge the answer or raise a counterpoint: ```{answer}```.
        """
        thoughts = get_completion(prompt)
        return thoughts

    elif mode == "ask_example":
        prompt = f"""
        Ask for an example related to the answer: ```{answer}```.
        """
        thoughts = get_completion(prompt)
        return thoughts

    elif mode == "ask_implications":
        prompt = f"""
        Ask about the potential implications or consequences of the answer: ```{answer}```.
        """
        thoughts = get_completion(prompt)
        return thoughts

    elif mode == "related_topics":
        prompt = f"""
        Suggest related concepts or topics based on the answer: ```{answer}```.
        """
        thoughts = get_completion(prompt)
        return thoughts

    elif mode == "go_deeper":
        prompt = f"""
        Ask for a deeper explanation or analysis of a specific aspect of the answer: ```{answer}```.
        """
        thoughts = get_completion(prompt)
        return thoughts

    else:
        return answer


# 设置评估者角色 V及其方法
# 评估者（V）角色，以评估A的回答。评估者可以根据准确性、相关性、详细程度等方面对回答进行评分
# 您是对的，评估函数可以根据具体任务和环境进行定制。不同的任务可能需要不同的评估标准，您可以根据实际需求为评估函数添加更多规则。以下是一些建议：

# 任务相关性：根据问题的具体主题，您可以要求评估者关注回答中特定关键词或概念的存在。

# 结构性：您可以要求评估者关注回答的结构，例如是否包含引言、主要观点和结论等。

# 逻辑性：评估者可以根据回答的逻辑连贯性进行评分。例如，您可以要求评估者检查回答是否包含支持论点的论据或示例。

# 语言表达：您可以要求评估者关注回答的语言表达，例如语法、拼写和清晰度等。

# 要根据这些标准修改评估函数，您可以在evaluate_answer函数中添加相应的提示。例如：


def evaluate_answer(question, answer):
    prompt = f"""
    You are ```{Role_V}```.\
    The question is: {question}\
    The answer is: {answer}\
    Rate the quality of the answer on a scale of 1 to 10.
    """

    rating_text = get_completion(prompt)
    match = re.search(r'\d+', rating_text)

    if match:
        rating = int(match.group())
    else:
        rating = 1  # or an alternative value when no rating is found

    return rating


# 获取A回答的情感

def get_sentiment(answer):
    prompt = f"Analyze the sentiment of the following text: ```{answer}```. Is it positive, negative, or neutral?"
    sentiment = get_completion(prompt).strip().lower()
    return sentiment


mode_keywords = {
    "summarize": ["summary", "overview", "brief"],
    "paraphrase": ["rephrase", "paraphrase", "different words"],
    "generate_response": ["new response", "alternative", "another answer"],
    "ask_details": ["details", "more information", "elaborate"],
    "ask_reason": ["reason", "cause", "why"],
    "challenge": ["challenge", "disagree", "counterpoint"],
    "ask_example": ["example", "instance", "case"],
    "ask_implications": ["implications", "consequences", "results"],
    "related_topics": ["related", "connected", "similar"],
    "go_deeper": ["deeper", "in-depth", "analysis"]
}


# 根据情感和关键字选择合适的模式

def select_mode_based_on_sentiment_and_keywords(question, answer):
    sentiment = get_sentiment(answer)
    
    positive_modes = ["ask_details", "ask_example", "related_topics"]
    negative_modes = ["challenge", "ask_reason", "ask_implications"]
    neutral_modes = ["summarize", "paraphrase", "generate_response"]
    
    if sentiment == "positive":
        mode_list = positive_modes
    elif sentiment == "negative":
        mode_list = negative_modes
    else:
        mode_list = neutral_modes

    selected_mode = None
    max_matches = 0
    
    for mode, keywords in mode_keywords.items():
        if mode not in mode_list:
            continue
            
        matches = sum([1 for keyword in keywords if keyword in question.lower()])
        
        if matches > max_matches:
            max_matches = matches
            selected_mode = mode
            
    if not selected_mode:
        selected_mode = random.choice(mode_list)
        
    return selected_mode

# packgae all the functions into a single function
