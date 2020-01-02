import random, re, string
from src import ModuleManager, utils

# Save things people have shouted (caps lock) and shout random saved things back

@utils.export("channelset", utils.BoolSetting("reshout",
    "Whether or not to save shouted things and shout random saved things back"))
class Module(ModuleManager.BaseModule):
    @utils.hook("command.regex")
    @utils.kwarg("command", "reshout")
    @utils.kwarg("pattern", re.compile(".*"))
    def message(self, event):
        if event["target"].get_setting("reshout", False):
            shout = "".join(event["message"].split())

            total = 0
            i = 0
            for char in shout:
                if char.isalnum():
                    total += 1
                    if char.isupper():
                        i += 1

            if total >= 20 and (i/total) >= 0.8:
                shouts = event["target"].get_setting("shouts", [])
                if shouts:
                    event["target"].send_message("%s: %s" %
                        (event["user"].nickname, random.choice(shouts)))
                if not event["message"] in shouts:
                    shouts.append(shout)
                    event["target"].set_setting("shouts", shouts)
