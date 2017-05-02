from setuptools import setup

install_requires = ['numpy', 'pandas']

setup(name='markovchain',
      version='0.1',
      description='Markov constraints',
      url='http://github.com/gabrielebarbieri/markovchain',
      author='Gabriele Barbieri',
      author_email='gabriele.barbieri83@gmail.com',
      license='MIT',
      packages=['markovchain'],
      install_requires=install_requires,
      zip_safe=False)
