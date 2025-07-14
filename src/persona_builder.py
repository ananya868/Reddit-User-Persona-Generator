import os, json, yaml 

from pathlib import Path
from typing import Dict, Any, List 

from src.utils.llm_client import LLMClient
from src.utils.schemas.persona_schema import UserPersona


# Path Configuration
current_file_path = Path(__file__)
SRC_DIR = current_file_path.parent
PROJECT_ROOT = SRC_DIR.parent
PROMPTS_DIR = SRC_DIR / "utils" / "prompts"
OUTPUT_DIR = PROJECT_ROOT / "output"


# Helper Methods 
def _load_prompt_template(filename: str) -> Dict[str, str]:
    """Loads a YAML prompt template file."""
    prompt_path = PROMPTS_DIR / filename
    try: 
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"ERROR: Prompt file not found at {prompt_path}")
        return None
    except Exception as e:
        print(f"ERROR: Failed to load or parse prompt file {prompt_path}. Reason: {e}")
        return None

    
# Core Methods 
def generate_structured_persona(processed_data: Dict[str, Any], prompt_filepath: str = 'structured_prompt.yml', OutputSchema: Any = UserPersona) -> None:
    """
    Generates a structured persona from processed data using an LLM.

    :param processed_data: Dictionary containing user data and preferences.
    """
    print("Generating structured persona...")
    if not processed_data:
        print("ERROR: No processed data provided.")
        return
    
    # Load the prompt template
    prompt_template = _load_prompt_template(prompt_filepath)
    if not prompt_template:
        print("ERROR: Failed to load prompt template.")
        return

    # Prepare the prompt
    username = processed_data["summary_analysis"]["username"]
    metadata_summary = json.dumps(
        processed_data["summary_analysis"], indent=2
    )
    user_content = json.dumps(
        processed_data["content_for_llm"], indent=2
    )

    # Format the Full Prompt 
    full_prompt = (
        f"{prompt_template['system_prompt']}\n\n"
        f"{prompt_template['user_prompt']}"
    ).format(
        username=username,
        metadata_summary=metadata_summary,
        user_content=user_content
    )

    # LLM Client 
    llm = LLMClient()
    structured_persona = llm.generate_structured_response(
        prompt=full_prompt, 
        pydantic_schema=OutputSchema
    )

    if not structured_persona:
        print("ERROR: Failed to generate structured persona.")
        return

    # Save to JSON File 
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = OUTPUT_DIR / f"{username}_structured_persona.json"

    try:
        with open(output_path, "w", encoding="utf‑8") as f:
            json.dump(structured_persona, f, indent=2, ensure_ascii=False)
            return structured_persona
        print(f"SUCCESS: Structured persona saved to {output_path}")
    except Exception as e:
        print(f"ERROR: Could not write structured persona to file. Reason: {e}")


def generate_standard_persona(processed_data: Dict[str, Any], prompt_filepath: str = 'standard_prompt.yml') -> None:
    """
    Generates a standard persona from processed data using an LLM.

    :param processed_data: Dictionary containing user data and preferences.
    """
    print("Generating standard persona...")
    if not processed_data:
        print("ERROR: No processed data provided.")
        return

    # Load the prompt template
    prompt_template = _load_prompt_template("standard_prompt.yml")
    if not prompt_template:
        return

    # Prepare the data for Prompt 
    username = processed_data["summary_analysis"]["username"]
    metadata_summary = json.dumps(processed_data["summary_analysis"], indent=2)
    user_content = json.dumps(processed_data["content_for_llm"], indent=2)

    # Format the Full Prompt
    full_prompt = (
        f"{prompt_template['system_prompt']}\n\n"
        f"{prompt_template['user_prompt']}"
    ).format(
        username=username,
        metadata_summary=metadata_summary,
        user_content=user_content
    )

    # LLM Client
    llm = LLMClient()
    standard_persona = llm.generate_response(
        prompt=full_prompt,
        temperature=0.1
    ) 

    if not standard_persona:
        print("ERROR: Failed to generate standard persona.")
        return

    # Save to a Markdown file
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = OUTPUT_DIR / f"{username}_standard_personas.md"

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(standard_persona.strip())
        print(f"SUCCESS: Standard persona saved to {output_path}")
    except Exception as e:
        print(f"ERROR: Could not write standard persona to file. Reason: {e}")

