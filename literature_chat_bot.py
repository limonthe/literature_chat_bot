import streamlit as st
from zhipuai import ZhipuAI
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)

# 设置页面标题和图标
st.set_page_config(
    page_title="聊天机器人",
    page_icon="🤖",
    layout="wide",  # 页面布局为宽模式
)

# 预置的API Key
predefined_api_key = "406281c034e39e55e05767ddd28fa9b3.I4A28mucE8NAUtkn"

def zhipu_chat(api_key, model, temperature, top_p, max_tokens):
    """初始化ZhipuAI客户端"""
    client = ZhipuAI(api_key=api_key)
    return client

def render_sidebar():
    """渲染设置区域并返回设置的参数"""
    st.sidebar.title("设置区域")

    # 选择是否使用预置API Key
    use_predefined_key = st.sidebar.radio(
        "选择API Key方式：", 
        ("使用预置API Key", "自定义API Key")
    )
    
    api_key = predefined_api_key if use_predefined_key == "使用预置API Key" else st.sidebar.text_input(
        "请输入您的API Key：", value=st.session_state.get("api_key", ""), type="password", placeholder="例如：sk-xxxxxxxxxxxx"
    )

    model = st.sidebar.selectbox(
        "选择模型：",
        ("glm-4-flash", "glm-4-long"),
        index=("glm-4-flash", "glm-4-long").index(st.session_state.get("model", "glm-4-flash")),
    )

    temperature = st.sidebar.slider(
        "选择采样温度 (Temperature)：",
        min_value=0.0, max_value=1.0, value=st.session_state.get("temperature", 0.95), step=0.01,
    )

    top_p = st.sidebar.slider(
        "选择核采样 (Top P)：",
        min_value=0.0, max_value=1.0, value=st.session_state.get("top_p", 0.70), step=0.01,
    )

    max_tokens = st.sidebar.number_input(
        "选择最大Token数量 (Max Tokens)：",
        min_value=1, max_value=4095, value=st.session_state.get("max_tokens", 4095), step=1,
    )

    # 保存设置到session_state
    st.session_state.api_key = api_key
    st.session_state.model = model
    st.session_state.temperature = temperature
    st.session_state.top_p = top_p
    st.session_state.max_tokens = max_tokens

    return api_key, model, temperature, top_p, max_tokens

def display_conversation():
    """显示对话历史"""
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []

    # 显示所有的问答历史
    for chat in st.session_state.conversation_history:
        if chat['role'] == 'user':
            st.markdown(f"**用户：** {chat['content']}")
        else:
            st.markdown(f"**机器人：** {chat['content']}")

def chat_with_bot(client, conversation, user_input, model, temperature, top_p, max_tokens):
    """与机器人聊天，并返回机器人的回答"""
    with st.spinner("等待机器人回复..."):
        try:
            # 添加用户输入到对话历史
            conversation.append({"role": "user", "content": user_input})

            # 进行API调用，获取机器人响应
            response = client.chat.completions.create(
                model=model,
                messages=conversation,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
            )

            assistant_response = response.choices[0].message.content
            # 添加机器人的回答到历史记录
            conversation.append({"role": "assistant", "content": assistant_response})

            # 显示机器人回答
            st.markdown(f"**机器人：** {assistant_response}")

        except Exception as e:
            logging.error(f"发生错误：{e}")
            st.error("发生错误，请重试。")

def main():
    # 页面标题
    st.title("欢迎来到聊天机器人！")
    st.markdown(
        """
        这是一个基于ZhipuAI模型的聊天机器人。请输入您的问题，机器人会尽快回答。
        """
    )

    # 渲染设置区域
    api_key, model, temperature, top_p, max_tokens = render_sidebar()

    # 检查并初始化ZhipuAI客户端
    if api_key and model:
        client = zhipu_chat(api_key, model, temperature, top_p, max_tokens)
    else:
        st.warning("请确保您已设置API Key和模型。")
        return

    # 如果对话历史不存在，初始化空对话历史
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []

    # 显示对话历史
    display_conversation()

    # 设置默认提示文本
    prompt_options = [
        "介绍俄罗斯文学概况",
        "介绍一部俄罗斯文学作品",
        "托尔斯泰的创作理念",
        "聊一聊陀思妥耶夫斯基的主要作品",
        "介绍俄国文学与西方文学的关系",
        "分析普希金的文学贡献"
    ]

    # 提供选择框让用户选择预设的提示
    selected_prompt = st.selectbox(
        "选择一个提示：",
        prompt_options,
        index=0
    )

    # 用户输入框，默认填充选择的提示
    user_input = st.text_input("用户输入：", value=selected_prompt, placeholder="在这里输入您的问题...")

    # 发送按钮
    send_button = st.button("发送")

    # 控制按钮点击或回车触发聊天
    if send_button or (user_input and st.session_state.get("input_key", False)):
        if not user_input.strip() and not send_button:
            st.error("请输入有效的内容。")
        else:
            # 调用与机器人聊天的函数
            chat_with_bot(client, st.session_state.conversation_history, user_input, model, temperature, top_p, max_tokens)

    # 页面底部说明
    st.markdown(
        """
        ----
        提示：如果遇到任何问题，请确保API Key输入正确并且可以正常访问ZhipuAI服务。
        """
    )

if __name__ == "__main__":
    main()
