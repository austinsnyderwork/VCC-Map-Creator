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

        config = configparser.ConfigParser()
        self.config = config.read(config_path)

    def __call__(self, key: str, cast_type):
        value = self.config
        for part in key.split('.'):
            value = value[part]  # Navigate through the nested keys

        if cast_type is bool:
            return True if value == 'True' else False
        elif cast_type is list:
            list_ = [item.strip() for item in value.split(',')]
            return list_
        return cast_type(value)

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
