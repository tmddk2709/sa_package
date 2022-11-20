from setuptools import setup, find_packages

# print(["lib"] + [f"lib.{item}" for item in find_packages(where="lib")])
# print(find_packages("sa_package"))

setup(
    name="sa_package",
    version="0.0.9",
    
    url="https://github.com/tmddk2709/sa_package",
    author="Seunga Shin",
    author_email="seungashin9275@gmail.com",

    packages=find_packages(),

    install_requires=[
        "bs4",
        "pandas",
        "gspread",
        "oauth2client",
        "google-api-python-client",
        "google-auth-httplib2",
        "google-auth-oauthlib",
        "selenium",
        "webdriver-manager",
        "packaging"
    ]
)