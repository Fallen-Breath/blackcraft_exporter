from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict, CliApp, CliImplicitFlag


class Config(BaseSettings):
	model_config = SettingsConfigDict(
		cli_prog_name='blackcraft_exporter',
		env_prefix='BCE_',
		cli_kebab_case=True,
	)

	host: str = Field(default='0.0.0.0', description='Host to listen on')
	port: int = Field(default=9165, description='Port to listen on')
	workers: int = Field(default=1, description='The number of uvicorn worker')

	debug: CliImplicitFlag[bool] = Field(default=False, description='Enable debug logging')

	dev_mode: CliImplicitFlag[bool] = Field(default=False, description='Enable development mode. Not for production use')

__config = Config()


def get_config() -> Config:
	return __config


def load_config_from_argv() -> Config:
	global __config
	__config = CliApp.run(Config)
	return get_config()
