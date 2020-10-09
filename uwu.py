#--depends-on commands

from src import ModuleManager, utils
from collections import defaultdict
import re
import json

history = defaultdict(list)

@utils.export("channelset", utils.BoolSetting("allow-uwu",
    "Allow using !uwu in the channel"))

class Module(ModuleManager.BaseModule):
    @utils.hook("received.command.uwu")
    @utils.spec("!<term>lstring")
    def uwu(self, event):
        if not str(event["target"]).startswith("#"):
            event["stderr"].write("This command can only be used in channels.")
            return
        else:
            if not event["target"].get_setting("allow-uwu", False):
                return
            try:
                goback = int(event["spec"][0])
            except:
                goback = 1
            try:
                lastmsg = history[event["target"]][len(history[event["target"]])-1-goback].replace('r','w').replace('l','w').replace('uck','uwk')
            except:
                event["stderr"].write("I couldn't find any messages in my history")
                return
            event["stdout"].write("%s" % (lastmsg))

    @utils.hook("received.message.channel")
    def handle_chanmsg(self, event):
        history[event["channel"]].append('<%s> %s' % (event["user"].nickname, event["message"]))
