# placeholder_insertion.py

import io
from typing import Dict, Any, Optional, List
from copy import deepcopy
import streamlit as st
from docx import Document
from docx.text.paragraph import Paragraph
from docx.text.run import Run

# --- HELPER FUNCTIONS ---
# This function is fine, but be aware it can fail if a placeholder
# like {NAME} is split across different formatting runs. For most templates, it's okay.
def replace_text_in_paragraph(paragraph: Paragraph, key: str, value: Any):
    for run in paragraph.runs:
        if key in run.text:
            run.text = run.text.replace(key, str(value))

# These formatting functions are excellent. No changes needed.
def copy_run_formatting(source_run: Run, target_run: Run):
    if source_run is None or target_run is None:
        return
    target_run.font.name = source_run.font.name
    target_run.font.size = source_run.font.size
    target_run.font.bold = source_run.font.bold
    target_run.font.italic = source_run.font.italic
    target_run.font.underline = source_run.font.underline
    if source_run.font.color.rgb:
        target_run.font.color.rgb = source_run.font.color.rgb

def copy_paragraph_formatting(source_paragraph: Paragraph, target_paragraph: Paragraph):
    target_paragraph.style = source_paragraph.style
    p_format = source_paragraph.paragraph_format
    target_p_format = target_paragraph.paragraph_format
    target_p_format.alignment = p_format.alignment
    target_p_format.space_after = p_format.space_after
    target_p_format.space_before = p_format.space_before
    target_p_format.left_indent = p_format.left_indent
    target_p_format.right_indent = p_format.right_indent

# *** CRITICAL FIX HERE ***
# This is the corrected version for handling multi-line text like Education.
def replace_with_multiline_text(paragraph: Paragraph, key: str, formatted_text: str):
    """
    Replaces a placeholder with multiple lines of text, creating new paragraphs.
    """
    if key not in paragraph.text:
        return

    lines = formatted_text.split('\n')
    
    # Replace the placeholder in the first line
    replace_text_in_paragraph(paragraph, key, lines[0])

    # Insert subsequent lines as new paragraphs below the current one
    current_paragraph_element = paragraph._p
    for line in lines[1:]:
        new_p = current_paragraph_element.getparent().add_paragraph(line)
        copy_paragraph_formatting(paragraph, new_p)
        # We move the new paragraph to be right after the current one.
        current_paragraph_element.addnext(new_p._p)
        current_paragraph_element = new_p._p

# Your bullet point logic is solid. No changes needed.
def replace_with_bullet_points(paragraph: Paragraph, key: str, bullet_points: List[str]):
    if key not in paragraph.text:
        return
        
    if not bullet_points:
        replace_text_in_paragraph(paragraph, key, "")
        return

    template_run = None
    for run in paragraph.runs:
        if key in run.text:
            template_run = run
            break
    if not template_run:
        return

    parent = paragraph._parent
    
    # Replace the placeholder key with the first bullet point in the original paragraph.
    replace_text_in_paragraph(paragraph, key, "• " + bullet_points[0])

    # Add subsequent bullet points as new paragraphs.
    current_paragraph_element = paragraph._p
    for point in bullet_points[1:]:
        new_p = parent.add_paragraph()
        copy_paragraph_formatting(paragraph, new_p)
        new_run = new_p.add_run("• " + point)
        copy_run_formatting(template_run, new_run)
        current_paragraph_element.addnext(new_p._p)
        current_paragraph_element = new_p._p


# --- MAIN GENERATION FUNCTION ---
# The main logic is very good. We are keeping it as is.
def generate_resume(data: Dict[str, Any], template_path: str) -> Optional[io.BytesIO]:
    """Generates a resume by populating a .docx template with JSON data."""
    try:
        doc = Document(template_path)
    except Exception as e:
        st.error(f"Error opening template file '{template_path}': {e}")
        return None

    # 1. Simple replacements
    simple_replacements = {
        "{NAME}": data.get("name", ""),
        "{CONTACT}": data.get("contact_number", ""),
        "{EMAIL}": data.get("email", ""),
    }
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    for key, value in simple_replacements.items():
                        replace_text_in_paragraph(p, key, value)

    # 2. Multi-line and Bulleted List replacements
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in list(cell.paragraphs): # Use list() to avoid issues when modifying paragraphs
                    # Education
                    if "{EDUCATION}" in p.text:
                        education_list = data.get("education", [])
                        if education_list:
                            edu_blocks = ["\n".join(filter(None, [entry.get("degree"), entry.get("institution"), entry.get("year"), f"CGPA: {entry.get('cgpa')}" if entry.get('cgpa') else None])) for entry in education_list]
                            formatted_education_string = "\n\n".join(edu_blocks)
                            replace_with_multiline_text(p, "{EDUCATION}", formatted_education_string)
                        else:
                            replace_text_in_paragraph(p, "{EDUCATION}", "")
                    
                    # Skills and Languages
                    if "{SKILLS}" in p.text:
                        replace_with_bullet_points(p, "{SKILLS}", data.get("skills", []))
                    if "{LANGUAGES}" in p.text:
                        replace_with_bullet_points(p, "{LANGUAGES}", data.get("languages", []))


    # 4. Work Experience (Dynamic Table Rows) - Your logic is great here
    work_exp_placeholders = {"{COMPANYNAME}", "{DURATION}", "{JOBTITLE}", "{JOBDESCRIPTION}", "{ACHIEVEMENTS}"}
    for table in doc.tables:
        template_rows_info = []
        for i, row in enumerate(table.rows):
            row_text = "".join(cell.text for cell in row.cells)
            if any(ph in row_text for ph in work_exp_placeholders):
                template_rows_info.append({'row': row, 'index': i})
        
        if not template_rows_info:
            continue

        template_row_to_copy = template_rows_info[0]['row']
        
        # Insert new rows based on the template
        for experience in reversed(data.get("work_experience", [])): # Reverse to insert in correct order
            new_row_elem = deepcopy(template_row_to_copy._element)
            template_row_to_copy._element.addnext(new_row_elem)
            
            new_row = table.rows[template_row_to_copy.idx + 1] # Access the newly added row
            for cell in new_row.cells:
                for p in list(cell.paragraphs):
                    replace_text_in_paragraph(p, "{COMPANYNAME}", experience.get("company_name", ""))
                    replace_text_in_paragraph(p, "{DURATION}", experience.get("duration", ""))
                    replace_text_in_paragraph(p, "{JOBTITLE}", experience.get("job_title", ""))
                    
                    if "{JOBDESCRIPTION}" in p.text:
                        replace_with_bullet_points(p, "{JOBDESCRIPTION}", experience.get("job_description", []))
                    if "{ACHIEVEMENTS}" in p.text:
                        replace_with_bullet_points(p, "{ACHIEVEMENTS}", experience.get("achievements", []))
        
        # Remove original template row after all new rows are added
        tbl = table._tbl
        tbl.remove(template_row_to_copy._tr)
        break # Assume only one work experience table

    # Save to in-memory buffer for Streamlit
    try:
        doc_buffer = io.BytesIO()
        doc.save(doc_buffer)
        doc_buffer.seek(0)
        return doc_buffer
    except Exception as e:
        st.error(f"Error saving output file to memory: {e}")
        return None
