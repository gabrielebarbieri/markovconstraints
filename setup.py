from setuptools import setup

install_requires = ['numpy', 'pandas']


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='markovconstraints',
      version='0.1',
      description='A Markov constraint satisfaction problem solver',
      long_description=readme(),
      url='https://github.com/gabrielebarbieri/markovconstraints',
      author='Gabriele Barbieri',
      author_email='gabriele.barbieri83@gmail.com',
      license='MIT',
      packages=['markovconstraints'],
      install_requires=install_requires,
      zip_safe=False)
