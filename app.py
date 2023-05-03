import streamlit as st
import re
import openai
from scripts.qav import get_completion, get_thoughts, evaluate_answer,select_mode_based_on_sentiment_and_keywords
from dotenv import load_dotenv
import os

# load_dotenv()  # Load environment variables from .env file

st.set_page_config(
    page_title='QAV智能体多角色协作演示', 
    page_icon='./images/favicon.ico',
    layout='wide',
    menu_items={
        'Get help': 'https://www.ai-avatar.org/QAV',
        'Report a Bug': 'mailto:jerry.zhang@ai-avatar.org',
        'About':'https://www.ai-avatar.org'
     }
    )


def main():
    # Set default role names
    Role_Q = "Q"
    Role_A = "A"
    Role_V = "V"

    # Define colors for Q, A, and V
    q_color = "blue"
    a_color = "green"
    v_color = "red"

    # 定义不同的mode
    models = ["summarize", "paraphrase", "generate_response", "ask_details", "ask_reason", "challenge", "ask_example", "ask_implications", "related_topics", "go_deeper"]

    st.write("演示Q（提问）、A（回答）和V（评估/验证）智能体协作。输入一个问题，开始演示:")
    
    user_question = st.text_input("")

    if user_question:
        conversation = [{"role": Role_Q, "content": user_question}]
        st.markdown(f'<p style="color:{q_color};">**{Role_Q}:** {user_question}</p>', unsafe_allow_html=True)

        while len(conversation) < 50:  # Limit conversation to 50 turns (adjust as needed)
            # A answers the question
            answer = get_completion(user_question)
            conversation.append({"role": Role_A, "content": answer})
            st.markdown(f'<p style="color:{a_color};">**{Role_A}:** {answer}</p>', unsafe_allow_html=True)

            # Evaluate the answer
            rating = evaluate_answer(user_question, answer)
            conversation.append({"role": Role_V, "content": f"{rating}/10"})
            st.markdown(f'<p style="color:{v_color};">**{Role_V}:** {rating}/10</p>', unsafe_allow_html=True)

            

            if rating >= 3:
                # Generate next question
                selected_model = select_mode_based_on_sentiment_and_keywords(user_question, answer)    
                
                thoughts = get_thoughts(answer, [selected_model])
                user_question = get_completion(thoughts)
                conversation.append({"role": Role_Q, "content": user_question})
                st.markdown(f'<p style="color:{q_color};">**{Role_Q}:** {user_question}</p>', unsafe_allow_html=True)
            else:
                st.write("请给出更好的回答.")
                # Request a better answer
                V_thoughts = get_thoughts(answer, "related_topics")
                answer = get_completion(f"这个回答不好，根据我的思考 {V_thoughts} 重新回答。")
                #chang_mind [todo] add new function to change mind.
                conversation.append({"role": Role_A, "content": answer})
                selected_model = select_mode_based_on_sentiment_and_keywords(user_question, answer)    
                thoughts = get_thoughts(answer, [selected_model])
                user_question = get_completion(thoughts)
                st.markdown(f'<p style="color:{a_color};">**{Role_A}:** {answer}</p>', unsafe_allow_html=True)

        st.write("End of conversation.")


# openai.api_key = os.getenv("OPENAI_API_KEY")

# Create a container for the logo, title, and image
header_container = st.container()

# Divide the container into 3 columns for the logo, title, and image
logo_column, title_column, image_column = header_container.columns([1, 4, 1])

# Add the logo to the left column
logo_column.image("./images/logo.png", width=80)

# Add the title to the center column
title_column.title("QAV智能体多角色协作演示")

# Add the image to the right column
image_column.image("./images/iamte-annie.png", width=80)

# Your main app content here

# Check if the session state is already initialized
if "openai_api_key" not in st.session_state:
    st.session_state.openai_api_key = None

if not st.session_state.openai_api_key:
    # Create a sidebar for OpenAI API key input
    st.sidebar.title("OpenAI API Key")
    st.session_state.openai_api_key = st.sidebar.text_input("输入你的OpenAI API key", type="password")

if st.session_state.openai_api_key:
    openai.api_key = st.session_state.openai_api_key

    main()
else:
    st.warning("请在左边菜单栏里输入你的OpenAI API key.")


# Add a footer to the bottom of the page
footer = """
    <style>
        .footer {
            position: fixed;
            bottom: 0;
            width: 100%;
            background-color: white;
            padding: 10px;
            text-align: center;
        }
    </style>
    <div class="footer">
        <p>Copyright &copy; 2023 艾凡达实验室. All rights reserved.</p>
    </div>
"""
st.markdown(footer, unsafe_allow_html=True)
