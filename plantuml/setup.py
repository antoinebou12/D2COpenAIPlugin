from setuptools import setup

setup(
    name='plantuml',
    version=__version_string__,
    description='Python interface with the PlantUML web. PlantUML is a library for generating UML diagrams from a simple text markup language',
    long_description=open('README.md', 'r').read(),
    url='https://github.com/antoinebou12/py-plantuml/',
    author="Antoine Boucher",
    author_email="antoine.boucher012@gmail.com",
    license='BSD',
    py_modules=['pyplantuml'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: Implementation :: CPython',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=['httplib2', "httpx", "typer", "docker"],
    keywords=['plantuml', 'uml']
)
