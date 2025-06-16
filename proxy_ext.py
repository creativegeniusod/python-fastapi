import os
import shutil
from string import Template
from urllib.parse import urlparse

from pydantic import BaseModel


class ProxyParams(BaseModel):
    proxy_host: str
    proxy_port: int
    proxy_user: str
    proxy_pass: str


    @staticmethod
    def from_url(url: str):
        comps = urlparse(url)
        return ProxyParams(
            proxy_host=comps.hostname,
            proxy_port=comps.port,
            proxy_user=comps.username,
            proxy_pass=comps.password
        )


# creates an extension with proxy parameters
def create_proxy_extension(params: ProxyParams, ext_dir: str):
    shutil.copytree("./proxy_extension", ext_dir, dirs_exist_ok=True)
    bg_content = open("./proxy_extension/background.js").read()
    with open(os.path.join(ext_dir, "background.js"), "w") as f:
        f.write(Template(bg_content).safe_substitute(ProxyParams.model_dump(params)))
