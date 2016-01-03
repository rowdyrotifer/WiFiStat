import os
from os import listdir
from os.path import isfile, join
import time
import sys
import utility
import parser
import server
import SimpleHTTPServer
import SocketServer
import socket
import webbrowser
import thread

class Const:
    data_directory = "data"
    throughput = "[Throughput] "
    latency = "[Latency] "


class WiFiStatRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        WiFiStat.Instance().print_verbose('\n'.join("%s: %s" % item for item in vars(self).items()))
        if self.path == '/':
            self.path = 'web/main.html'
        return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
    
class WiFiStatTCPServer(SocketServer.TCPServer):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)

# The "Borg" design pattern: http://code.activestate.com/recipes/66531/
# Best singleton-like pattern for this app?
class WiFiStat:
    args=None
    
    __shared_state = {}
    def __init__(self):
        self.__dict__ = self.__shared_state
        self.args = parser.cli_parser.parse_args()

    def start_server(self, port):
        if port is None:
            port = 8000
        
        tcpserver = server.WiFiStatTCPServer(("", port), server.WiFiStatRequestHandler)
        
        print "Serving at http://localhost:" + str(port)
        webbrowser.open("http://localhost:" + str(port))
        tcpserver.serve_forever()
        
    def stop_server(self, tcpserver):
        def killserver(server):
            server.shutdown()
        thread.start_new_thread(killserver, (tcpserver,))

    def run_command(self, requesthandler, command, value):
        if command == "shutdown" and value == "true":
            self.stop_server(requesthandler.server)
            return "shutdown"

    def run(self):
        #Running the server should never reach the normal code.
        if self.args.server != -1:
            self.start_server(self.args.server)
            exit(0)
        
        #Get a network name from SSID or whatever. 
        if self.args.network is None:
            self.print_verbose("Automatically detecting a network name from SSID...")
            self.args.network = utility.get_best_network_name()
        if not self.args.process:
            print "Network name: " + str(self.args.network)
        
        #Get an IP to ping test for latency.
        if self.args.ping is None:
            self.print_verbose("Automatically detecting a latency test IP...")
            self.args.ping = utility.get_best_ping_ip()
        elif self.args.ping == -1:
            self.print_verbose("Not testing latency/ping.")
        if not self.args.ping is None and self.args.ping != -1:
            print "Latency ping test IP: " + str(self.args.ping) 
        
        #Arguments summary
        self.print_verbose("Arguments processed:")
        for key in self.args.__dict__:
            self.print_verbose("  " + key + ": " + str(self.args.__dict__[key]))
        
        #Check that iperf ip is valid
        if self.args.iperf:
            if not utility.is_valid_ip(self.args.iperf):
                sys.exit("Invalid iperf IP given: " + self.args.iperf)
        #Check that the ping ip is valid
        if self.args.ping != -1:
            if not utility.is_valid_ip(self.args.ping):
                sys.exit("Invalid ping IP given: " + self.args.ping)
                
        #Handle the eight possible combinations.
        #At least one of speedtest, iperf, or ping must be selected.
        #self.args.speedtest == -1 indicates that the --speedtest flag was supplied but no args were given whereas
        #self.args.speedtest, args.iperf, or self.args.ping == None indicates that the flag was not suppied at all
        method = "nothroughput"
        if self.args.iperf is None and not self.args.speedtest == -1:
            method="speedtest"
            if self.args.speedtest is None:
                self.print_verbose("Automatically choosing a speedtest server.")
                self.args.speedtest = utility.getspeedtest_server();
            print "Throughput speedtest server ID: " + self.args.speedtest
        elif not self.args.iperf is None and self.args.speedtest == -1:
            method="iperf"
            print "Throughput iperf server IP: " + self.args.iperf
        elif not self.args.iperf is None and not self.args.speedtest == -1:
            sys.exit("Cannot use both speedtest-cli and iperf to test. Only specify one.")
        else:
            self.print_verbose("Not testing throughput/speed.")
            
        if not self.args.process: print ""
        
        #Print all the args if in verbose mode.
        self.print_verbose("Running WiFiStat with the following parameters:")
        for key, value in vars(self.args).iteritems(): self.print_verbose("  " + key + ": " + str(value))
        
        ##### THROUGHPUT TEST #####
        for i in range(self.args.trials):
            if method == "speedtest":
                pass
            elif method == "iperf":
                print Const.throughput + "iperf test " + str(i+1) + "/" + str(self.args.trials)
                throughput = float(self.iperf_run(self.args.iperf))
                self.log("throughput", self.args.location, throughput)
                print Const.throughput + str(throughput) + " megabits/second."
                if not self.args.delay == 0:
                    print Const.throughput + str(self.args.delay) + "-second delay."
                if self.args.prompt:
                    utility.wait(Const.throughput)
                     
        ##### LATENCY TEST #####  
        if self.args.ping != -1:
            for i in range(self.args.trials):    
                print Const.latency + "ping test " + str(i+1) + "/" + str(self.args.trials)
                ping = self.ping_run(self.args.ping)
                self.log("latency", self.args.location, ping)
                print Const.latency + str(ping) + " milliseconds."
                if not self.args.delay == 0:
                    print Const.latency + str(self.args.delay) + "-second delay."
                    time.sleep(self.args.delay)
                if self.args.prompt:
                    utility.wait(Const.latency)
                    
        ##### PROCESS TEST DATA #####
        if self.args.process:
            print "Processing collected data."
            if not os.path.exists(Const.data_directory):
                sys.exit("No data to process. Use --iperf, --speedtest, or --ping to collect data about network throughput and latency.")
            networks = [x[0] for x in os.walk(Const.data_directory)][1:]
            for network in networks:
                print "Processing data from " + network
                filenames = [f.split(".")[0] for f in listdir(network) if isfile(join(network, f))]
                locations = []
                [locations.append(item) for item in filenames if item not in locations]
                for location in locations:
                    print '  Processing data for location "' + location + '"'
                    with open(network + "/" + location + ".throughput") as f:
                        throughputs = sorted([float(i) for i in f.read().splitlines()])
                    self.print_verbose("  Throughputs: " + str(throughputs))
                    with open(network + "/" + location + ".latency") as f:
                        latencies = sorted([float(i) for i in f.read().splitlines()])
                    self.print_verbose("  Latencies: " + str(latencies))
                    
                    fns_throughput = five_number_summary(throughputs)
                    fns_latency = five_number_summary(latencies)
                    
                    print "  " + str(fns_throughput)
                    print "  " + str(fns_latency)

    ##### TEST FUNCTIONS #####
    
    ### IPERF ###
    def iperf_run(self, ip):
        print Const.throughput + "Testing with iperf server at " + ip
        result = utility.cmd(["iperf", "-c", ip, "-f", "m", "-p", str(self.args.iperfport)], short=False)
        if "failed" in result[0]:
            sys.exit("Failed to connect to iperf server at " + self.args.iperf)
        else:
            return result[0].splitlines()[6].split()[6]

    ### SPEEDTEST CLI ####
    def speedtest_run(self, server):
        pass 

    ### PING ###
    def ping_run(self, ip):
        print Const.latency + "Pinging server at " + ip
        return float(utility.cmd(["ping", "-c", "1", ip]).splitlines()[1].split()[6][5:])

    ### LOG TESTS ###
    def log(self, datatype, location, value):
        filename = Const.data_directory + "/" + self.args.network + "/" + location + "." + datatype
        if not os.path.exists(Const.data_directory + "/" + self.args.network):
            os.makedirs(Const.data_directory + "/" + self.args.network)
        with open(filename, "a+") as datafile:
            datafile.write(str(value) + "\n")
            
    #Only prints if the --verbose flag is specified. 
    def print_verbose(self, string):
        if self.args.verbose:
            print string


def median(values):
    if len(values) % 2 == 0:
        return (values[(len(values)/2)-1] + values[len(values)/2])/2
    else:
        return values[len(values)//2]

def five_number_summary(values):
    fns_min = values[0]
    fns_q1 = median(values[:(len(values)//2)])
    fns_median = median(values)
    fns_q3 = median(values[(len(values)//2+(0 if len(values) % 2 == 0 else 1)):]) 
    fns_max = values[-1]
    return {"min": fns_min, "q1": fns_q1, "median": fns_median, "q3": fns_q3, "max": fns_max}
               
if __name__ == '__main__':
    print "sys.argv: " + str(sys.argv)
    inst = WiFiStat()
    inst.run()