from setuptools import find_packages, setup
from typing import List


minus_E_dot = "-e ."
def get_requirements(file_path:str)->List[str]:
    requirements=[]
    with open(file_path) as file_object:
        requirements=file_object.readlines()
        requirements= [x.replace("\n","") for x in requirements]
        
        if minus_E_dot in requirements:
            requirements.remove(minus_E_dot)

    return requirements

setup(
    name= 'MovieRecommender',
    version= '0.0.1',
    author= 'Ijeoma',
    author_email= 'orihjane@gmail.com',
    packages= find_packages(),
    install_requires= get_requirements("requirement.txt")
)