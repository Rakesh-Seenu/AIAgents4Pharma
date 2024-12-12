<h1 align="center" style="font-weight: bold;">🤖 AIAgents4Pharma</h1>

Welcome to **AIAgents4Pharma** – an open-source project by [Team VPE](https://github.com/VirtualPatientEngine) that brings together AI-driven tools to help researchers and pharma interact seamlessly with complex biological data.

Our toolkit currently consists of three agents, each designed to simplify and enhance access to complex data in biology:

- [**Talk2BioModels**](talk2biomodels/models/intro.md): Engage directly with mathematical models in systems biology.

- [**Talk2Cells**](talk2cells/intro.md) *(Coming soon)*: Query and analyze sequencing data with ease.

- [**Talk2KnowledgeGraphs**](Talk2KnowledgeGraphs/intro.md) *(Coming soon)*: Access and explore complex biological knowledge graphs for insightful data connections.

### Prerequisites

- **Python 3.10+**
- **Git**
- Required libraries specified in `requirements.txt`

### Installation

#### Option 1: PyPI
   ```bash
   pip install aiagents4pharma
   ```

Check out the tutorials on each agent for detailed instrcutions.

#### Option 2: Git
1. Clone the repository:
   ```bash
   git clone https://github.com/VirtualPatientEngine/AIAgents4Pharma
   cd AIAgents4Pharma
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Initialize OPENAI_API_KEY
   ```bash
   export OPENAI_API_KEY = ....
   ```

4. Launch Streamlit:
   ```bash
   streamlit run app/frontend/streamlit_app.py
   ```

### Contributing

We welcome contributions to AIAgents4Pharma! Here’s how you can help:

1. **Fork the repository**
2. **Create a new branch** for your feature (`git checkout -b feat/feature-name`)
3. **Commit your changes** (`git commit -m 'feat: Add new feature'`)
4. **Push to the branch** (`git push origin feat/feature-name`)
5. **Open a pull request**

Check out our [CONTRIBUTING.md](CONTRIBUTING.md) for more information.