import time
from src import ModuleManager, utils

class Module(ModuleManager.BaseModule):
    def _float(self, f):
        return "{0:.3f}".format(f)

    @utils.hook("api.get.prometheus")
    def api(self, event):
        now = int(time.time())
        lines = [
            "# HELP server_users Visible user count",
            "# TYPE server_users gauge",

            "# HELP server_channels Channel count",
            "# TYPE server_channels gauge",

            "# HELP server_upload Bytes per second uploaded",
            "# TYPE server_upload gauge",
            "# HELP server_download Bytes per second downloaded",
            "# TYPE server_download gauge"
        ]

        for server in self.bot.servers.values():
            lines.append("server_users{server=\"%s\"} %d" %
                (str(server), len(server.users)))

            lines.append("server_channels{server=\"%s\"} %d" %
                (str(server), len(server.channels)))

            connection_time = time.time()-server.socket.connect_time

            lines.append("server_upload{server=\"%s\"} %s" %
                (str(server),
                self._float(server.socket.bytes_written/connection_time)))

            lines.append("server_download{server=\"%s\"} %s" %
                (str(server),
                self._float(server.socket.bytes_read/connection_time)))


        event["response"].write_text("\n".join(lines)+"\n")
