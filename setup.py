import setuptools

install_requires = ['numpy', 'pandas']


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
      name='markovconstraints',
      version='0.1',
      description='A Markov constraint satisfaction problem solver',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/gabrielebarbieri/markovconstraints',
      author='Gabriele Barbieri',
      author_email='gabriele.barbieri83@gmail.com',
      license='MIT',
      packages=setuptools.find_packages(),
      install_requires=install_requires,
      classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
      ],
      python_requires='>=3.6',
)
