##################################################
# Brian Lesko
# 2024-12-24
# In this Low code UI, we interact with a large language transformer model (LLM) through an Application Programming Interface (API).

import streamlit as st
from aitools import AIClient
import base64
import time

def write_stream(stream):
    text = ""
    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content is not None: 
            text += content
            with Stream:
                st.markdown(f"""<div style="height: 80vh; background-color: white;" class="flex flex-col"> <div>{text}</div>""", unsafe_allow_html=True)
    return text

 # {"Original" if i == len(messages) else "Iteration" + str(len(messages) - i)}
def write_recursive_stream(stream, messages):
    tab_name = "Most concise"
    past_tabs = " ".join(f'''
    <input type="radio" name="my_tabs_2" role="tab" class="tab p-2 m-2" aria-label="tabn" /> 
    <label for="tab_{i}" class="p-2 m-2 tab-label"><!-- This is the visible text -->{ "Original" if i == len(messages) else f"Iteration {len(messages) - i}" }
    </label>
    <div role="tabpanel" class="tab-content bg-base-100 border-base-300 rounded-box p-6 m-6">
        <div style="padding: 10px; margin: 10px;">
            {s}
        </div>
    </div>''' for i, s in enumerate(reversed(messages)))

    text = "\n"
    for chunk in stream:
        chunk_text = chunk.choices[0].delta.content
        if chunk_text is not None:
            text += chunk_text
            # build our HTML
            my_html = f"""
                <div role="tablist" class="tabs tabs-lifted p-6">
                    <input type="radio" name="my_tabs_2" role="tab" class="tab" aria-label="{tab_name}" checked="checked" />
                    <label for="tab" class="p-2 m-2 tab-label"> 
                        <!-- This is the visible text -->
                        Most Concise
                    </label>
                    <div role="tabpanel" class="tab-content bg-base-100 border-base-300 rounded-box p-6 m-6">
                        <div style = "padding: 10px; margin: 10px;">
                        {text}
                        </div>
                    </div>{past_tabs}
                </div>
            """
            # Display in Streamlit
            # (If you only want to show the final result once all chunks have arrived)
            with Stream:
                st.markdown(f"""<div style="min-height: 80vh; background-color: white;" class="flex flex-col">{my_html}</div>""",unsafe_allow_html=True)
    return text

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
myAiClients.append(AIClient('google'))

for ai in myAiClients:
    if ai.api_key is None:
        st.error(f"Please enter an API key for {ai.company_name} in keys.json")
        st.stop()
    ai.setup()
    st.write(f"{ai.company_name} is ready")


Title = st.empty()
Title.markdown('<h1 style="text-align: center; padding-top: 60px;">AI Chat Comparison</h1>', unsafe_allow_html=True)
Chat = st.empty()

#file = Upload.file_uploader("", accept_multiple_files=False)
#if file: st.session_state.file = st.session_state.myai._reduce_image_size(file)
#if "file" in st.session_state:
#    b64 = st.session_state.file
#    st.html(f"""
#        <div style="text-align: center; padding-top: 40px; padding-bottom: 20px;">
#            <img src="data:image/png;base64,{b64}" alt="Base64 Image" style="max-width: 100%; height: auto; border-radius: 10px;">
#        </div>
#    """)

if "messages" not in st.session_state:
    st.session_state["messages"] = []
else:
    Title.empty()
    #Upload.empty()

# Display all the historical messages
def write_history(messages):
    to_write = [""]
    for msg in messages:
        if msg["role"] == "system":
            continue  # Skip system messages
        if msg["role"] == "user":
            to_write.append("\n ##  " + msg["content"])
        else: 
            to_write.append(msg["content"])
    History.markdown(f"<div style='padding-top: 40px;'>{"\n".join(to_write)}</div>", unsafe_allow_html=True)

def write_msg(msg):
    if isinstance(msg["content"], str):  # This is a text message
        if msg["role"] == "user":
            st.markdown(f"<h2 style='padding-top: 40px;'>{msg['content']}</h2>", unsafe_allow_html=True)
        else:
            st.markdown(f'''<p style="padding: 0; margin: 0;"> {msg["content"]} </p>''', unsafe_allow_html=True)
    else:  # This is an image message
        url = next(item["image_url"]["url"] for item in msg["content"] if item["type"] == "image_url")
        st.markdown(f"<h2 style='padding-top: 40px;'>{msg['content'][1]['text']}</h2>", unsafe_allow_html=True)

History = st.empty()
#write_history(st.session_state.messages)
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
        <input type="radio" name="my_tabs" class="tab" aria-label="{ai.company_name}" {checked}/>
        <div class="tab-content bg-base-100 border-base-300 rounded-box p-6 m-6"><div style = "padding: 10px; margin: 10px;">{content}</div></div>"""
        all_responses.append(html)
    
    my_html = f"""
                <div role="tablist" class="tabs tabs-lifted p-6">
                    {'\n'.join(all_responses)}
                </div>
            """
    Stream.html(my_html)

    #st.session_state.messages.append(messages[-1])

st.session_state.messages=messages