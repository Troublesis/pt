# https://dynaconf.readthedocs.io/en/docs_223/guides/accessing_values.html
# https://www.dynaconf.com/validation/
from dynaconf import Dynaconf, Validator

settings = Dynaconf(
    envvar_prefix=False,
    load_dotenv=True,
    root_path="src/config",
    settings_files=["settings.toml"],
    environments=True,
    validators=[Validator("DEBUG", must_exist=True, is_type_of=bool)],
)

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.

# Example of accessing values with nice comments
# Get a dictionary from settings
# settings["a_dict"]

# Convert a string to boolean from settings
# settings.as_bool("a_boolean")

# Convert a JSON string to a dictionary
# a_dict = '{"key": "value"}'
# settings.as_json("a_dict")

# Get a value from settings, use default if not exists
# settings.get("number", fresh=True)

# Load settings from environment, then get number
# settings.from_env("production").number

# Get a nested value from a dictionary, use default if not exists
# settings.mysql.auth.get("user", "default_user")


if __name__ == "__main__":
    pass
