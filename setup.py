from setuptools import setup, find_packages

setup(
    name='hvp',
    version='0.11',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': ['presets/*.json'],  # Include JSON files in the package
    },
    install_requires=[
        'pydantic>=1.8',
    ],
    description='custom library for human values project',
    author='Mohd Raheel Sayeed',
    author_email='raheel_sayeed@hms.harvard.edu',
    url='https://github.com/raheelsayeed/hvp',  # Update with your repository URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
