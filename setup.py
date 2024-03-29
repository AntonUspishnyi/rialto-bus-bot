import setuptools


with open("README.md") as fp:
    long_description = fp.read()

setuptools.setup(
    name="rialto_bus_bot",
    version="1.0.0",
    description="RialtoBusBot CDK Python app",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="author",
    package_dir={"": "rialto_bus_bot"},
    packages=setuptools.find_packages(where="rialto_bus_bot"),
    install_requires=[
        "aws-cdk-lib>=2.4.0",
        "constructs>=10.0.0",
        "aws-cdk.aws-lambda-python-alpha",
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
)
