from src import ModuleManager, utils

URL_DRUG = "http://tripbot.tripsit.me/api/tripsit/getDrug"
URL_COMBO = "http://tripbot.tripsit.me/api/tripsit/getInteraction"
URL_WIKI = "http://drugs.tripsit.me/%s"

INSUFFLATED = ["Insufflated", "Insufflated-IR", "Insufflated-XR"]

METHODS = {
    "iv": ["IV"],
    "shot": ["IV"],

    "im": ["IM"],

    "oral": ["Oral", "Oral-IR", "Oral-XR"],

    "insufflated": INSUFFLATED,
    "snorted": INSUFFLATED,

    "smoked": ["Smoked"]
}

class Module(ModuleManager.BaseModule):
    _name = "tripsit"

    def _get_drug(self, name):
        return utils.http.request(URL_DRUG, get_params={"name": name}).json()

    @utils.hook("received.command.drug", min_args=1)
    @utils.kwarg("help", "Show information about a given drug")
    @utils.kwarg("usage", "<drug> [category]")
    def drug(self, event):
        drug = self._get_drug(event["args_split"][0])
        if drug:
            if not drug["err"]:
                pretty_name = drug["data"][0]["pretty_name"]
                drug = drug["data"][0]["properties"]
                if len(event["args_split"]) > 1:
                    category = event["args_split"][1].lower()
                    if category in drug:
                        data = drug[category]
                        if isinstance(data, list):
                            data = ", ".join(data)
                        event["stdout"].write("%s %s: %s - %s" % (
                            pretty_name, category, data, URL_WIKI % pretty_name))
                    else:
                        event["stderr"].write("Unknown category '%s'" % category)
                else:
                    categories = ", ".join(drug.keys())
                    event["stdout"].write("%s data categories: %s" % (
                        pretty_name, categories))
            else:
                event["stderr"].write("Unknown drug")
        else:
            raise utils.EventsResultsError()

    @utils.hook("received.command.combo", min_args=2)
    @utils.kwarg("help", "Show information about a given drug combination")
    @utils.kwarg("usage", "<drugA> <drugB>")
    def combo(self, event):
        combo = utils.http.request(URL_COMBO, get_params=
            {"drugA":event["args_split"][0], "drugB": event["args_split"][1]}
            ).json()
        if combo:
            if not combo["err"] and combo["data"][0]:
                data = combo["data"][0]
                drug_a = data["interactionCategoryA"]
                drug_b = data["interactionCategoryB"]
                interaction = data["status"]
                event["stdout"].write("%s & %s: %s%s" % (drug_a, drug_b, interaction,
                    "" if not "note" in data else "; %s" % data["note"]))
            else:
                event["stderr"].write("Unknown drug provided")
        else:
            raise utils.EventsResultsError()


    @utils.hook("received.command.idose")
    @utils.kwarg("min_args", 2)
    @utils.kwarg("usage", "<dose> <drug> [method]")
    def idose(self, event):
        dose = event["args_split"][0]

        drug_name = event["args_split"][1]
        method = (event["args_split"][2:] or [None])[0]
        found_method = False
        onset = None
        drug = self._get_drug(drug_name)
        if not drug["err"]:
            drug = drug["data"][0]
            drug_name = drug["pretty_name"]
            method_keys = ["value"]
            methods = []
            if method:
                methods = [method.lower()]
                methods = METHODS.get(methods[0], methods)
                method_keys += methods

            if "formatted_onset" in drug:
                match = list(set(method_keys)&
                    set(drug["formatted_onset"].keys()))
                if match:
                    onset = drug["formatted_onset"][match[0]]
                    found_method = True
                    if match[0] in methods:
                        method = (match or [method])[0]

                if onset and "_unit" in drug["formatted_onset"]:
                    onset = "%s %s" % (
                        onset, drug["formatted_onset"]["_unit"])

        drug_and_method = drug_name
        if method:
            if not found_method:
                method = method.title()

            drug_and_method = "%s via %s" % (drug_and_method, method)

        now = utils.datetime.utcnow()
        event["user"].set_setting("idose",
            [drug_name, dose, method, utils.datetime.format.iso8601(now)])

        human_time = self.exports.get_one("time-localise")(event["user"], now)

        out = "Dosed %s of %s at %s" % (dose, drug_and_method, human_time)
        if not onset == None:
            out += ". You should start feeling effects %s from now" % onset
        event["stdout"].write("%s: %s" % (event["user"].nickname, out))

    @utils.hook("received.command.lastdose")
    def lastdose(self, event):
        lastdose = event["user"].get_setting("idose", None)
        if lastdose == None:
            raise utils.EventError("%s: No last dose saved for you"
                % event["user"].nickname)

        drug_and_method = lastdose[0]
        if lastdose[2]:
            drug_and_method = "%s via %s" % (lastdose[0], lastdose[2])

        dose = lastdose[1]

        now = utils.datetime.utcnow()
        since = (now-utils.datetime.parse.iso8601(lastdose[3])).total_seconds()
        since = utils.datetime.format.to_pretty_time(since, max_units=2)

        event["stdout"].write("%s: You dosed %s of %s %s ago" % (
            event["user"].nickname, dose, drug_and_method, since))

    @utils.hook("received.command.undose")
    def undose(self, event):
        lastdose = event["user"].get_setting("idose", None)
        if not lastdose == None:
            event["user"].del_setting("idose")
            event["stdout"].write("%s: Removed dose of %s" %
                (event["user"].nickname, lastdose[0]))
        else:
            event["stderr"].write("%s: No last dose saved for you" %
                event["user"].nickname)
