#!/usr/bin/env python
# coding: utf-8

# # Step 1: Text Extraction

# In[ ]:

import io
from typing import Optional
import streamlit as st

# Import libraries from your requirements.txt
from docx import Document
from pdfminer.high_level import extract_text
from PIL import Image
import pytesseract


class ResumeParser:
    """Reads resume content from DOCX, PDF, or image files."""

    def read_file(self, uploaded_file) -> Optional[str]:
        """Dispatcher to read file content based on file type."""
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
        """Extracts text from a DOCX file."""
        doc = Document(file)
        return "\n".join([para.text for para in doc.paragraphs])

    def _read_pdf(self, file) -> str:
        """Extracts text from a PDF file."""
        return extract_text(file)

    def _read_image(self, file) -> str:
        """Extracts text from an image using Tesseract OCR."""
        return pytesseract.image_to_string(Image.open(file))
