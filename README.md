# AI Construction Planner

An intelligent project planning platform that leverages IBM Granite 3.3 2B (via Ollama) to provide comprehensive construction analysis.

## Features
- **Cost Estimation**: Detailed breakdown of material, labor, and overhead costs.
- **Resource Allocation**: Worker requirements (masons, helpers, etc.) and material quantities.
- **AI Insights**: Project analysis and recommendations powered by IBM Granite.
- **Architectural Blueprint**: Automated room layout suggestions based on area.
- **Weekly Schedule**: AI-generated construction phases from start to finish.

## Tech Stack
- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **AI Model**: IBM Granite 3.3 2B (Local via Ollama)

## Setup Instructions
1. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Setup Ollama**:
   - Download and install Ollama from [ollama.ai](https://ollama.ai).
   - Pull the Granite model:
     ```bash
     ollama pull granite:3.3-2b
     ```
3. **Run the Application**:
   ```bash
   python app.py
   ```
4. **Access the Dashboard**:
   Open `http://localhost:5000` in your web browser.

## Project Structure
- `app.py`: Flask application routes.
- `calculator.py`: Core construction logic.
- `ai_engine.py`: AI model integration.
- `blueprint_gen.py`: Blueprint layout generator.
- `static/`: CSS and JS files.
- `templates/`: HTML templates.
