import streamlit as st
from pydantic import BaseModel
import json
import sys

def generate_schema_from_code(code: str, model_name: str = None):
    """
    Executes the given code and finds the first Pydantic BaseModel subclass.
    Returns its JSON Schema dict.
    """
    local_ns = {}
    try:
        exec(code, {}, local_ns)
    except Exception as e:
        st.error(f"Error executing code: {e}")
        return None

    # Find Pydantic BaseModel subclasses
    models = [obj for obj in local_ns.values()
              if isinstance(obj, type) and issubclass(obj, BaseModel) and obj is not BaseModel]
    if not models:
        st.error("No Pydantic BaseModel subclass found in the provided code.")
        return None

    # If a model_name is provided, try to select it
    if model_name:
        model = next((m for m in models if m.__name__ == model_name), models[0])
    else:
        model = models[0]

    try:
        # For Pydantic v2 use model.model_json_schema(), else v1 use model.schema()
        if hasattr(model, 'model_json_schema'):
            schema = model.model_json_schema()
        else:
            schema = model.schema()
    except Exception as e:
        st.error(f"Error generating schema: {e}")
        return None

    return schema

# Streamlit UI
st.title("Pydantic Model → JSON Schema Converter")

st.markdown("Paste your Pydantic `BaseModel` subclass below:")
code_input = st.text_area("Pydantic Model Code", height=300, placeholder="class User(BaseModel):\n    id: int\n    name: str\n    tags: list[str]")

if st.button("Generate JSON Schema"):
    if not code_input.strip():
        st.warning("Please paste your Pydantic model code.")
    else:
        schema = generate_schema_from_code(code_input)
        if schema:
            payload = {
                "name": "user_data",
                "strict": True,
                "schema": schema
            }
            st.markdown("**Generated JSON Schema:**")
            st.json(payload)

# Show instructions
with st.expander("How to use this app"):
    st.markdown(
        "1. Paste your Pydantic `BaseModel` subclass in the text area above.\n"
        "2. Click **Generate JSON Schema**.\n"
        "3. View or copy the resulting JSON Schema envelope.\n"
    )
