"""
Templates!
"""

import json
import logging

import config

class TemplateDB(object):
    """
    Stores templates, not even a DB
    """
    def __init__(self):
        try:
            self.templates = json.loads(open(config.templatedb).read())
        except:
            logging.debug("No templates file exists")
            self.templates = dict()

    def get_template(self, template):
        logging.debug("Looking up %s" % (template))
        try:
            return self.templates[template]
        except:
            raise TemplateException("Template not found")

    def add_template(self, template, text):
        if len(text) > 256:
            return False
        self.templates[template] = text
        self._sync_template()
        return True

    def del_template(self, template):
        del self.templates[template]
        self._sync_template()

    def list_templates(self, search=""):
        return [(k, v) for k, v in self.templates.items()]

    def _sync_template(self):
        open(config.templatedb, 'w').write(json.dumps(self.templates))


class TemplateException(ValueError):
    pass

