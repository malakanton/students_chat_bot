import yaml
from loguru import logger
import sys


class Secrets:
    _dotenv_path: str

    def __init__(self, dotenv_path: str = ".env") -> None:
        self._dotenv_path = dotenv_path
        self.dict()

    def _parse_dotenv(self) -> dict:
        attrs_dict = dict()
        with open(self._dotenv_path) as dotenv_file:
            lines = dotenv_file.readlines()

        for line in lines:
            if line:
                if "=" in line:
                    key, val = line.split("=")
                    val = val.strip()
                    if val:
                        attrs_dict[key] = val.strip()
        return attrs_dict

    def _parse_values(self, attrs_dict: dict) -> None:
        for k, v in attrs_dict.items():
            if "," in v:
                v = v.split(",")
                try:
                    v = [int(item) for item in v]
                except ValueError:
                    pass

            elif v[-1].isdigit():
                try:
                    v = int(v)
                except ValueError:
                    pass

            setattr(self, k, v)

    def dict(self) -> dict:
        env_dct = self._parse_dotenv()
        self._parse_values(env_dct)
        return {
            k: v
            for k, v in self.__dict__.items()
            if k not in {"dotenv_path", "attrs_dict"}
        }


class Config:
    _instance = None

    def __init__(self, config_file: str = "./config.yml", dotenv_file: str = "../.env"):
        self._config_file = config_file
        self._mode = "prod"
        self.secrets = Secrets(dotenv_file)

    def _load_config(self):
        try:
            with open(self._config_file, "r") as file:
                self._config_docs = yaml.safe_load(file)
        except FileNotFoundError:
            logger.error(f"Config file not found on path {self._config_file}!")

    def _set_cfg_attrs(self):
        for name, value in self._config_docs.items():
            setattr(self, name, value)

    def _switch_mode(self):
        if sys.platform in {"darwin", "win32"}:
            self._mode = "dev"

    @staticmethod
    def _apply_mode(_o: object, mode: str):
        attrs = [att for att in _o.__dict__.keys() if att[0].isupper()]
        for att in attrs:
            if att.startswith(f"{mode.upper()}_"):
                setattr(_o, att.replace(f"{mode.upper()}_", ""), getattr(_o, att))

    def _get_secrets(self):
        try:
            self.secrets.dict()
            self._apply_mode(self.secrets, self._mode)
        except Exception as e:
            logger.error(f"Failed to parse secrets: {e}")

    def set_config(self):
        try:
            self._switch_mode()
            self._get_secrets()
            self.reset_config()
            logger.success("Config set up successfully")
        except Exception as e:
            logger.error(f"Failed to set config file: {e}")

    def reset_config(self):
        try:
            self._load_config()
            self._set_cfg_attrs()
            self._apply_mode(self, self._mode)

        except Exception as e:
            logger.error(f"Failed to reset config: {e}")

    def update_config(self, updated_dict: dict) -> bool:
        if self._validate_new_dict(updated_dict):
            self._update_yaml_file(updated_dict)
            self.reset_config()
            return True
        else:
            return False

    def dict(self) -> dict:
        return {
            k: v
            for k, v in self.__dict__.items()
            if not k.startswith("_") and not isinstance(v, Secrets)
        }

    def _update_yaml_file(self, updated_dict: dict) -> None:
        with open(self._config_file, 'w') as file:
            yaml.dump(updated_dict, file, default_flow_style=False)

    def _validate_new_dict(self, updated_dict: dict) -> bool:
        config_fields = self.dict()
        for key, value in updated_dict.items():
            if key not in config_fields or value in (['', ' ', None, []]):
                return False
        return True


cfg = Config()
