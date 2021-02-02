import json
import logging

LANGUAGE_FILE = "texts-%s.json"


class Translation:
    def __init__(self, master):
        self.master = master

    def __getitem__(self, key):
        return self.master.get_text(key)


class Settings:
    @classmethod
    def from_file(cls, file):
        try:
            with open(file, encoding="utf8") as json_file:
                data = json.load(json_file)
                settings = cls(data)
        except (IOError, json.JSONDecodeError):
            logging.error("Error reading settings. Ensure settings.json is a valid JSON file.")
            return None

        language = settings.get_language_setting()
        language_file = LANGUAGE_FILE % language
        try:
            with open(language_file, encoding="utf8") as json_file:
                settings.texts = json.load(json_file)
        except (IOError, json.JSONDecodeError):
            logging.error("Error reading texts. Ensure %s is a valid JSON file.", language_file)
            return None

        return settings

    def __init__(self, data):
        self.data = data
        self.texts = None
        self.translation = Translation(self)

    def __get_string(self, key: str, default: str):
        if key not in self.data or not isinstance(self.data[key], str):
            logging.error("Excepted key \"%s\" in settings.json being a string.", key)
            return default
        return self.data[key]

    def get_dpi_awareness(self):
        if "dpi_awareness" not in self.data or not isinstance(self.data["dpi_awareness"], bool):
            logging.error("Excepted key \"dpi_awareness\" in settings.json being a bool.")
            return False
        return self.data["dpi_awareness"]

    def get_icon_path(self):
        return self.__get_string("icon_path", "util/icon.ico")

    def get_language_setting(self):
        return self.__get_string("language", "eng")

    def get_text(self, text_id):
        if text_id not in self.texts:
            logging.error("Excepted key %s in language file.", text_id)
            return text_id
        return self.texts[text_id]

    def get_translation(self) -> Translation:
        return self.translation

    def get_baud_rate(self):
        if "baud_rate" not in self.data or not isinstance(self.data["baud_rate"], int):
            logging.error("Excepted key \"baud_rate\" in settings.json being a int.")
            return 115200
        return self.data["baud_rate"]

    def get_terminal_font(self):
        return self.__get_string("terminal_font", "Courier")

    def get_connect_window_size(self):
        return self.__get_string("connect_window_size", "640x480")

    def get_bus_tracer_window_size(self):
        return self.__get_string("bus_tracer_window_size", "800x600")

    def get_autoconnect_port(self):
        return self.__get_string("autoconnect_port", None)

    def get_memory_browser_window_size(self):
        return self.__get_string("memory_browser_window_size", "400x600")

    def get_use_vasm(self):
        if "use_vasm" not in self.data or not isinstance(self.data["use_vasm"], bool):
            logging.error("Excepted key \"use_vasm\" in settings.json being a bool.")
            return False
        return self.data["use_vasm"]
