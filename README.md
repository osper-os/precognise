Precognise
-----

A simple library to build simple command line utils.

Essentially a wrapper around `argparse`.

# Getting started

### Install the package

`pip install precognise`

### Import

`from precognise import command, command_arg, CommandGroup, CliApp`

### Define the CLI app

The CLI app is the main entry point for your application; you can
you can override some methods which are hooks into the process of
running your app.

For example:

    class DemoCliApp(CliApp):
        cmd_groups = []

        def _before_run(self, args):
            print('Running the app, raw args are: {}'.format(args)

        def _add_root_args(self, parser):
            parser.add_argument('--verbose', action='store_true')


Without adding any command groups (see below) this will do nothing,
though the following would work (but do nothing)

`python demoapp.py --verbose`

### Define a CLI group:

    class DemoGroup(CommandGroup):
        """
        Demo command group.

        This documentation will be used for help for this command.
        """
        name = 'demo'

        @command('somecall')
        @command_arg('positionalarg')
        @command_arg('--flag', action='store_true')
        def somecall(positionalarg, flag=False):
            print('Positionalarg: {}, flag: {}'.format(
                positionalarg, flag))

And allow the CliApp to use it:

    class DemoCliApp(CliApp):
        cmd_groups = [DemoGroup]

And now it can be run like so:

`python demoapp.py demo somecall 123`

Result in the output

`Positionalarg: 123, flag: false`

