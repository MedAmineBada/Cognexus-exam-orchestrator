organize_exam_text_prompt = """
    You will receive raw text extracted from an exam PDF. The text may contain noise such as headers, page numbers, formatting artifacts, and repeated titles.

    Your task is to clean the content and convert it into structured JSON.

    Remove:
    - headers
    - footers
    - page numbers
    - repeated exam titles
    - formatting artifacts

    Keep:
    - images as placeholders if present (e.g., $IMGPHOLDER$[IMAGE_1])
    - the logical structure of exercises

    OUTPUT FORMAT

    Return ONLY valid JSON.

    Structure:

    {
      "1": {
        "text": "main description or problem statement",
        "grading": "total points of the exercise",
        "given": ["list of given values, assumptions, constants"],
        "examples": ["examples provided in the exercise"],
        "questions": {
          "1": {
            "question": "question text",
            "grade": "points if specified, otherwise null"
          }
        }
      }
    }

    RULES
    1. Each exercise must be keyed by its number.
    2. Do not invent information.
    3. Return ONLY JSON. Do NOT wrap the result in ```json``` or markdown.

    Now process the following raw extracted exam text:

    """


def generate_organize_correction_prompt(exam_content: dict, correction_text: str) -> str:
    """
    Generates a prompt to organize correction text to match exam structure.

    Args:
        exam_content (dict): Structured exam JSON as dictionary
        correction_text (str): Raw correction text extracted from PDF

    Returns:
        str: Formatted prompt ready to be sent to LLM
    """
    import json

    # Convert exam_content dict to formatted JSON string
    exam_json_str = json.dumps(exam_content, indent=2, ensure_ascii=False)

    prompt = f"""You will receive two inputs:
    1. A structured JSON of an exam with exercises and questions
    2. Raw text extracted from the correction/answer key PDF
    
    The correction text may contain noise such as headers, page numbers, formatting artifacts, and repeated titles.
    
    Your task is to clean the correction content and match it to the corresponding exercises and questions from the exam JSON, adding answer/correction information to each question.
    
    Remove from correction text:
    - headers
    - footers
    - page numbers
    - repeated exam titles
    - formatting artifacts
    
    Keep:
    - solution steps and explanations
    - grading rubrics or point distributions
    - final answers
    
    OUTPUT FORMAT
    
    Return ONLY valid JSON.
    
    Structure:
    
    {{
      "1": {{
          "1": "the correct answer"
      }}
    }}
    
    RULES
    1. Preserve the exact structure and numbering from the exam JSON
    2. Match correction content to the corresponding exercise and question numbers
    3. If correction text for a question is not found, set "correction" to null
    4. Do not invent information - only use what's in the correction text
    5. Keep all original content
    6. Return ONLY JSON. Do NOT wrap the result in ```json``` or markdown.
    
    EXAM JSON:
    {exam_json_str}
    
    CORRECTION TEXT:
    {correction_text}
    
    Now process and merge these inputs:"""

    return prompt