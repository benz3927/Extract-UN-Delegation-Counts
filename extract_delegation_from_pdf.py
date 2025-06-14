import os
import pandas as pd
from typing import List
from pydantic import BaseModel, Field

from pypdf import PdfReader  # or use `from PyPDF2 import PdfReader` if needed
import gradio as gr

from langchain.chat_models import ChatOpenAI
from langchain.output_parsers.openai_functions import JsonKeyOutputFunctionsParser
from langchain.output_parsers.openai_functions import convert_to_openai_function
from langchain.prompts import ChatPromptTemplate

# === Pydantic Schema ===
class Delegation(BaseModel):
    country: str = Field(description="Country name, like 'Ethiopia'")
    year: int = Field(description="Year of the UNGA session")
    officials: int = Field(description="Number of officials listed before 'Representatives'")
    leader_present: int = Field(description="1 if President or Prime Minister is listed among officials, otherwise 0")
    representatives: int = Field(description="Number of representatives")
    alternate_representatives: int = Field(description="Number of alternate representatives")
    advisers: int = Field(description="Number of advisers")
    attendees: int = Field(description="Total number of people across all above categories")

class DelegationInfo(BaseModel):
    entries: List[Delegation]

# === Prompt Template ===
prompt_template_delegation = ChatPromptTemplate.from_messages([
    ("system", "You are an assistant that extracts delegation data from UN General Assembly reports."),
    ("human", """
From the following text, extract the following information for each country:
- Country
- Year
- Number of officials (those listed before 'Representatives')
- Whether a leader is present (President or Prime Minister → 1, otherwise 0)
- Number of representatives
- Number of alternate representatives
- Number of advisers
- Total attendees (sum of above roles)

Please return one entry per country per year. Use numeric values.

Text: {policy}
""")
])

# === LangChain Setup ===
model = ChatOpenAI(model="gpt-4", temperature=0)
extraction_function = [convert_to_openai_function(DelegationInfo)]
extraction_model = model.bind(functions=extraction_function, function_call={"name": "DelegationInfo"})
extraction_chain = prompt_template_delegation | extraction_model | JsonKeyOutputFunctionsParser(key_name="entries")

# === Extract Text from PDF ===
def extract_text_from_pdf(pdf_file):
    try:
        reader = PdfReader(pdf_file)
        return "".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        return f"Error reading PDF: {e}"

# === Main Logic for Gradio ===
def process_delegation_pdf(pdf_file):
    policy_text = extract_text_from_pdf(pdf_file.name)
    if not policy_text.strip():
        return "❌ No text extracted.", None, pd.DataFrame()

    entries = extraction_chain.invoke({"policy": policy_text})
    df = pd.DataFrame(entries)

    output_dir = "/Users/CS/Documents/DataExtraction/Summer2025/aid_commitments"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "delegation_data.xlsx")
    df.to_excel(output_path, index=False)

    return f"✅ Extracted {len(df)} entries", output_path, df

# === Gradio App ===
iface = gr.Interface(
    fn=process_delegation_pdf,
    inputs=gr.File(label="📄 Upload UNGA Report PDF"),
    outputs=[
        gr.Textbox(label="Summary"),
        gr.File(label="⬇️ Excel File Output"),
        gr.DataFrame(label="📊 Extracted Table")
    ],
    title="UN Delegation PDF Extractor",
    description="Upload a UNGA report PDF to extract delegation information and download an Excel file."
)

if __name__ == "__main__":
    iface.launch()
