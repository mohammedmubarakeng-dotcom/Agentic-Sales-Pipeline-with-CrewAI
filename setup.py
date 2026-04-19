from setuptools import setup

setup(
    name="agentic-sales-pipeline-crewai",
    version="0.1.0",
    description="A portfolio-grade Agentic Sales Pipeline built with CrewAI for lead qualification and email engagement.",
    author="Your Name",
    license="MIT",
    py_modules=["models", "crews", "flow"],
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "crewai==1.14.1",
        "crewai-tools==1.14.1",
        "pydantic>=2.8,<3.0",
        "PyYAML>=6.0,<7.0",
        "python-dotenv>=1.0,<2.0",
        "pandas>=2.2,<3.0",
        "rich>=13.7,<14.0",
    ],
    python_requires=">=3.11",
)
