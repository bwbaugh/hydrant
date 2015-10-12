import setuptools


setuptools.setup(
    name='hydrant',
    version='0.1.0',
    url='https://github.com/bwbaugh/hydrant',
    license='BSD',
    author='Wesley Baugh',
    author_email='wesley@bwbaugh.com',
    description='Redirects stdin to Amazon Kinesis Firehose.',
    long_description=open('README.rst').read(),
    packages=setuptools.find_packages(exclude=['tests']),
    install_requires=[
        'click',
    ],
    entry_points={
        'console_scripts': [
            'hydrant = hydrant.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
    ]
)
