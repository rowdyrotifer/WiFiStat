import argparse

#Create argparser with help page info.
cli_parser = argparse.ArgumentParser(description="Collect and analyze WiFi LAN network speeds.",
                                 epilog="Project home page:\n  http://marklalor.com/projects/wifistat\nGitHub:\n  http://github.com/MarkLalor/WifiStat",
                                 formatter_class=argparse.RawTextHelpFormatter)

#Get info about the method to actually be used for the test.
cli_parser.add_argument('--iperf', help='iperf server IP to run the test.')
cli_parser.add_argument('--iperfport', default=5001, type=int, help='Specify an alternative iperf server port.')
cli_parser.add_argument('--speedtest', nargs='?', default=-1, help='Specify a speedtest-cli server id to run the test (see speedtest-cli --list, defaults to first one).')
cli_parser.add_argument('--ping', nargs='?', default=-1, help='IP to be pinged in order to test latency.')

#Get info on how to log the data (WiFi network name and location may wish to be recorded)
cli_parser.add_argument('-n', '--network', help='Manually specify the name of this network (default on OS X is the connected WiFi SSID, "network" otherwise).')
cli_parser.add_argument('-l', '--location', default='nolocation', help='Name of location to log speed for (e.g. "basement"), defaults to "nolocation".')

#Other ease of use options
cli_parser.add_argument('-t', '--trials', default=5, type=int, help='Number of trials to run for this location.')
cli_parser.add_argument('-d', '--delay', default=0, type=int, help='Delay between trials.')
cli_parser.add_argument('-p', '--prompt', action='store_true', help='Prompt for [ENTER] keypress between trials.')
cli_parser.add_argument('-v', '--verbose', action='store_true', help='Increase output verbosity')


cli_parser.add_argument('--process', action='store_true', help='Process collected data for analysis.')
cli_parser.add_argument('--server', nargs='?', default=-1, type=int, help='Start and open the web interface.')