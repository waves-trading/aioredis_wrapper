import setuptools

setuptools.setup(
    name="aioredis_wrapper",
    version="0.0.2",
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
        'aioredis',
    ],
    python_requires='>=3.5',
)
