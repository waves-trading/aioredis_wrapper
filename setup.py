import setuptools

setuptools.setup(
    name="aioredis_wrapper",
    version="1.6.0",
    author="Alex Shitik",
    author_email="salexs95@yandex.ru",
    description="Wrapper for aioredis library",
    packages=["aioredis_wrapper"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'aioredis==2.0.0',
    ],
    python_requires='>=3.5',
)
