from src import ModuleManager, utils

URL_DRUG = "http://tripbot.tripsit.me/api/tripsit/getDrug"
URL_COMBO = "http://tripbot.tripsit.me/api/tripsit/getInteraction"
URL_WIKI = "http://drugs.tripsit.me/%s"

class Module(ModuleManager.BaseModule):
    _name = "tripsit"

    def _get_drug(self, name):
        return utils.http.request(URL_DRUG, get_params={"name": name},
            json=True)

    @utils.hook("received.command.drug", min_args=1)
    @utils.kwarg("help", "Show information about a given drug")
    @utils.kwarg("usage", "<drug> [category]")
    def drug(self, event):
        drug = self._get_drug(event["args_split"][0])
        if drug:
            if not drug.data["err"]:
                pretty_name = drug.data["data"][0]["pretty_name"]
                drug = drug.data["data"][0]["properties"]
                if len(event["args_split"]) > 1:
                    category = event["args_split"][1].lower()
                    if category in drug:
                        data = drug[category]
                        if isinstance(data, list):
                            data = ", ".join(data)
                        event["stdout"].write("%s %s: %s (%s)" % (
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
            {"drugA":event["args_split"][0], "drugB": event["args_split"][1]},
            json=True)
        if combo:
            if not combo.data["err"] and combo.data["data"][0]:
                data = combo.data["data"][0]
                drug_a = data["interactionCategoryA"]
                drug_b = data["interactionCategoryB"]
                interaction = data["status"]
                event["stdout"].write("%s & %s: %s%s" % (drug_a, drug_b, interaction,
                    "" if not "note" in data else "; %s" % data["note"]))
            else:
                event["stderr"].write("Unknown drug provided")
        else:
            raise utils.EventsResultsError()


