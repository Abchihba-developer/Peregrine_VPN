from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8080

class Database:
    def __init__(self):
        self.path = str(Path(__file__).resolve().parent / "VPN_db.sqlite3")
        self.echo = True
    @property
    def get_db_url(self):
        return f"sqlite+aiosqlite:///{self.path}"

class Server:
    SERVER_PUBLIC_KEY = "ваш_публичный_ключ_сервера"
    SERVER_IP = "ваш_IP_адрес"
    VPN_SUBNET = "10.0.0.0/24"

class Settings(BaseSettings):
    run: RunConfig = RunConfig()
    db: Database = Database()
    serv: Server = Server()

    model_config = SettingsConfigDict(env_file="pass")

settings = Settings()
