import random, re, string
from src import ModuleManager, utils

# Save things people have shouted (caps lock) and shout random saved things back

@utils.export("channelset", utils.BoolSetting("reshout",
    "Whether or not to save shouted things and shout random saved things back"))
class Module(ModuleManager.BaseModule):
    def on_load(self):
        if not self.bot.database.has_table("reshout-v2"):
            self.bot.database.execute("""
                CREATE TABLE reshout-v2 (
                    id INTEGER PRIMARY KEY,
                    channel_id INTEGER,
                    shout TEXT,
                    who TEXT,
                    when TEXT
                )
                FOREIGN KEY (channel_id) REFERENCES channels(channel_id),
                UNIQUE (channel_id, shout))""")

    def _add_shout(self, channel, shout, who):
        when = utils.datetime.format.iso8601_now()
        self.bot.database.execute("""
            INSERT OR IGNORE INTO
            reshout-2 (channel_id, shout, who, when)
            VALUES (?, ?)""", [channel.id, shout, who, when])

    def _random_shout(self, channel):
        return (self.bot.database.execute_fetchone("""
            SELECT shout, who, when
            FROM reshout-v2
            WHERE channel_id=?
            ORDER BY RANDOM() LIMIT 1""", [channel.id]) or [None])[0]

    @utils.hook("command.regex")
    @utils.kwarg("command", "reshout")
    @utils.kwarg("pattern", re.compile(".*"))
    def message(self, event):
        if event["target"].get_setting("reshout", False):
            total = 0
            i = 0
            for char in event["message"]:
                if char.isalnum():
                    total += 1
                    if char.isupper():
                        i += 1

            if total >= 20 and (i/total) >= 0.8:
                reshout = self._random_shout(event["target"])
                if reshout:
                    reshout, who, when = reshout
                    event["target"]._last_shout = (who, when)

                    event["target"].send_message("%s: %s" %
                        (event["user"].nickname, reshout))

                self._add_shout(event["target"], event["message"],
                    event["user"].hostmask())

    @utils.hook("received.command.unshout")
    @utils.kwarg("help", "Remove a saved shout")
    @utils.kwarg("usage", "[substring]")
    @utils.kwarg("require_mode", "o")
    @utils.kwarg("require_access", "unshout")
    @utils.kwarg("permission", "unshout")
    def unshout(self, event):
        shout = None
        success, error = None, None
        if event["args"]:
            success = "Deleted shout"
            error = "Shout not found"

            shout = self.bot.database.execute_fetchone("""
                SELECT id, shout FROM reshout WHERE channel_id=?
                AND shout LIKE ? ORDER BY id LIMIT 1""",
                [event["target"].id, "%%%s%%" % event["args"]])
        else:
            success = "Deleted last shout"
            error = "No saved shouts"

            shout = self.bot.database.execute_fetchone("""
                SELECT id, shout FROM reshout WHERE channel_id=?
                ORDER BY id LIMIT 1""", [event["target"].id])
        if shout:
            id, shout = shout
            self.bot.database.execute(
                "DELETE FROM reshout WHERE id=?", [id])
            event["stdout"].write(success)
        else:
            event["stderr"].write(error)
