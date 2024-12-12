#!/usr/bin/env python3

"""
Tool for plotting a custom figure.
"""

import logging
from typing import Type, List, TypedDict
from pydantic import BaseModel, Field
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomHeader(TypedDict):
    """
    A list of headers extracted from the user question.
    """
    y: List[str]

class CustomPlotterInput(BaseModel):
    """
    Input schema for the PlotImage tool.
    """
    question: str = Field(description="Description of the plot")

# Note: It's important that every field has type hints. BaseTool is a
# Pydantic class and not having type hints can lead to unexpected behavior.
class CustomPlotterTool(BaseTool):
    """
    Tool for plotting a custom plot.
    """
    name: str = "custom_plotter"
    description: str = "A tool to plot or visualize the simulation results."
    args_schema: Type[BaseModel] = CustomPlotterInput
    st_session_key: str = None

    def _run(self, question: str) -> str:
        """
        Run the tool.

        Args:
            question (str): The question to ask about the model description.

        Returns:
            str: The answer to the question
        """
        # Check if sys_bio_model is provided
        model_object = st.session_state[self.st_session_key]
        if model_object is None:
            return "Please run the simulation first before plotting the figure."
        if model_object.simulation_results is None:
            return "Please run the simulation first before plotting the figure."
        df = model_object.simulation_results
        species_names = "\n".join(df.columns.tolist())
        llm = ChatOpenAI(model="gpt-4o")
        system = f"""
        Given the user question: {question},
        and the species: {species_names},
        which species are relevant to the user's question?
        """
        llm_with_structured_output = llm.with_structured_output(CustomHeader)
        system_prompt_structured_output = ChatPromptTemplate.from_template(system)
        chain = system_prompt_structured_output | llm_with_structured_output
        results = chain.invoke({"input": question})
        logger.info("Suggestions: %s", results)
        extracted_species = []
        for species in results['y']:
            if species in df.columns.tolist():
                extracted_species.append(species)
        logger.info("Extracted species: %s", extracted_species)
        st.session_state.custom_simulation_results = extracted_species
        if len(extracted_species) == 0:
            return "No species found in the simulation results that matches the user prompt."
        return "Plotted the figure using the following species: " + str(extracted_species)
