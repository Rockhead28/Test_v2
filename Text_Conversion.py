#!/usr/bin/env python
# coding: utf-8

# # Step 2: Conversion from text to json structured data

# In[ ]:


def convert_to_json_with_gpt(resume_text: str, api_key: str) -> dict:
    client = OpenAI(api_key=api_key)

    prompt = f"""
You are a resume parser. Extract the following structured fields from the resume text below and return ONLY a valid JSON object.

Required fields:
- name
- contact_number
- email
- skills (as a list)
- languages
- education: list of {{education certificate}}
- work_experience: list of {{
    company_name (reformat font to only capitalize first letter as capital),
    duration,
    job_title,
    job_description (as a list of bullet points),
    achievements (if available, as list of bullet points)
}}

Make sure work_experience is a list of entries, and fields like skills or job_description are lists, not strings.

Resume text:
\"\"\"
{resume_text}
\"\"\"
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        raw_output = response.choices[0].message.content

        match = re.search(r"{.*}", raw_output, re.DOTALL)
        if match:
            json_text = match.group(0)
        else:
            st.error("No valid JSON found in GPT response.")
            return {}

        return json.loads(json_text)

    except json.JSONDecodeError:
        st.error("Failed to parse GPT response as JSON.")
        return {}
    except Exception as e:
        st.error(f"GPT API call failed: {e}")
        return {}

