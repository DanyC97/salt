'''
A state module to manage installed NPM packages.
'''

# Import salt libs
from salt.exceptions import CommandExecutionError, CommandNotFoundError


def installed(name,
              dir=None,
              runas=None,
              force_reinstall=False,
              **kwargs):
    '''
    Verify that the given package is installed and is at the correct version
    (if specified).

    dir
        The target directory in which to install the package, or None for
        global installation

    runas
        The user to run NPM with

    force_reinstall
        Install the package even if it is already installed
    '''
    ret = {'name': name, 'result': None, 'comment': '', 'changes': {}}

    prefix = name.split('@')[0].strip()

    try:
        installed_pkgs = __salt__['npm.list'](pkg=name, dir=dir)
    except (CommandNotFoundError, CommandExecutionError) as err:
        ret['result'] = False
        ret['comment'] = 'Error installing \'{0}\': {1}'.format(name, err)
        return ret

    installed_pkgs = dict((p.lower(), info) for p, info in installed_pkgs.items())

    if prefix.lower() in installed_pkgs:
        if force_reinstall is False:
            ret['result'] = True
            ret['comment'] = 'Package %s satisfied by %s@%s' % (name, prefix, installed_pkgs[prefix.lower()]['version'])
            return ret

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'NPM package {0} is set to be installed'.format(name)
        return ret

    try:
        call = __salt__['npm.install'](
            pkg=name,
            dir=dir,
            runas=runas
        )
    except (CommandNotFoundError, CommandExecutionError) as err:
        ret['result'] = False
        ret['comment'] = 'Error installing \'{0}\': {1}'.format(name, err)
        return ret

    if call or isinstance(call, list) or isinstance(call, dict):
        ret['result'] = True
        version = call[0]['version']
        pkg_name = call[0]['name']
        ret['changes']["{0}@{1}".format(pkg_name, version)] = 'Installed'
        ret['comment'] = 'Package %s was successfully installed' % name
    else:
        ret['result'] = False
        ret['comment'] = 'Could not install package'

    return ret


def removed(name,
            dir=None,
            runas=None,
            **kwargs):
    '''
    Verify that the given package is not installed.

    dir
        The target directory in which to install the package, or None for
        global installation

    runas
        The user to run NPM with
    '''
    ret = {'name': name, 'result': None, 'comment': '', 'changes': {}}

    try:
        installed_pkgs = __salt__['npm.list'](dir=dir)
    except (CommandExecutionError, CommandNotFoundError) as err:
        ret['result'] = False
        ret['comment'] = 'Error uninstalling \'{0}\': {1}'.format(name, err)
        return ret

    if name not in installed_pkgs:
        ret["result"] = True
        ret["comment"] = "Package is not installed."
        return ret

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'Package {0} is set to be removed'.format(name)
        return ret

    if __salt__["npm.uninstall"](pkg=name,
                                 dir=dir,
                                 runas=runas):
        ret["result"] = True
        ret["changes"][name] = 'Removed'
        ret["comment"] = 'Package was successfully removed.'
    else:
        ret["result"] = False
        ret["comment"] = 'Error removing package.'

    return ret


def bootstrap(
            name,
            runas=None):
    '''
    Bootstraps a node.js application.

    will execute npm install --json on the specified directory


    runas
        The user to run NPM with


    '''
    ret = {'name': name, 'result': None, 'comment': '', 'changes': {}}

    try:
        call = __salt__['npm.install'](
            dir=name,
            runas=runas,
            pkg=None
        )

    except (CommandNotFoundError, CommandExecutionError) as err:
        ret['result'] = False
        ret['comment'] = 'Error Bootstrapping \'{0}\': {1}'.format(name, err)
        return ret

    # npm.install will return a string if it can't parse a JSON result
    if isinstance(call, str):
        ret['result'] = False
        ret['comment'] = 'Could not bootstrap directory'
    else:
        ret['result'] = True
        ret['changes'] = name, 'Bootstrapped'
        ret['comment'] = 'Directory was successfully bootstrapped'

    return ret
