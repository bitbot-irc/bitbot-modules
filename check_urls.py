#--depends-on commands
#--depends-on config
#--require-config virustotal-api-key

import re
from src import ModuleManager, utils

URL_VIRUSTOTAL = "https://www.virustotal.com/vtapi/v2/url/report"
RE_URL = re.compile(r"https?://\S+", re.I)

@utils.export("channelset", utils.BoolSetting("check-urls",
    "Enable/Disable automatically checking for malicious URLs"))
@utils.export("serverset", utils.BoolSetting("check-urls",
    "Enable/Disable automatically checking for malicious URLs"))
@utils.export("channelset", utils.BoolSetting("check-urls-kick",
    "Enable/Disable automatically kicking users that send malicious URLs"))
class Module(ModuleManager.BaseModule):
    _name = "CheckURL"

    @utils.hook("command.regex")
    @utils.kwarg("ignore_action", False)
    @utils.kwarg("command", "check-url")
    @utils.kwarg("pattern", utils.http.REGEX_URL)
    def message(self, event):
        if event["target"].get_setting("check-urls",
                event["server"].get_setting("check-urls", False)):
            event.eat()

            url = utils.http.url_sanitise(event["match"].group(0))
            page = utils.http.request(URL_VIRUSTOTAL, get_params={
                "apikey": self.bot.config["virustotal-api-key"], "resource": url
                }).json()

            if page and page.get("positives", 0) > 1:
                if event["target"].get_setting("check-urls-kick", False):
                    event["target"].send_kick(event["user"].nickname,
                        "Don't send malicious URLs!")
                else:
                    event["stdout"].write("%s just send a malicous URL!" %
                        event["user"].nickname)

