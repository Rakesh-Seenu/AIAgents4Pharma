#!/usr/bin/env python3

"""
Tool for asking a question about the simulation results.
"""

from typing import Type, Optional
from dataclasses import dataclass
import streamlit as st
from pydantic import BaseModel, Field
from langchain_core.tools.base import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
from ..models.basico_model import BasicoModel

@dataclass
class ModelData:
    """
    Dataclass for storing the model data.
    """
    modelid: Optional[int] = None
    sbml_file_path: Optional[str] = None
    model_object: Optional[BasicoModel] = None

class AskQuestionInput(BaseModel):
    """
    Input schema for the AskQuestion tool.
    """
    question: str = Field(description="question about the simulation results")

# Note: It's important that every field has type hints. BaseTool is a
# Pydantic class and not having type hints can lead to unexpected behavior.
class AskQuestionTool(BaseTool):
    """
    Tool for calculating the product of two numbers.
    """
    name: str = "ask_question"
    description: str = "A tool to ask question about the simulation results."
    args_schema: Type[BaseModel] = AskQuestionInput
    return_direct: bool = True
    st_session_key: str = None
    sys_bio_model: ModelData = ModelData()

    def _run(self,
             question: str,
             run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """
        Run the tool.

        Args:
            question (str): The question to ask about the simulation results.
            run_manager (Optional[CallbackManagerForToolRun]): The CallbackManagerForToolRun object.

        Returns:
            str: The answer to the question.
        """
        st_session_key = self.st_session_key
        sys_bio_model = self.sys_bio_model
        # Check if sys_bio_model is provided in the input
        if sys_bio_model.modelid or sys_bio_model.sbml_file_path or sys_bio_model.model_object:
            if sys_bio_model.modelid is not None:
                model_object = BasicoModel(model_id=sys_bio_model.modelid)
            elif sys_bio_model.sbml_file_path is not None:
                model_object = BasicoModel(sbml_file_path=sys_bio_model.sbml_file_path)
            else:
                model_object = sys_bio_model.model_object
        else:
            # If the sys_bio_model is not provided in the input,
            # get it from the Streamlit session state
            if st_session_key:
                if st_session_key not in st.session_state:
                    return f"Session key {st_session_key} not found in Streamlit session state."
                model_object = st.session_state[st_session_key]
            else:
                return "Please provide a valid model object or \
                    Streamlit session key that contains the model object."
        # Update the object in the streamlit session state
        if st_session_key:
            st.session_state[st_session_key] = model_object
        if model_object.simulation_results is None:
            model_object.simulate()
        df = model_object.simulation_results
        # If there is a Streamlit session key,
        # display the simulation results
        if st_session_key:
            st.text(f"Simulation Results of the model {model_object.model_id}")
            st.dataframe(df, use_container_width = False, width = 650)
        # Check if run_manager's metadata has the key 'prompt_content'
        prompt_content = None
        if run_manager and 'prompt' in run_manager.metadata:
            prompt_content = run_manager.metadata['prompt']
        # Create a pandas dataframe agent with OpenAI
        df_agent = create_pandas_dataframe_agent(ChatOpenAI(model="gpt-3.5-turbo"),
                                                  allow_dangerous_code=True,
                                                  agent_type=AgentType.OPENAI_FUNCTIONS,
                                                  df=df,
                                                  prefix=prompt_content)
        llm_result = df_agent.invoke(question)
        return llm_result["output"]

    def get_metadata(self):
        """
        Get metadata for the tool.

        Returns:
            dict: The metadata for the tool.
        """
        return {
            "name": self.name,
            "description": self.description
        }
