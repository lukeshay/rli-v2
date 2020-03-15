from setuptools import setup


setup(
    name="rli",
    version="0.0.1",
    url="https://github.com/LukeShay/lcli",
    author="LukeShay",
    author_email="shay.luke17@gmail.com",
    description="cli",
    packages=["rli", "rli.commands"],
    include_package_data=True,
    platforms="any",
    entry_points="""
        [console_scripts]
        rli=rli.cli:cli
    """,
)
