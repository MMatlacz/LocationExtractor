from setuptools import setup

try:
    import pypandoc

    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    long_description = open('README.md').read()

setup(
    name='LocationExtractor',
    version='1.0.0',
    description='Extract countries, regions and cities from text',
    python_require='>=3.0.0',
    long_description=long_description,
    license='MIT',
    packages=['location_extractor'],
    install_requires=open('requirements.txt').readlines(),
    include_package_data=True,
    package_data={
        '': ['data/*'],
    }
)
