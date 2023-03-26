
"""
gptty: context-preserving chatGPT CLI wrapper

"""

__name__ = "gptty"
__author__ = "Sig Janoska-Bedi"
__credits__ = ["Sig Janoska-Bedi"]
__version__ = "0.1.3"
__license__ = "MIT"
__maintainer__ = "Sig Janoska-Bedi"
__email__ = "signe@atreeus.com"

# general packages
import click
import os
import asyncio

# app specific requirements
from gptty.config import get_config_data
from gptty.gptty import create_chat_room, run_query

# Define color codes
CYAN = "\033[1;36m"
RED = "\033[1;31m"
RESET = "\033[0m"
# borrowed version callback from https://click.palletsprojects.com/en/7.x/options/#callbacks-and-eager-options
def print_version(ctx, param, value, version=__version__):
    if not value or ctx.resilient_parsing:
        return
    click.echo(f'gptty version {version}')
    ctx.exit()

@click.group()
@click.option('--version', '-v', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True, help="Show app version.")
def main():
  pass


@click.command()
@click.option('--config_path', '-c', default=os.path.join(os.getcwd(),'gptty.ini'), help="Path to config file.")
def chat(config_path):
  
  """
  Run the gptty chat client
  """

  asyncio.run(chat_async_wrapper(config_path))

async def chat_async_wrapper(config_path):
  title = r"""
                 _   _         
     ____  ____ | | | |        
    / __ `/ __ \| |_| |_ _   _ 
   / /_/ / /_/ /| __| __| | | |
   \__, / .___/ | |_| |_| |_| |
  /____/_/       \__|\__|\__, |
                          __/ |
                         |___/ 
  """

  # Print the text in cyan
  click.echo(f"{CYAN}{title}\nWelcome to gptty (v.{__version__}), a ChatGPT wrapper in your TTY.\nType :help in the chat interface if you need help getting started.{RESET}\n")
  
  if not os.path.exists(config_path):
      click.echo(f"{RED}FAILED to access app config file at {config_path}. Are you sure this is a valid config file? Run `gptty chat --help` for more information.")
      return

  # load the app configs
  configs = get_config_data(config_file=config_path)
  
  # create the output file if it doesn't exist
  with open (configs['output_file'], 'a'): pass
  
  # Run the main function
  # create_chat_room(configs=configs, config_path=config_path)
  # asyncio.run(create_chat_room(configs=configs, config_path=config_path))
  await create_chat_room(configs=configs, config_path=config_path)


@click.command()
# @click.option('--log', '-l', is_flag=True, callback=print_version,
#               expose_value=False, is_eager=True, help="Show question log.")
@click.option('--config_path', '-c', default=os.path.join(os.getcwd(),'gptty.ini'), help="Path to config file.")
@click.option('--question', '-q', multiple=True, help='Repeatable list of questions.')
@click.option('--tag', '-t', default="", help='Tag to categorize your query. [optional]')
def query(config_path, question, tag):
  """
  Submit a gptty query
  """

  asyncio.run(query_async_wrapper(config_path, question, tag))


async def query_async_wrapper(config_path, question, tag):
  # load the app configs
  configs = get_config_data(config_file=config_path)
  
  # create the output file if it doesn't exist
  with open (configs['output_file'], 'a'): pass

  await run_query(questions=question, tag=tag, configs=configs, config_path=config_path)



main.add_command(chat)
main.add_command(query)

if __name__ == "__main__":
  main()