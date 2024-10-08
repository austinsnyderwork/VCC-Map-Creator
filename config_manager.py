import configparser


class ConfigManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance.load_config()
        return cls._instance

    def load_config(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.config = config

    def get_config_value(self, key, cast_type):
        if not ConfigManager._instance:
            ConfigManager()

        value = self.config
        for part in key.split('.'):
            value = value[part]  # Navigate through the nested keys

        if cast_type is bool:
            return True if value == 'True' else False
        elif cast_type is list:
            list_ = [item.strip() for item in value.split(',')]
            return list_
        return cast_type(value)

    def get_config_values(self, key, subkeys, cast_types):
        if not ConfigManager._instance:
            ConfigManager()

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

