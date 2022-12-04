from flask.cli import FlaskGroup
from converter import converter

cli = FlaskGroup(converter)

if __name__ == "__main__":
    cli()