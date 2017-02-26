from setuptools import setup

setup(name="evgen", 
      version="0.5", 
      description="Comprehensive event generation framework",
      packages=['evgen', 'examples'],
      install_requires=["Faker", "azure", "user_agent"]
      )

#temporary python setup.py bdist
#python setup.py sdist
#easy_install -U dist\...egg