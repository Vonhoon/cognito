# Agent Guide for Cognito - AURA Interface

## Project Overview
This project is a PySide6-based narrative simulation and chatbot interface. It simulates a retro-futuristic terminal where the user interacts with an AI named "AURA". The experience involves a linear narrative progression triggered by user interactions, simulated system failures ("scares"), and unlocking capabilities (Internet, MCP).

## Codebase Structure
Currently, the project is a monolithic script:
- `cognito_v0.1.py`: Contains all logic, UI definition, state management, and LLM interaction.
- `sounds/`: Directory for `.wav` sound effects.
- `neodgm_code.ttf`: Custom font file.
- `api_key.txt`: (Ignored by git) Contains the Gemini API key.

## Development Guidelines

### Coding Standards
- Follow PEP 8 guidelines.
- Use descriptive variable names.
- Add docstrings to functions and classes.

### UI Development (PySide6)
- The UI is built programmatically (no `.ui` files).
- Stylesheets (QSS) are heavily used to achieve the retro "dark mode" aesthetic (Green text on Dark background).
- Custom fonts are loaded dynamically.
- **Caution:** The `CognitoWindow` class handles everything. Be careful when modifying the `setup_ui` method to not break the layout.

### State Machine Logic
The application relies on a simple state machine stored in `self.game_state`.
**Key States:**
- `NORMAL_NO_PERMISSIONS`: Initial state.
- `AWAITING_INTERNET_CONFIRM`: User requested internet-related info.
- `NORMAL_INTERNET_ONLY`: Internet enabled.
- `AWAITING_MCP_CONFIRM`: User requested computation-heavy info.
- `NORMAL_ALL_PERMISSIONS`: MCP enabled.
- `UNEASY`: Post-Blank Screen scare.
- `HOSTILE`: Post-BSOD scare.
- `DEBUGGING`: Developer Mode active.
- `POST_DEBUG`: "Fragment" removed, system stabilizing.
- `ENDING`: Final sequence.

**Triggers:**
- Triggers are checked in `send_prompt`.
- Triggers can be based on prompt count (`self.prompt_count`) or specific keywords.

## Key Components

### LLM Integration
- Uses `google.generativeai` (Gemini 1.5 Flash).
- The `generate_aura_response` method constructs the system prompt based on the current `game_state`.
- **Note:** Currently, the LLM call is synchronous and blocks the UI.

### Narrative & "Scares"
- Scares (Blank Screen, BSOD, Glitch) are implemented using `QWidget` overlays (`_blank_overlay`, `_bsod_overlay`).
- Sound effects are triggered via `QSoundEffect`.
- The "Developer Mode" allows simulating code editing to "fix" a bug (`BUG_MARKER`).

## Future Roadmap (Improvements)

Future agents should prioritize the following improvements:

1.  **Refactoring (High Priority):**
    - Split `cognito_v0.1.py` into multiple modules:
        - `main.py`: Entry point.
        - `ui/`: specific widgets (Chat, Header, DevDock).
        - `core/`: Game state, LLM client.
        - `utils/`: Config, Asset loading.
        - `config.py`: Constants (Colors, Strings).

2.  **Threading (Critical):**
    - Move `self.llm_model.generate_content` calls to a `QThread` or `QRunnable`.
    - Use signals/slots to update the UI with the response. This will prevent the "Not Responding" state during generation.

3.  **Configuration Management:**
    - Move hardcoded strings (TRANSLATIONS), colors, and other constants to a separate configuration file (JSON/YAML) or a dedicated python module.

4.  **Type Hinting:**
    - Add Python type hints to all functions and methods to improve code clarity and enable static analysis.

5.  **Testing:**
    - Add unit tests for the logic (State transitions, Keyword detection).
    - Add UI tests using `pytest-qt`.

6.  **Dependency Management:**
    - Create a `requirements.txt` or `pyproject.toml` file.
