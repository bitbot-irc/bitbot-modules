import datetime, os.path
from src import EventManager, ModuleManager, utils

ROOT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOGS_DIRECTORY = os.path.join(ROOT_DIRECTORY, "logs")

@utils.export("channelset", utils.BoolSetting("urlsnarf",
    "Whether or not to record URLs sent to this channel"))
class Module(ModuleManager.BaseModule):
    def _log_file(self, server_name, channel_name):
        return open(os.path.join(LOGS_DIRECTORY,
            "%s%s.log" % (server_name, channel_name)), "a")
    def _log(self, server, channel, user, url):
        if channel.get_setting("log", False):
            with self._log_file(str(server), str(channel)) as log:
                timestamp = datetime.datetime.now().strftime("%x %X")
                log.write("%s %s %s\n" % (timestamp, user.hostmask(), url))

    @utils.hook("command.regex")
    @utils.kwarg("ignore_action", False)
    @utils.kwarg("priority", EventManager.PRIORITY_MONITOR)
    @utils.kwarg("command", "urlsnarf")
    @utils.kwarg("pattern", utils.http.REGEX_URL)
    def urlsnarf(self, event):
        if event["target"].get_setting("urlsnarf", False):
            url = utils.http.url_sanitise(event["match"].group(0))
            self._log(event["server"], event["target"], event["user"], url)
