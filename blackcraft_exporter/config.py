from pydantic_settings import BaseSettings, SettingsConfigDict, CliApp


class Config(BaseSettings):
	model_config = SettingsConfigDict(
		cli_prog_name='blackcraft_exporter',
		env_prefix='BCE_',
	)

	host: str = '0.0.0.0'
	port: int = 9165
	workers: int = 1


__config = Config()


def get_config() -> Config:
	return __config


def load_config_from_argv() -> Config:
	global __config
	__config = CliApp.run(Config)
	return get_config()
