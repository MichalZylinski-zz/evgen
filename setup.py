from setuptools import setup

setup(name="EvGen", 
      author = "Michal Zylinski",
      author_email = "michal.zylinski@gmail.com",
      license = "MIT",
      url="https://github.com/MichalZylinski/EvGen",
      version="0.5.3", 
      description="Comprehensive event generation framework",
      packages=['evgen', 'examples'],
      classifiers=[
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3"
          ],      
      install_requires=["Faker", "azure", "user_agent", "numpy", "future", "schwifty"]
      )




