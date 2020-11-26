import re
import string

from robot.api import ResultVisitor
from six.moves.urllib.parse import unquote

from . import listener_gp
from .variables import _variables


class RobotResultsVisitor(ResultVisitor):
    _link_pattern = re.compile("src=[\"\']([^\"\']+)[\"\']")

    def start_result(self, result):
        if "RP_LAUNCH" not in _variables:
            _variables["RP_LAUNCH"] = result.suite.name
        if "RP_LAUNCH_DOC" not in _variables:
            _variables["RP_LAUNCH_DOC"] = result.suite.doc

    def start_suite(self, suite):
        attrs = {
            'id': suite.id,
            'longname': suite.longname,
            'doc': suite.doc,
            'metadata': suite.metadata,
            'source': suite.source,
            'suites': suite.suites,
            'tests': suite.tests,
            'totaltests': getattr(suite.statistics, 'all', suite.statistics).total,
            'starttime': suite.starttime
        }
        listener_gp.start_suite(suite.name, attrs)

    def end_suite(self, suite):
        attrs = {
            'id': suite.id,
            'longname': suite.longname,
            'doc': suite.doc,
            'metadata': suite.metadata,
            'source': suite.source,
            'suites': suite.suites,
            'tests': suite.tests,
            'totaltests': getattr(suite.statistics, 'all', suite.statistics).total,
            'starttime': suite.starttime,
            'endtime': suite.endtime,
            'elapsedtime': suite.elapsedtime,
            'status': suite.status,
            'statistics': suite.statistics,
            'message': suite.message,
        }
        listener_gp.end_suite(None, attrs)

    def start_test(self, test):
        attrs = {
            'id': test.id,
            'longname': test.longname,
            # 'originalname': test.originalname,
            'doc': test.doc,
            'tags': list(test.tags),
            'critical': getattr(test, 'critical', ''),
            'template': '',
            # 'lineno': test.lineno,
            'starttime': test.starttime,
        }
        listener_gp.start_test(test.name, attrs)

    def end_test(self, test):
        attrs = {
            'id': test.id,
            'longname': test.longname,
            # 'originalname': test.originalname,
            'doc': test.doc,
            'tags': list(test.tags),
            'critical': getattr(test, 'critical', ''),
            'template': '',
            # 'lineno': test.lineno,
            'starttime': test.starttime,
            'endtime': test.endtime,
            'elapsedtime': test.elapsedtime,
            'status': test.status,
            'message': test.message,
        }
        listener_gp.end_test(test.name, attrs)

    def start_keyword(self, kw):
        attrs = {
            'type': string.capwords(kw.type),
            'kwname': kw.kwname,
            'libname': kw.libname,
            'doc': kw.doc,
            'args': kw.args,
            'assign': kw.assign,
            'tags': kw.tags,
            'starttime': kw.starttime,
        }
        listener_gp.start_keyword(kw.name, attrs)

    def end_keyword(self, kw):
        attrs = {
            'type': string.capwords(kw.type),
            'kwname': kw.kwname,
            'libname': kw.libname,
            'doc': kw.doc,
            'args': kw.args,
            'assign': kw.assign,
            'tags': kw.tags,
            'starttime': kw.starttime,
            'endtime': kw.endtime,
            'elapsedtime': kw.elapsedtime,
            'status': 'PASS' if kw.assign else kw.status,
        }
        listener_gp.end_keyword(kw.name, attrs)

    def start_message(self, msg):
        if msg.message:
            message = {
                'message': msg.message,
                'level': msg.level,
            }
            try:
                m = self.parse_message(message['message'])
                message["message"] = m[0]
                listener_gp.log_message_with_image(message, m[1])
            except (AttributeError, IOError):
                # noinspection PyBroadException
                try:
                    listener_gp.log_message(message)
                except Exception:
                    pass

    def parse_message(self, msg):
        m = self._link_pattern.search(msg)
        return [m.group(), unquote(m.group(1))]
