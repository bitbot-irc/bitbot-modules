#--depends-on commands

from src import ModuleManager, utils

URL_CVE = "https://cve.circl.lu/api/cve/%s"

class Module(ModuleManager.BaseModule):
    _name = "CVE"

    @utils.hook("received.command.cve", min_args=1)
    def cve(self, event):
        """
        :help: Get information for a CVE number
        :usage: <CVE>
        """
        cve_id = event["args_split"][0].upper()
        if not cve_id.startswith("CVE-"):
            cve_id = "CVE-%s" % cve_id

        page = utils.http.request(URL_CVE % cve_id).json()

        if page:
            cve_id = page["id"]

            published = utils.datetime.format.date_human(
                utils.datetime.parse.iso8601(page["Published"]))

            rank = page["cvss"]
            summary = page["summary"]

            event["stdout"].write("%s, %s (%s): %s" %
                (cve_id, published, rank, summary))
        else:
            raise utils.EventsResultsError()
