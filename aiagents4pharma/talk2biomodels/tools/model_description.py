#!/usr/bin/env python3

"""
Tool for asking a question about the model description.
"""

from typing import Type, Optional
from dataclasses import dataclass
from pydantic import BaseModel, Field, model_validator
import streamlit as st
from langchain_core.tools import BaseTool
from langchain_core.output_parsers import StrOutputParser
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.prompts import ChatPromptTemplate
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

    # Check if model_object is an instance of BasicoModel
    # otherwise make it None. This is important because
    # sometimes the LLM may invoke the tool with an
    # inappropriate model_object.
    @model_validator(mode="before")
    @classmethod
    def check_model_object(cls, data):
        """
        Check if model_object is an instance of BasicoModel.
        """
        if 'model_object' in data:
            if not isinstance(data['model_object'], BasicoModel):
                data['model_object'] = None
        return data

class ModelDescriptionInput(BaseModel):
    """
    Input schema for the ModelDescription tool.
    """
    question: str = Field(description="question about the model description")
    sys_bio_model: ModelData = Field(description="model data", default=None)

# Note: It's important that every field has type hints. BaseTool is a
# Pydantic class and not having type hints can lead to unexpected behavior.
class ModelDescriptionTool(BaseTool):
    """
    Tool for returning the description of the specified BioModel.
    """
    name: str = "model_description"
    description: str = '''A tool to ask about the description of the model.'''
    args_schema: Type[BaseModel] = ModelDescriptionInput
    return_direct: bool = True
    st_session_key: str = None

    def _run(self,
             question: str,
             sys_bio_model: ModelData = ModelData(),
             run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """
        Run the tool.

        Args:
            question (str): The question to ask about the model description.
            run_manager (Optional[CallbackManagerForToolRun]): The CallbackManagerForToolRun object.

        Returns:
            str: The answer to the question.
        """
        st_session_key = self.st_session_key
        print (st_session_key, 'st_session_key')
        # Check if sys_bio_model is provided in the input schema
        if sys_bio_model.modelid or sys_bio_model.sbml_file_path \
            or sys_bio_model.model_object not in [None, "", {}]:
            if sys_bio_model.modelid:
                model_object = BasicoModel(model_id=sys_bio_model.modelid)
            elif sys_bio_model.sbml_file_path:
                model_object = BasicoModel(sbml_file_path=sys_bio_model.sbml_file_path)
            else:
                print (sys_bio_model.model_object, 'model_object')
                model_object = sys_bio_model.model_object
            if st_session_key:
                st.session_state[st_session_key] = model_object
        # Check if sys_bio_model is provided in the Streamlit session state
        elif st_session_key:
            if st_session_key not in st.session_state:
                return f"Session key {st_session_key} " \
                        "not found in Streamlit session state."
            model_object = st.session_state[st_session_key]
        else:
            return "Please provide a valid model object or Streamlit "\
                "session key that contains the model object."
        # check if model_object is None
        if model_object is None:
            return "Please provide a BioModels ID or an SBML file path for the model."
        description = model_object.description
        if description in [None, ""]:
            return "No description found for the model."
        # Append the BioModel ID of the model to the description
        description = f"{description} (BioModel ID: {model_object.model_id})"
        llm = ChatOpenAI(model="gpt-3.5-turbo")
        # Check if run_manager's metadata has the key 'prompt_content'
        if run_manager and 'prompt' in run_manager.metadata:
            prompt_content = run_manager.metadata['prompt']
        else:
            prompt_content = '''
                            Given the description of a System biology model:
                            {description},
                            answer the user question:
                            {question}.
                            '''
        prompt_template = ChatPromptTemplate.from_messages(
            [("system", prompt_content),
             ("user", "{description} {question}")]
        )
        parser = StrOutputParser()
        chain = prompt_template | llm | parser
        return chain.invoke({"description": description,
                             "question": question})

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
