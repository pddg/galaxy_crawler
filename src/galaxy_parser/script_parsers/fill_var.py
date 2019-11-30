import re
import logging

prefix = 'ANSIBLE_VAR_'
UNDEF = prefix + 'UNDEF'
tmpl_var_re = re.compile(r'{{[^}]+}}')
logger = logging.getLogger(__name__)


def _is_var(chars: str) -> bool:
    """
    If given chars are template variable (Jinja2 syntax like `{{ hoge }}`)
    :param chars: Any string
    :return: Whether the given sentence is a template variable or not
    """
    if tmpl_var_re.match(chars):
        return True
    return False


def is_tmpl_var(statement: str) -> bool:
    """
    Return that the statement was Ansible variable
    (filled the value by this module) like `ANSIBLE_VAR_xxx` or not.
    :param statement: A sentence
    :return: If that is the variable, returns True.
    """
    if statement.startswith(prefix):
        return True
    return _is_var(statement)


def fill_variable(statement: str) -> str:
    """
    Fill all variable like {{ hoge }} as ANSIBLE_VAR_UNDEF.
    :param statement: Template statement
    :return: Filled statement
    """
    if tmpl_var_re.search(statement):
        return tmpl_var_re.sub(UNDEF, statement)
    else:
        return statement
