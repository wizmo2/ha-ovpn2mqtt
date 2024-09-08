
import os
import json

PREFIX="OVPN2MQTT_"

def load_config(config:json, cat:str=""):
    """Load a saved config as OS environment values"""
    for key in config:
        attr = PREFIX+cat+key.upper()
        print(f"{attr}='{config[key]}'")
        os.environ[attr] = str(config[key])

def get_config_attr(key:str, default):
    """gets environment variable with prefix"""
    return os.environ.get(PREFIX+key, default)

def get_config_list(key:str, default):
    """gets environment variable with prefix as list"""
    list = get_config_attr(key, None)
    if not list and not isinstance(list, str):
        return default
    return list[1:-1].split(',') 

def set_config_attr(key:str, value):
    """sets environment variable with prefix"""
    os.environ[PREFIX+key]=str(value)
