#--depends-on commands

import datetime, json
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

            published = "%sZ" % page["Published"].rsplit(".", 1)[0]
            published = datetime.datetime.strptime(published,
                utils.ISO8601_PARSE)
            published = datetime.datetime.strftime(published, "%Y-%m-%d")

            rank = page["cvss"]
            summary = page["summary"]

            event["stdout"].write("%s, %s (%s): %s" %
                (cve_id, published, rank, summary))
        else:
            raise utils.EventsResultsError()
