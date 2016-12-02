from setuptools import setup, find_packages

setup(
    name="python-telegram-dialog-bot",
    version="0.0.1",
    description=
        "Simple Python package for creating "
        "Telegram bots with complex dialogs.",
    url="https://github.com/saluev/python-telegram-dialog-bot",

    author="Tigran Saluev",
    author_email="tigran@saluev.com",

    license="MIT",

    classifiers=[
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    packages=["telegram_dialog"],

    install_requires=['python-telegram-bot'],
)
