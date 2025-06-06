import configparser


class ConfigManager:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)

        return cls._instance

    def __init__(self, config_path: str = 'config.ini'):
        cls = self.__class__
        if cls._initialized:
            return

        self.config = configparser.ConfigParser()
        self.config.read(config_path)

    def __call__(self, section: str, key: str, cast_type):
        if cast_type == int:
            return self.config.getint(section, key)
        elif cast_type == float:
            return self.config.getfloat(section, key)
        elif cast_type == bool:
            return self.config.getboolean(section, key)
        elif cast_type == str:
            return self.config.get(section, key)
        elif cast_type == list:
            return [item.strip() for item in self.config.get(section, key).split(',')]
        else:
            raise ValueError(f"Unsupported cast_type: {cast_type}")

    def fetch_config_values(self, key, subkeys, cast_types):
        nest = self.config[key]

        outputs = []
        for subkey, cast_type in zip(subkeys, cast_types):
            value = nest[subkey]

            if cast_type is bool:
                outputs.append(True if value == 'True' else False)
            elif cast_type is list:
                list_ = [item.strip() for item in value.split(',')]
                outputs.append(list_)
            else:
                outputs.append(cast_type(value))
        return outputs

    def fetch_config_value(self, key, cast_type):
        return cast_type(self.config)
