import os
import shutil
from pathlib import Path

import gradio as gr
from dotenv import load_dotenv
from elsai_docloom import DocumentExtract

load_dotenv()

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

API_KEY = os.getenv("DOCLOOM_API_KEY")

SCHEMA = [
    {"name": "envelope_id", "type": "string", "description": "Docusign Envelope ID"},
    {"name": "date", "type": "string", "description": "Date of authorization"},
    {"name": "authorized_agent_name", "type": "string", "description": "Name of Authorized Agent"},
    {"name": "authorized_agent_title", "type": "string", "description": "Title of Authorized Agent"},
    {"name": "company_name", "type": "string", "description": "Name of Company"},
    {"name": "telephone_number", "type": "string", "description": "Telephone Number"},
    {"name": "complete_sign_special_waste_profile", "type": "boolean", "description": "Complete and sign Special Waste Profile"},
    {"name": "complete_sign_special_waste_profile_recertification", "type": "boolean", "description": "Complete and sign Special Waste Profile-Recertification"},
    {"name": "authorize_amendments_to_special_waste_profile", "type": "boolean", "description": "Authorize amendments to Special Waste Profile"},
    {"name": "sign_contracts_dispose_transport", "type": "boolean", "description": "Sign contracts to dispose and/or transport material"},
    {"name": "sign_certifications_landfill", "type": "boolean", "description": "Sign certifications necessary to comply with landfill requirements"},
    {"name": "sign_manifests_shipment", "type": "boolean", "description": "Sign manifests to initiate shipment to disposal facilities"},
    {"name": "generator_name", "type": "string", "description": "Generator Name"},
    {"name": "generator_mailing_address", "type": "string", "description": "Generator Mailing Address"},
    {"name": "generator_contact_name", "type": "string", "description": "Generator Contact Name"},
    {"name": "generator_contact_title", "type": "string", "description": "Title of Generator Contact"},
    {"name": "generator_email", "type": "string", "description": "Generator Email"},
    {"name": "signature", "type": "boolean", "description": "Whether a signature is present on the form"},
]

REQUIRED_FIELDS = ["authorized_agent_name", "generator_name", "signature"]


def validate_tpa_form(file):
    if file is None:
        return "", [], ""

    # Save uploaded file locally
    filename = os.path.basename(file)
    dest_path = UPLOAD_DIR / filename
    shutil.copy2(file, dest_path)

    # Extract data using Docloom
    extractor = DocumentExtract(api_key=API_KEY)
    result = extractor.extract(str(dest_path), schema=SCHEMA)
    structured_data = result["structured_data"]

    # Build display data
    display_rows = []
    for field in SCHEMA:
        name = field["name"]
        value = structured_data.get(name, None)
        display_rows.append([field["description"], str(value) if value is not None else "—"])

    # Validate required fields
    missing = []
    for field_name in REQUIRED_FIELDS:
        value = structured_data.get(field_name)
        if not value:
            label = next(f["description"] for f in SCHEMA if f["name"] == field_name)
            missing.append(label)

    if not missing:
        status_html = """
        <div style="padding: 20px; border-radius: 10px; background-color: #d4edda;
                    border: 2px solid #28a745; text-align: center; margin: 10px 0;">
            <span style="font-size: 48px;">&#9989;</span>
            <h2 style="color: #155724; margin: 10px 0;">TPA Form is VALID</h2>
            <p style="color: #155724;">All required fields (Agent Name, Generator Name, Signature) are present.</p>
        </div>
        """
    else:
        missing_list = ", ".join(missing)
        status_html = f"""
        <div style="padding: 20px; border-radius: 10px; background-color: #f8d7da;
                    border: 2px solid #dc3545; text-align: center; margin: 10px 0;">
            <span style="font-size: 48px;">&#10060;</span>
            <h2 style="color: #721c24; margin: 10px 0;">TPA Form is NOT VALID</h2>
            <p style="color: #721c24;">Missing: {missing_list}</p>
        </div>
        """

    return status_html, display_rows, f"File saved to: {dest_path}"


with gr.Blocks(title="TPA Form Validator") as app:
    gr.Markdown("# TPA Form Validator")
    gr.Markdown("Upload a TPA (Third Party Authorization) form to validate it using Docloom extraction.")

    with gr.Row():
        file_input = gr.File(label="Upload TPA Form (PDF)", file_types=[".pdf"])

    validate_btn = gr.Button("Validate TPA Form", variant="primary", size="lg")

    loading_msg = gr.HTML(value="")
    status_output = gr.HTML(label="Validation Result")
    data_table = gr.Dataframe(
        headers=["Field", "Value"],
        label="Extracted Data",
        interactive=False,
    )
    file_info = gr.Textbox(label="File Info", interactive=False)

    def show_loading():
        return (
            """<div style="text-align:center; padding:30px;">
                <div style="display:inline-block; width:40px; height:40px;
                    border:4px solid #e0e0e0; border-top:4px solid #6366f1;
                    border-radius:50%; animation:spin 1s linear infinite;">
                </div>
                <style>@keyframes spin{to{transform:rotate(360deg)}}</style>
                <p style="margin-top:12px; color:#6366f1; font-weight:600;">
                    Extracting and validating TPA form...
                </p>
            </div>""",
            "", [], "",
        )

    def run_validation(file):
        result = validate_tpa_form(file)
        return ("",) + result

    validate_btn.click(
        fn=show_loading,
        inputs=None,
        outputs=[loading_msg, status_output, data_table, file_info],
    ).then(
        fn=run_validation,
        inputs=[file_input],
        outputs=[loading_msg, status_output, data_table, file_info],
    )

if __name__ == "__main__":
    app.launch(theme=gr.themes.Soft())
