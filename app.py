import streamlit as st
import tiktoken
import PyPDF2
import locale

# Define the STRINGS dictionary for all UI text
STRINGS = {
    "title": "Token Calculator",
    "description": "This app calculates the token count for your text or PDF files.",
    "results_header": "Token Calculation Results",
    "token_count_label": "Total Tokens",
    "encoding_used_label": "Encoding Used",
    "token_explanation": "Your input is broken down into {tokens} tokens using the '{encoding}' encoding. Tokens are units of text processed by AI models.",
    "input_method_label": "Choose your input method",
    "text_input_label": "Input your text here",
    "pdf_upload_label": "Upload a PDF file",
    "pdf_content_label": "Content extracted from your PDF",
    "encoding_label": "Select encoding",
    "encoding_help": "Choose an encoding to use for token calculation.",
    "calculate_button": "Calculate Tokens",
    "warning_no_input": "Please provide text or upload a PDF file.",
    "info": "Token calculation completed."
}

def get_user_language():
    try:
        lang, _ = locale.getdefaultlocale()
        return lang.split('_')[0] if lang else "en"
    except Exception:
        return "en"

def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return ""

def calculate_tokens_local(text: str, encoding_name: str = "cl100k_base") -> int:
    try:
        encoding = tiktoken.get_encoding(encoding_name)
        tokens = encoding.encode(text)
        return len(tokens)
    except Exception as e:
        st.error(f"Error in token calculation: {e}")
        return -1

def main():
    # Initialize session state
    if "token_result" not in st.session_state:
        st.session_state["token_result"] = None
    if "input_cleared" not in st.session_state:
        st.session_state["input_cleared"] = False

    user_lang = get_user_language()
    st.title(STRINGS["title"])
    st.write(STRINGS["description"])

    # Display results if available
    if st.session_state["token_result"]:
        tokens, encoding = st.session_state["token_result"]
        st.subheader(STRINGS["results_header"])

        # Center the token count using a single centered column
        col1, col2, col3 = st.columns([1, 2, 1])  # Middle column wider for emphasis
        with col2:  # Use the middle column to ensure centering
            st.markdown(
                f"<div style='text-align: center;'>"
                f"<h1 style='color: #FFFF00; border: 3px solid black; padding: 5px 10px; display: inline-block; background-color: #000000; margin: 0;'>{tokens:,}</h1>"
                f"<p style='font-size: 1.2em; margin-top: 5px;'>{STRINGS['token_count_label']}</p>"
                f"</div>",
                unsafe_allow_html=True
            )

        # Secondary details in a balanced layout
        col1, col2 = st.columns([1, 1])
        with col1:
            st.write(f"**{STRINGS['encoding_used_label']}**: {encoding}")
        with col2:
            st.write("")  # Empty for balance (optional additional info could go here)

        # Explanation below, also centered
        st.markdown(
            f"<p style='text-align: center;'>{STRINGS['token_explanation'].format(tokens=f'{tokens:,}', encoding=encoding)}</p>",
            unsafe_allow_html=True
        )
        st.divider()

    # Input form
    input_method = st.radio(STRINGS["input_method_label"], ("Text", "PDF Upload"))

    with st.form(key="input_form"):
        prompt = ""
        if input_method == "Text":
            prompt = st.text_area(
                STRINGS["text_input_label"],
                value="" if st.session_state["input_cleared"] else "",
                height=200,
                key="text_input"
            )
        else:
            uploaded_file = st.file_uploader(
                STRINGS["pdf_upload_label"],
                type=["pdf"],
                key="pdf_upload"
            )
            if uploaded_file:
                prompt = extract_text_from_pdf(uploaded_file)
                st.write(STRINGS["pdf_content_label"])
                st.text_area("PDF Content", prompt, height=200, disabled=True, key="pdf_content")

        selected_encoding = st.selectbox(
            STRINGS["encoding_label"],
            ["cl100k_base", "p50k_base", "r50k_base"],
            index=0,
            help=STRINGS["encoding_help"],
            key="encoding_select"
        )

        submit_button = st.form_submit_button(label=STRINGS["calculate_button"])

    # Process submission
    if submit_button:
        if prompt:
            local_tokens = calculate_tokens_local(prompt, encoding_name=selected_encoding)
            if local_tokens != -1:  # Ensure calculation succeeded
                st.session_state["token_result"] = (local_tokens, selected_encoding)
                st.session_state["input_cleared"] = True  # Clear input after successful calculation
                st.rerun()  # Refresh to show results
        else:
            st.warning(STRINGS["warning_no_input"])
            st.session_state["input_cleared"] = False

    # Reset input_cleared flag after displaying results
    if st.session_state["input_cleared"] and not submit_button:
        st.session_state["input_cleared"] = False

    st.info(f"{STRINGS['info']} (Detected language: {user_lang})")

if __name__ == "__main__":
    main()
