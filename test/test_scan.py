import xmlrpc.client
import click
import time


@click.command()
@click.argument('samples', type=click.INT)
@click.argument('int_time', type=click.FLOAT)
@click.argument('runs', type=click.INT)
@click.option('-h', '--host', default='localhost', type=click.STRING)
@click.option('-p', '--port', default=9000, type=click.INT)
def main(samples, int_time, runs, host, port):
    addr = 'http://{}:{}'.format(host, port)
    print('Connecting to {}'.format(addr))
    proxy = xmlrpc.client.ServerProxy(addr)
    channels = ['c1', 'c3']
    low_time = 0.0001
    wait_time = (int_time + low_time) * 3
    for i in range(runs):
        data = {'c1': [], 'c3': []}
        samples_readies = 0
        proxy.set_channels_enabled([], False)
        proxy.set_channels_enabled(channels, True)
        print('Running scan {}'.format(i))
        proxy.start_all(samples, int_time, low_time)
        while not proxy.is_done():
            time.sleep(wait_time)
            new_samples_readies = proxy.get_samples_readies()
            if new_samples_readies > samples_readies:
                for channel in channels:
                    channel_data = proxy.get_channel_data(channel,
                                                          samples_readies,
                                                          new_samples_readies)
                    data[channel] += channel_data
                samples_readies = new_samples_readies

        if samples_readies < samples:
            for channel in channels:
                channel_data = proxy.get_channel_data(channel, samples_readies)
                data[channel] += channel_data

        for channel in channels:
            print('Scan data {}: len {} data{}'.format(channel,
                                                       len(data[channel]),
                                                       data[channel]))


if __name__ == '__main__':
    main()
