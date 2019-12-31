import random, string
from src import ModuleManager, utils

# Save things people have shouted (caps lock) and shout random saved things back

@utils.export("channelset", utils.BoolSetting("reshout",
    "Whether or not to save shouted things and shout random saved things back"))
class Module(ModuleManager.BaseModule):
    @utils.hook("received.message.channel")
    def message(self, event):
        if event["channel"].get_setting("reshout", False):
            shout = event["message"]
            normalised_shout = "".join(shout.split())
            for char in string.punctuation:
                normalised_shout = normalised_shout.replace(char, "")

            if not len(normalised_shout) > 20:
                return

            i = 0
            for char in normalised_shout:
                if char.isupper():
                    i += 1

            ratio = i/len(normalised_shout)
            if ratio > 0.8:
                shouts = event["channel"].get_setting("shouts", [])
                if shouts:
                    event["channel"].send_message("%s: %s" %
                        (event["user"].nickname, random.choice(shouts)))
                if not event["message"] in shouts:
                    shouts.append(shout)
                    event["channel"].set_setting("shouts", shouts)
