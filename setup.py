from setuptools import setup, find_packages

setup(
    name="appcannon",
    version="0.1.0",
    description="AI-powered app generation CLI tool",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="255BITS",
    author_email="info@255labs.xyz",  # Replace with your contact email
    url="https://github.com/255BITS/appcannon",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "anthropic>=0.6.0",
    ],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "appcannon = appcannon.appcannon:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
