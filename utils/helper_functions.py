

def get_config_value(config, key, cast_type, default=None):
    """Helper function to get and cast config values with optional default."""
    try:
        value = config
        for part in key.split('.'):
            value = value[part]  # Navigate through the nested keys

        if cast_type == 'bool':
            return True if value == 'True' else False
        return cast_type(value)
    except (KeyError, ValueError, TypeError):
        if default is not None:
            return default
        raise ValueError(f"Configuration key '{key}' not found or invalid type")
