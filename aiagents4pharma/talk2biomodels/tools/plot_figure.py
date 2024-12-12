#!/usr/bin/env python3

"""
Tool for plotting a figure.
"""

from typing import Type, Optional
from dataclasses import dataclass
import matplotlib.pyplot as plt
from pydantic import BaseModel, Field
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.openai_tools import JsonOutputKeyToolsParser
from langchain_experimental.tools import PythonAstREPLTool
from ..models.basico_model import BasicoModel

@dataclass
class ModelData:
    """
    Dataclass for storing the model data.
    """
    modelid: Optional[int] = None
    sbml_file_path: Optional[str] = None
    model_object: Optional[BasicoModel] = None

class PlotImageInput(BaseModel):
    """
    Input schema for the PlotImage tool.
    """
    question: str = Field(description="Description of the plot")
    sys_bio_model: ModelData = Field(description="model data", default=None)

# Note: It's important that every field has type hints. BaseTool is a
# Pydantic class and not having type hints can lead to unexpected behavior.
class PlotImageTool(BaseTool):
    """
    Tool for plotting a figure.
    """
    name: str = "plot_figure"
    description: str = "A tool to plot or visualize the simulation results."
    args_schema: Type[BaseModel] = PlotImageInput
    st_session_key: str = None

    def _run(self,
             question: str,
             sys_bio_model: ModelData = ModelData()) -> str:
        """
        Run the tool.

        Args:
            question (str): The question to ask about the model description.
            sys_bio_model (ModelData): The model data.

        Returns:
            str: The answer to the question
        """
        st_session_key = self.st_session_key
        # Check if sys_bio_model is provided
        if sys_bio_model.modelid or sys_bio_model.sbml_file_path or sys_bio_model.model_object:
            if sys_bio_model.modelid:
                model_object = BasicoModel(model_id=sys_bio_model.modelid)
            elif sys_bio_model.sbml_file_path:
                model_object = BasicoModel(sbml_file_path=sys_bio_model.sbml_file_path)
            else:
                model_object = sys_bio_model.model_object
            if st_session_key:
                st.session_state[st_session_key] = model_object
        else:
            # If the model_object is not provided,
            # get it from the Streamlit session state
            if st_session_key:
                if st_session_key not in st.session_state:
                    return f"Session key {st_session_key} not found in Streamlit session state."
                model_object = st.session_state[st_session_key]
            else:
                return "Please provide a valid model object or \
                    Streamlit session key that contains the model object."
        if model_object is None:
            return "Please run the simulation first before plotting the figure."
        if model_object.simulation_results is None:
            model_object.simulate()
        df = model_object.simulation_results
        tool = PythonAstREPLTool(locals={"df": df})
        llm = ChatOpenAI(model="gpt-3.5-turbo")
        llm_with_tools = llm.bind_tools([tool], tool_choice=tool.name)
        system = f"""
                    You have access to a pandas dataframe `df`.
                    Here is the output of `df.head().to_markdown()`:
                    {df.head().to_markdown()}
                    Given a user question, write the Python code to
                    plot a figure of the answer using matplolib.
                    Return ONLY the valid Python code and nothing else.
                    The firgure size should be equal or smaller than (2, 2).
                    Show the grid and legend. The font size of the legend should be 6.
                    Also write a suitable title for the figure. The font size of the title should be 8.
                    The font size of the x-axis and y-axis labels should be 8.
                    The font size of the x-axis and y-axis ticks should be 6.
                    Make sure that the x-axis has at least 10 tick marks.
                    Use color-blind friendly colors. The figure must be of high quality.
                    Don't assume you have access to any libraries other
                    than built-in Python ones, pandas, streamlit and matplotlib.
                    """
        prompt = ChatPromptTemplate.from_messages([("system", system), ("human", "{question}")])
        parser = JsonOutputKeyToolsParser(key_name=tool.name, first_tool_only=True)
        code_chain = prompt | llm_with_tools | parser
        response = code_chain.invoke({"question": question})
        exec(response['query'], globals(), {"df": df, "plt": plt})
        # load for plotly
        fig = plt.gcf()
        if st_session_key:
            st.pyplot(fig, use_container_width=False)
            st.dataframe(df)
        return "Figure plotted successfully"

    def call_run(self,
            question: str,
            sys_bio_model: ModelData = ModelData(),
            st_session_key: str = None) -> str:
        """
        Run the tool.
        """
        return self._run(question=question,
                         sys_bio_model=sys_bio_model,
                         st_session_key=st_session_key)

    def get_metadata(self):
        """
        Get metadata for the tool.
        """
        return {
            "name": self.name,
            "description": self.description
        }
