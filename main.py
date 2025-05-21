import streamlit as st
from pydantic import BaseModel
import json
import traceback

def generate_schema_from_code(code: str, model_name: str = None):
    """
    Executes the given code and finds the first Pydantic BaseModel subclass.
    Returns its JSON Schema dict.
    """
    local_ns = {}
    try:
        exec(code, {}, local_ns)
    except Exception as e:
        return {"error": f"Code execution error: {e}"}

    # Find Pydantic BaseModel subclasses
    models = [obj for obj in local_ns.values()
              if isinstance(obj, type) and issubclass(obj, BaseModel) and obj is not BaseModel]
    if not models:
        return {"error": "No Pydantic BaseModel subclass found."}

    # Select model
    if model_name:
        model = next((m for m in models if m.__name__ == model_name), models[0])
    else:
        model = models[0]

    try:
        if hasattr(model, 'model_json_schema'):
            schema = model.model_json_schema()
        else:
            schema = model.schema()
    except Exception as e:
        return {"error": f"Schema generation error: {e}"}

    return schema

# Streamlit UI
st.set_page_config(page_title="Pydantic → JSON Schema", layout="wide")
st.title("Pydantic Model → JSON Schema Converter")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Paste your Pydantic Model")
    code_input = st.text_area(
        "Model Code", height=400,
        placeholder="from pydantic import BaseModel\nclass User(BaseModel):\n    id: int\n    name: str"
    )
    model_name = st.text_input("Model class name (optional)", help="Specify to choose among multiple models in the code.")
    if st.button("Generate JSON Schema"):
        if not code_input.strip():
            st.warning("Please paste your Pydantic model code.")
        else:
            result = generate_schema_from_code(code_input, model_name)
            if 'error' in result:
                col2.error(result['error'])
            else:
                payload = {
                    "name": "user_data",
                    "strict": True,
                    "schema": result
                }
                with col2:
                    st.subheader("Generated JSON Schema")
                    st.json(payload)

with col2:
    st.subheader("JSON Schema Output")
    st.info("Paste your model and click 'Generate JSON Schema' on the left.")

with st.expander("How to use this app"):
    st.markdown(
        "1. Paste your Pydantic `BaseModel` subclass in the left panel.  
"
        "2. (Optional) Enter the class name if there are multiple models.  
"
        "3. Click **Generate JSON Schema**.  
"
        "4. View or copy the JSON Schema on the right."
    )
