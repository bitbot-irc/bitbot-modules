from src import ModuleManager, utils

VOWELS = "aeiou"

@utils.export("set", utils.Setting("species", "*sniffs at*", example="sandcat"))
class Module(ModuleManager.BaseModule):
    _name = "Species"
    @utils.hook("received.command.species")
    def species(self, event):
        """
        :require_setting: species
        :require_setting_unless: 1
        """

        target_user = event["user"]
        if event["args"]:
            target_name = event["args_split"][0]
            if event["server"].has_user_id(target_name):
                target_user = event["server"].get_user(target_name)
            else:
                raise utils.EventError("I don't know who %s is" % target_name)

        species = target_user.get_setting("species", None)
        if not species == None:
            a_an = "an" if species[0].lower() in VOWELS else "a"
            event["stdout"].write(f"{target_user.nickname} is {a_an} {species}")
        else:
            event["stderr"].write("%s has no species set" %
                target_user.nickname)
