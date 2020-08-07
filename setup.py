import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="byte_converter",
    version="0.1.1",
    author="AdriBloober",
    author_email="adrianbloober@gmail.com",
    description="Translate python objects to bytes.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AdriBloober/ByteConverter",
    packages=["byte_converter"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
