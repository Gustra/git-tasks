from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()

tests_require=[
    '',
]

setup(name='git-tasks',
      version='0.1.0',
      description='Task manager git plugin',
      long_description=readme(),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: GNU General Public License v3'
          ' or later (GPLv3+)',
          'Programming Language :: Python :: 2.7',
      ],
      keywords='git tasks issues tickets',
      url='http://github.com/Gustra/git-tasks',
      author='Gunnar Strand',
      author_email='Gurra.Strand@gmail.com',
      license='GPL3',
      packages=['git-tasks'],
      install_requires=[
      ],
      include_package_data=True,
      zip_safe=False)
