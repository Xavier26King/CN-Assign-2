import dpkt
import socket
import pandas as pd
import matplotlib.pyplot as plt

def parse_pcap_fast(pcap_file):
    with open(pcap_file, 'rb') as f:
        pcap = dpkt.pcap.Reader(f)

        data = []
        seq_numbers = {}
        lost_packets = 0
        start_time = None

        for timestamp, buf in pcap:
            eth = dpkt.ethernet.Ethernet(buf)
            if not isinstance(eth.data, dpkt.ip.IP):
                continue
            ip = eth.data
            if not isinstance(ip.data, dpkt.tcp.TCP):
                continue
            
            tcp = ip.data
            src_ip = socket.inet_ntoa(ip.src)
            dst_ip = socket.inet_ntoa(ip.dst)
            length = len(buf)
            window_size = tcp.win
            seq = tcp.seq

            if start_time is None:
                start_time = timestamp
            relative_time = timestamp - start_time

            key = (src_ip, dst_ip)
            if key in seq_numbers and seq in seq_numbers[key]:
                lost_packets += 1
            seq_numbers.setdefault(key, set()).add(seq)

            data.append([relative_time, src_ip, dst_ip, length, window_size])

    df = pd.DataFrame(data, columns=['timestamp', 'src_ip', 'dst_ip', 'length', 'window_size'])
    return df, lost_packets

def calculate_metrics(df, lost_packets):
    df['throughput'] = df['length'].cumsum() / df['timestamp']
    goodput = df[df['length'] > 64]['length'].sum()
    
    total_packets = len(df)
    packet_loss_rate = lost_packets / total_packets if total_packets else 0
    max_window_size = df['window_size'].max()

    return df, goodput, packet_loss_rate, max_window_size

def plot_throughput(df):
    plt.figure(figsize=(10, 5))
    plt.plot(df['timestamp'], df['throughput'], label='Throughput (bytes/sec)', color='b')
    plt.xlabel("Time (s)")
    plt.ylabel("Throughput (bytes/sec)")
    plt.title("Throughput over Time")
    plt.legend()
    plt.grid()
    plt.show()

def plot_window_size(df):
    plt.figure(figsize=(10, 5))
    plt.plot(df['timestamp'], df['window_size'], label='Window Size (bytes)', color='g')
    plt.xlabel("Time (s)")
    plt.ylabel("Window Size (bytes)")
    plt.title("TCP Window Size Over Time")
    plt.legend()
    plt.grid()
    plt.show()

def main():
    pcap_file = "b_westwood_o.pcap"  # Replace with actual file path
    df, lost_packets = parse_pcap_fast(pcap_file)
    df, goodput, packet_loss_rate, max_window_size = calculate_metrics(df, lost_packets)

    print(f"Goodput: {goodput} bytes")
    print(f"Packet Loss Rate: {packet_loss_rate:.2%}")
    print(f"Max Window Size: {max_window_size} bytes")

    plot_throughput(df)
    plot_window_size(df)

if __name__ == "__main__":
    main()
