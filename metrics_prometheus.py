#--depends-on rest_api

import time
from src import ModuleManager, utils

class Module(ModuleManager.BaseModule):
    @utils.hook("api.get.prometheus")
    def api(self, event):
        now = int(time.time())
        lines = [
            "# HELP server_users Visible user count",
            "# TYPE server_users gauge",
            "# HELP server_channels Channel count",
            "# TYPE server_channels gauge",
        ]

        for server in self.bot.servers.values():
            lines.append("server_users{server=\"%s\"} %d" %
                (str(server), len(server.users)))
            lines.append("server_channels{server=\"%s\"} %d" %
                (str(server), len(server.channels)))


        event["response"].write_text("\n".join(lines)+"\n")
