from setuptools import find_packages, setup


def long_description():
    with open('README.md', 'r', encoding='utf-8') as f:
        content = f.read()
    return content


setup(
    name="BitTorrent",
    version='1.0',
    description="BitTorrent(DHT) Python implementation",
    long_description=long_description(),
    author="wessup",
    packages=find_packages(),
    license='MIT',
    python_requires='>=3.7',
)
