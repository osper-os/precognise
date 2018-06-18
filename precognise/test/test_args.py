import argparse
import pytest
from expects import (
    expect,
    equal,
    have_properties,
    raise_error,
    contain,
)

from precognise import (
    command,
    command_arg,
    CommandGroup,
)


class JustOneCommandGroup(CommandGroup):
    """
    Demo command group
    """
    name = 'demo'
    retval = 'success'

    @command('callme')
    def maybe(self):
        """Calls me, maybe.

        This is the documentation for the command; if the `@command` annotation
        has the `help` kwarg, this value will override this documentation.
        """
        return self.retval


class TestCommandGathering(object):

    @pytest.mark.skip
    def test_doc_from_code_doc(self, capsys):

        parser = argparse.ArgumentParser()
        JustOneCommandGroup().build(parser.add_subparsers())
        try:
            parser.parse_args(['demo', 'callme', '--help'])
        except SystemExit:
            pass
        captured = capsys.readouterr()

        expect(captured.out).to(contain('Calls me, maybe.'))

    def test_bad_commandname_raises_error(self):

        parser = argparse.ArgumentParser()
        JustOneCommandGroup().build(parser.add_subparsers())

        def parse():
            parser.parse_args(['demo' 'nosuchcommand'])

        expect(parse).to(raise_error(SystemExit))

    def test_missing_arg_raises_error(self):
        class DemoGroup(CommandGroup):
            name = 'demo'

            @command('callme')
            @command_arg('arg1')
            def maybe(self, arg1):
                return arg1

        parser = argparse.ArgumentParser()
        DemoGroup().build(parser.add_subparsers())

        def parse():
            parser.parse_args(['demo', 'callme'])

        expect(parse).to(raise_error(SystemExit))

    def test_positional_then_optional(self):
        opt_val = 1

        class DemoGroup(CommandGroup):
            name = 'demo'

            @command('callme')
            @command_arg('arg1')
            @command_arg('--opt-arg', required=False, default=opt_val)
            def maybe(self, arg1, opt_arg):
                return (arg1, opt_arg)

        parser = argparse.ArgumentParser()
        DemoGroup().build(parser.add_subparsers())

        arg1_val = 'yay'

        args = parser.parse_args(['demo', 'callme',
                                  arg1_val])

        expect(args).to(have_properties(arg1=arg1_val, opt_arg=opt_val))

        args = parser.parse_args(['demo', 'callme',
                                  arg1_val, '--opt-arg', '2'])

        expect(args).to(have_properties(arg1=arg1_val, opt_arg='2'))

    def test_optional_then_positional(self):
        opt_val = 1

        class DemoGroup(CommandGroup):
            name = 'demo'

            @command('callme')
            @command_arg('--opt-arg', required=False, default=opt_val)
            @command_arg('arg1')
            def maybe(self, opt_arg, arg1):
                return (arg1, opt_arg)

        parser = argparse.ArgumentParser()
        DemoGroup().build(parser.add_subparsers())

        arg1_val = 'yay'

        args = parser.parse_args(['demo', 'callme',
                                  arg1_val])

        expect(args).to(have_properties(arg1=arg1_val, opt_arg=opt_val))

        args = parser.parse_args(['demo', 'callme',
                                  '--opt-arg', '2', arg1_val])

        expect(args).to(have_properties(arg1=arg1_val, opt_arg='2'))

    def test_positional_args(self):
        class DemoGroup(CommandGroup):
            name = 'demo'

            @command('callme')
            @command_arg('arg1')
            @command_arg('arg2')
            def maybe(self, arg1, arg2):
                return arg1, arg2

        parser = argparse.ArgumentParser()
        DemoGroup().build(parser.add_subparsers())

        arg1_val = 'yay'
        arg2_val = 'works'

        args = parser.parse_args([
            'demo', 'callme', arg1_val, arg2_val
        ])

        expect(args).to(have_properties(arg1=arg1_val,
                                        arg2=arg2_val))

        expect(args.func(args.arg1, args.arg2))\
            .to(equal((arg1_val, arg2_val)))

    def test_finds_command(self):

        parser = argparse.ArgumentParser()
        JustOneCommandGroup().build(parser.add_subparsers())

        args = parser.parse_args(['demo', 'callme'])

        expect(args.func()).to(equal(JustOneCommandGroup.retval))
