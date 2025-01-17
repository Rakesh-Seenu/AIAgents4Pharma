'''
A test BasicoModel class for pytest unit testing.
'''

import pandas as pd
import pytest
import basico
from ..models.basico_model import BasicoModel

@pytest.fixture(name="model")
def model_fixture():
    """
    A fixture for the BasicoModel class.
    """
    return BasicoModel(model_id=64, species={"Pyruvate": 100}, duration=2, interval=2)

def test_with_model_id(model):
    """
    Test initialization of BasicoModel with model_id.
    """
    assert model.model_id == 64
    # check if the simulation results are a pandas DataFrame object
    assert isinstance(model.simulate(parameters={'Pyruvate': 0.5, 'KmPFKF6P': 1.5},
                                     duration=2,
                                     interval=2),
                    pd.DataFrame)
    assert isinstance(model.simulate(parameters={None: None}, duration=2, interval=2),
                    pd.DataFrame)
    assert model.description == basico.biomodels.get_model_info(model.model_id)["description"]

def test_with_sbml_file():
    """
    Test initialization of BasicoModel with sbml_file_path.
    """
    model_object = BasicoModel(
        sbml_file_path="aiagents4pharma/talk2biomodels/tests/BIOMD0000000064_url.xml")
    assert model_object.sbml_file_path == \
        "aiagents4pharma/talk2biomodels/tests/BIOMD0000000064_url.xml"
    assert isinstance(model_object.simulate(duration=2, interval=2), pd.DataFrame)
    assert isinstance(model_object.simulate(parameters={'NADH': 0.5}, duration=2, interval=2),
                      pd.DataFrame)

def test_check_model_id_or_sbml_file_path():
    '''
    Test the check_model_id_or_sbml_file_path method of the BioModel class.
    '''
    with pytest.raises(ValueError):
        BasicoModel(species={"Pyruvate": 100}, duration=2, interval=2)

def test_get_model_metadata():
    """
    Test the get_model_metadata method of the BasicoModel class.
    """
    model = BasicoModel(model_id=64)
    metadata = model.get_model_metadata()
    assert metadata["Model Type"] == "SBML Model (COPASI)"
    assert metadata["Parameter Count"] == len(basico.get_parameters())
