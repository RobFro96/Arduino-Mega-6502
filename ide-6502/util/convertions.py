class Convertions:
    @classmethod
    def string_to_int_auto_base(cls, string: str, default=None):
        try:
            return int(string, 0)
        except ValueError:
            return default
