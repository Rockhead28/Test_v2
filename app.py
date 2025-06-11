def main():
    st.set_page_config(layout="wide", page_title="AI Resume Builder")
    st.title("📄 AI-Powered Resume Builder")
    st.write("A modular application to parse resumes and generate new ones from a template.")

    # Get OpenAI API Key from Streamlit Secrets
    api_key = st.secrets.get("OPENAI_API_KEY")
    if not api_key:
        st.error("OPENAI_API_KEY not found in Streamlit Secrets. Please add it to run this app.")
        st.stop()

    # Initialize session state
    if "extracted_text" not in st.session_state:
        st.session_state.extracted_text = None
    if "parsed_data" not in st.session_state:
        st.session_state.parsed_data = None

    # --- UI LAYOUT ---
    st.header("Step 1: Upload & Parse Resume")
    
    uploaded_resume = st.file_uploader(
        "Upload a resume file (PDF, DOCX, PNG, JPG)",
        type=["pdf", "docx", "png", "jpg", "jpeg"],
        key="resume_uploader"
    )

    col1, col2 = st.columns(2)

    with col1:
        if uploaded_resume:
            parser = ResumeParser()
            st.session_state.extracted_text = parser.read_file(uploaded_resume)
        
        if st.session_state.extracted_text:
            st.text_area("Extracted Text", st.session_state.extracted_text, height=400)

    with col2:
        if st.session_state.extracted_text:
            if st.button("Parse Extracted Text with AI", use_container_width=True):
                with st.spinner("AI is parsing your resume..."):
                    st.session_state.parsed_data = convert_to_json_with_gpt(
                        st.session_state.extracted_text, api_key
                    )
        
        if st.session_state.parsed__data:
            st.json(st.session_state.parsed_data)

    st.divider()

    # --- Step 2: Generate New Resume ---
    if st.session_state.parsed_data:
        st.header("Step 2: Generate New Resume")
        
        uploaded_template = st.file_uploader(
            "Upload your .docx resume template",
            type=["docx"],
            key="template_uploader"
        )
        
        if uploaded_template:
            if st.button("Generate & Download Resume", use_container_width=True, type="primary"):
                with st.spinner("Creating your new resume..."):
                    # The function now returns a buffer, not a boolean
                    generated_doc_buffer = generate_resume(st.session_state.parsed_data, uploaded_template)

                    if generated_doc_buffer:
                        st.success("🎉 Resume Generated!")
                        st.download_button(
                            label="Click to Download",
                            data=generated_doc_buffer, # Use the buffer here
                            file_name=f"Generated_Resume_{st.session_state.parsed_data.get('name', 'candidate').replace(' ', '_')}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True
                        )
                    else:
                        st.error("Failed to generate the document.")

if __name__ == "__main__":
    main()
