from src import ModuleManager, utils

@utils.export("set", utils.Setting("orientation", "owo", example="pansexual"))
class Module(ModuleManager.BaseModule):
    _name = "Orientation"
    @utils.hook("received.command.orientation")
    def orientation(self, event):
        """
        :require_setting: orientation
        :require_setting_unless: 1
        """

        target_user = event["user"]
        if event["args"]:
            target_name = event["args_split"][0]
            if event["server"].has_user_id(target_name):
                target_user = event["server"].get_user(target_name)
            else:
                raise utils.EventError("I don't know who %s is" % target_name)

        orientation = target_user.get_setting("orientation", None)
        if orientation is None:
            event["stderr"].write("%s has no orientation set" %
                target_user.nickname)
            return

        event["stdout"].write(f"{target_user.nickname} is {orientation.strip()}")
