##################################################
# Brian Lesko
# 2024-12-24
# In this Low code UI, we interact with a large language transformer model (LLM) through an Application Programming Interface (API).

import streamlit as st
from aitools import AIClient
import base64
import time

st.set_page_config(page_title='LLM0',page_icon='')
tailwind_cdn = """
<link href="https://cdn.jsdelivr.net/npm/daisyui@4.12.23/dist/full.min.css" rel="stylesheet" type="text/css" />
<script src="https://cdn.tailwindcss.com"></script>
"""
st.markdown(tailwind_cdn, unsafe_allow_html=True)
hide_streamlit_style = "<style>#MainMenu, footer, header {visibility: hidden;}</style>"
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

myAiClients = []
myAiClients.append(AIClient('xai'))
myAiClients.append(AIClient('openai'))
myAiClients.append(AIClient('openai',model_name='o3-mini'))
myAiClients.append(AIClient('google'))

st.markdown('<h1 style="text-align: center; padding-top: 60px;">AI Chat Comparison</h1>', unsafe_allow_html=True)
labels = []
for ai in myAiClients:
    if ai.api_key is None:
        st.error(f"Please enter an API key for {ai.company_name} in keys.json")
        st.stop()
    labels.append(f'''<div class="badge badge-ghost badge-lg"><div class="p-4 m-4">{ai.model_name}</div></div>''')
st.html(f'''<div style="text-align: center; class="flex flex-row justify-center items-center mx-auto">{'\n'.join(labels)}</div>''')

Chat = st.empty()

if "messages" not in st.session_state:
    st.session_state["messages"] = []

User = st.empty()
Stream = st.empty()

prompt = st.chat_input("Write a message")

messages = []
streams_finished = False
while prompt and not streams_finished:
    streams_finished = True
    messages.append({"role": "user", "content": prompt})
    Stream.html("""
                <div style="display: flex; justify-content: center; align-items: center; height: 100%; margin: 20px 0;">
                    <span class="loading loading-spinner loading-xl"></span>
                </div>
                """)
    User.markdown(f""" ##  {prompt} """, unsafe_allow_html=True)
    
    #loop through the streams
    all_responses = []
    dict_responses = {}
    for ai in myAiClients:
        stream = ai.get_stream(messages)
        chunks = list(stream)
        # if any stream has no chunks, it means it's finished
        if len(chunks) == 0:
            streams_finished = True
            break
        content = ai.get_content(chunks)
        checked = '''checked="checked"''' if ai.company_name == myAiClients[0].company_name else ""
        html = f"""
        <input type="radio" name="my_tabs" class="flex grow tab p-4 m-4 w-40" aria-label="{ai.model_name}" {checked}"/>
        <div class="tab-content bg-base-100 border-base-300 rounded-box p-8 m-8"><div style="padding: 20px; margin: 20px;">{content}</div></div>"""
        all_responses.append(html)
        # dictionary of the model name and the content
        dict_responses[ai.model_name] = content

    my_html = f"""
                <div role="tablist" class="tabs tabs-lifted p-6">
                    {'\n'.join(all_responses)}
                </div>
            """
    Stream.html(my_html)

    # JUDGE MODEL
    messages = []
    messages.append({"role": "user", "content": prompt})
    messages.append({"role": "user", "content": str(dict_responses)})
    messages.append({"role": "system", "content": "Which response is best for the user's question? Take into account the user's question and the responses, their clarity efficiency and accuracy. Answer with the name only"})

    # use a judge model to select the best response
    judge = AIClient('openai',model_name='gpt-4o')
    stream = judge.get_stream(messages)
    time.sleep(1)
    chunks = list(stream)
    content = judge.get_content(chunks)
    st.write(f"Judge gpt-4o declares the winner: {content}")