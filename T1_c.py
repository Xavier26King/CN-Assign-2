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
    h7 = net.addHost('h7', ip='10.0.0.7')  # Server

    # Create links with specified bandwidths
    print("*** Creating links with specific bandwidth")
    net.addLink(s1, s2, bw=100, delay='5ms')  # S1-S2: 100Mbps
    net.addLink(s2, s3, bw=50, delay='10ms')  # S2-S3: 50Mbps
    net.addLink(s3, s4, bw=100, delay='5ms')  # S3-S4: 100Mbps

    # Extra links for scenarios
    net.addLink(h1, s1, bw=10, delay='5ms')
    net.addLink(h2, s1, bw=10, delay='5ms')
    net.addLink(h3, s2, bw=10, delay='5ms')
    net.addLink(h4, s2, bw=10, delay='5ms')
    net.addLink(h7, s4, bw=10, delay='5ms')  # Server at S4

    # Start the network
    print("*** Starting network")
    net.start()

    # Start TCP server on h7
    print("*** Starting TCP server on h7")
    h7.cmd('iperf3 -s -p 6633 &')

    # *** Test cases ***
    # (1) S2-S4 active, H3 as client -> H7 as server
    print("*** Running test: Link S2-S4 active, H3 as client")
    h3.cmd('iperf3 -c 10.0.0.7 -p 6633 -b 10M -P 10 -t 150 -C bbr &')

    # (2) S1-S4 active, multiple clients
    print("*** Running test: Link S1-S4 active")
    
    # (a) Clients: H1, H2 -> Server: H7
    h1.cmd('iperf3 -c 10.0.0.7 -p 6633 -b 10M -P 10 -t 150 -C bbr &')
    h2.cmd('iperf3 -c 10.0.0.7 -p 6633 -b 10M -P 10 -t 150 -C bbr &')

    # (b) Clients: H1, H3 -> Server: H7
    h1.cmd('iperf3 -c 10.0.0.7 -p 6633 -b 10M -P 10 -t 150 -C bbr &')
    h3.cmd('iperf3 -c 10.0.0.7 -p 6633 -b 10M -P 10 -t 120 -C bbr &')

    # (c) Clients: H1, H3, H4 -> Server: H7
    h1.cmd('iperf3 -c 10.0.0.7 -p 6633 -b 10M -P 10 -t 150 -C bbr &')
    h3.cmd('iperf3 -c 10.0.0.7 -p 6633 -b 10M -P 10 -t 120 -C bbr &')
    h4.cmd('iperf3 -c 10.0.0.7 -p 6633 -b 10M -P 10 -t 90 -C bbr &')

    # (d) Configure loss on S2-S3 link and repeat (c)
    print("*** Configuring link loss on S2-S3")
    net.configLinkStatus('s2', 's3', 'down')
    net.addLink(s2, s3, bw=50, delay='10ms', loss=1)  # 1% packet loss
    print("*** Running test with 1% packet loss")
    h1.cmd('iperf3 -c 10.0.0.7 -p 6633 -b 10M -P 10 -t 150 -C bbr &')
    h3.cmd('iperf3 -c 10.0.0.7 -p 6633 -b 10M -P 10 -t 120 -C bbr &')
    h4.cmd('iperf3 -c 10.0.0.7 -p 6633 -b 10M -P 10 -t 90 -C bbr &')

    # Increase loss to 5%
    net.configLinkStatus('s2', 's3', 'down')
    net.addLink(s2, s3, bw=50, delay='10ms', loss=5)  # 5% packet loss
    print("*** Running test with 5% packet loss")
    h1.cmd('iperf3 -c 10.0.0.7 -p 6633 -b 10M -P 10 -t 150 -C bbr &')
    h3.cmd('iperf3 -c 10.0.0.7 -p 6633 -b 10M -P 10 -t 120 -C bbr &')
    h4.cmd('iperf3 -c 10.0.0.7 -p 6633 -b 10M -P 10 -t 90 -C bbr &')

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
