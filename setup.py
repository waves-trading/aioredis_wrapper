import setuptools

# with open("README.md", "r") as fh:
#     long_description = fh.read()

setuptools.setup(
    name="aioredis_wrapper",
    version="0.0.1",
    author="Alex Shitik",
    author_email="salexs95@yandex.ru",
    description="Wrapper for aioredis library",
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    # url="https://github.com/pypa/sampleproject",
    packages=["aioredis_wrapper"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'aioredis',
    ],
    python_requires='>=3.5',
)
