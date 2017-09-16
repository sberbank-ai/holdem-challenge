from setuptools import setup, find_packages

setup(
    name='sberbank-pypokerengine',
    version='1.1.1',
    author='Peter Romov, ishikota',
    author_email='romovpa@gmail.com, ishikota086@gmail.com',
    description='Poker engine for poker AI development adapted for Sberbank Holdem Challenge 2017',
    license='MIT',
    keywords='python, poker engine, ai, sberbank, holdem challenge',
    url='http://github.com/sberbank-ai/holdem-challenge',
    packages=find_packages(include=('pypokerengine', 'pypokerengine.*',)),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
