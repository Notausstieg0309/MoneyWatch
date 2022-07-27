from setuptools import find_packages, setup

setup(
    name='moneywatch',
    version='0.1',
    packages=find_packages("src"),
    package_dir={'':'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask',
        'Flask_Session',
        'Flask-Babel',
        'Flask-SQLAlchemy',
        'Flask-Migrate',
        'schwifty'
    ],
    tests_require=['pytest'],
    setup_requires=['pytest-runner']

)
