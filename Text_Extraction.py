#!/usr/bin/env python
# coding: utf-8

# # Step 1: Text Extraction

# In[ ]:


class ResumeParser:
    def read_file(self, uploaded_file) -> Optional[str]:
        """Read resume content from DOCX, PDF, or image file"""
        try:
            filename = uploaded_file.name.lower()
            if filename.endswith('.docx'):
                return self._read_docx(uploaded_file)
            elif filename.endswith('.pdf'):
                return self._read_pdf(uploaded_file)
            elif filename.endswith(('.png', '.jpg', '.jpeg')):
                return self._read_image(uploaded_file)
            else:
                st.error("Unsupported file format. Please upload a DOCX, PDF, or image.")
                return None
        except Exception as e:
            st.error(f"Error reading file: {e}")
            return None

    def _read_docx(self, file) -> str:
        """Extract text from DOCX file"""
        doc = Document(file)
        return "\n".join([para.text for para in doc.paragraphs])

    def _read_pdf(self, file) -> str:
        """Extract text from PDF file"""
        return extract_text(file)

    def _read_image(self, file) -> str:
        """Extract text from image using OCR"""
        return pytesseract.image_to_string(Image.open(file))


# Streamlit Interface
def main():
    st.title("Resume Text Extractor")
    st.write("Upload a resume file (PDF, DOCX, PNG, JPG) to extract its text.")

    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "png", "jpg", "jpeg"])

    if uploaded_file is not None:
        parser = ResumeParser()
        extracted_text = parser.read_file(uploaded_file)

        if extracted_text:
            st.subheader("Extracted Text")
            st.text_area("Resume Content", extracted_text, height=400)
        else:
            st.warning("No text was extracted.")

if __name__ == "__main__":
    main()

