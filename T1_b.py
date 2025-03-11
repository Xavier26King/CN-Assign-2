from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink

def create_topology():
    net = Mininet(controller=RemoteController, switch=OVSSwitch, link=TCLink)

    # Add controller
    print("*** Adding controller")
    c0 = net.addController('c0', ip='127.0.0.1', port=6633)
    
    # Add switches
    print("*** Adding switches")
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    s3 = net.addSwitch('s3')
    s4 = net.addSwitch('s4')

    # Add hosts
    print("*** Adding hosts")
    h1 = net.addHost('h1', ip='10.0.0.1')
    h2 = net.addHost('h2', ip='10.0.0.2')
    h3 = net.addHost('h3', ip='10.0.0.3')
    h4 = net.addHost('h4', ip='10.0.0.4')
    h5 = net.addHost('h5', ip='10.0.0.5')
    h6 = net.addHost('h6', ip='10.0.0.6')
    h7 = net.addHost('h7', ip='10.0.0.7')

    # Create links between switches and hosts with bandwidth and delay settings
    print("*** Creating links")
    net.addLink(h1, s1, bw=10, delay='5ms')
    net.addLink(h2, s1, bw=10, delay='5ms')
    net.addLink(s1, s2, bw=20, delay='10ms')
    net.addLink(h3, s2, bw=10, delay='5ms')
    net.addLink(h4, s2, bw=10, delay='5ms')
    net.addLink(s2, s3, bw=20, delay='10ms')
    net.addLink(h5, s3, bw=10, delay='5ms')
    net.addLink(h6, s3, bw=10, delay='5ms')
    net.addLink(s3, s4, bw=20, delay='10ms')
    net.addLink(h7, s4, bw=10, delay='5ms')

    # Start the network
    print("*** Starting network")
    net.start()

    # Start TCP server on h7 using port 6633
    print("*** Starting TCP server on h7")
    h7.cmd('iperf3 -s -p 6633 &')

    # Start TCP clients with staggered timing
    print("*** Starting TCP clients with staggered timing")

    h1.cmd(f'iperf3 -c 10.0.0.7 -p 6633 -b 10M -P 10 -t 150 -C bbr &')  # H1 starts at T=0s
    h3.cmd(f'sleep 15 && iperf3 -c 10.0.0.7 -p 6633 -b 10M -P 10 -t 120 -C bbr &')  # H3 starts at T=15s
    h4.cmd(f'sleep 30 && iperf3 -c 10.0.0.7 -p 6633 -b 10M -P 10 -t 90 -C bbr &')  # H4 starts at T=30s

    # Test connectivity
    print("*** Testing connectivity")
    net.pingAll()
    
    # Open Mininet CLI for interaction
    print("*** Running CLI")
    CLI(net)

    # Stop the network
    print("*** Stopping network")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_topology()
