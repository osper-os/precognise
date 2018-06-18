import argparse
import sys


class CommandGroup(object):
    """
    A group of commands.

    Override `name` to define the cli command group name.

    Use `@command` to denote a method on a class as a CLI command.
    Use `@command_arg` to define an argument for that command.
    """
    name = None
    help = None

    def __init__(self):
        assert self.name, 'Command group name must be set - override `name`'

    def build(self, parsers):
        """:type parsers: argparse.ArgumentParser"""
        self.parsers = parsers.add_parser(self.name,
                                          help=self.__doc__).add_subparsers()

        command_fns = self._gather_commands()

        for entry in command_fns:
            if hasattr(entry['fn'], 'cmd_name'):
                entry['name'] = entry['fn'].cmd_name

            parser = self.parsers.add_parser(entry['name'],
                                             help=entry['fn'].help)
            arg_names = []
            for args, kwargs in reversed(getattr(entry['fn'], '_cliargs', [])):
                arg_names.append(*[arg.replace('--', '').replace('-', '_')
                                   for arg in args])
                parser.add_argument(*args, **kwargs)

            parser.set_defaults(func=entry['fn'], cls=self,
                                arg_names=arg_names)

        return self

    def _gather_commands(self):
        command_fns = []
        for prop_name in [key for key in dir(self) if key[0] != '_']:
            prop = getattr(self, prop_name)
            if hasattr(prop, 'is_call'):
                command_fns.append(dict(name=prop_name, fn=prop))
        return command_fns


def command(name, help=None):
    """
    Delineates a class method to be called from the command line
    :param name: the name of the command line arg
    """
    def decorator(fn):
        fn.is_call = True
        fn.cmd_name = name
        if help:
            fn.help = help
        elif fn.__doc__:
            fn.help = fn.__doc__
        else:
            fn.help = ''

        return fn
    decorator.is_dec = True
    return decorator


def command_arg(*args, **kwargs):
    """
    Defines a CLI argument for the particular command.

    This takes the exact parameteres that `argparse`'s `add_argument`
    takes
    """
    the_args = args
    the_kwargs = kwargs

    def decorator(fn):
        args = getattr(fn, '_cliargs', [])
        args.append((the_args, the_kwargs))
        fn._cliargs = args
        return fn

    return decorator


class CliApp(object):
    """
    Base class for all command line apps.

    Assign a series of `CommandGroup` classes to `cmd_groups`.
    """
    cmd_groups = None

    def _add_root_args(self, parser):
        """
        :type parser: argparse.ArgumentParser
        :param parser:
        :return:
        """
        pass

    def _before_run(self, args):
        pass

    def _after_run(self, args):
        pass

    def run(self, args=sys.argv):
        assert self.cmd_groups, 'Must set cmd_groups'

        parser = argparse.ArgumentParser()
        parser = self._add_root_args(parser)

        sub_parsers = parser.add_subparsers()
        for group in self.cmd_groups:
            group().build(sub_parsers)

        args = parser.parse_args(args)
        if hasattr(args, 'cls'):
            args.cls.app = self

        fn_args = {arg_name: getattr(args, arg_name) for arg_name in
                   args.arg_names}

        self._before_run(args)
        try:
            return args.func(**fn_args)
        finally:
            self._after_run(args)


class DemoApp(CliApp):
    def _add_root_args(self, parser):
        parser.add_argument('--hostname', default='localhost:9876')
        parser.add_argument('--protocol', default='http')
        parser.add_argument('--renderer', default='user',
                            choices=['user', 'json', 'yaml'])
        parser.add_argument('--api-version', default='2018-06-08')
        parser.add_argument('--dump-responses', action='store_true')

