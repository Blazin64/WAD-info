#!/usr/bin/env python
# Compatible with Python 2 and 3.
from struct import unpack
from glob import glob
from codecs import encode, decode
from argparse import ArgumentParser


# Decode the unsigned integers in the WAD


def dec_u32(byte):
    return unpack(">I", decode(byte, 'hex'))[0]


def dec_u16(byte):
    return unpack(">H", decode(byte, 'hex'))[0]


def dec_u8(byte):
    return unpack(">B", decode(byte, 'hex'))[0]


# Round up to the next multiple of 64


def align_64(num):
    return (num + 64 - 1) & - 64


def read_header(file):
    file.seek(0)
    raw_header = encode(file.read(32), 'hex')
    header = []

    for i in range(0, len(raw_header), 8):
        if i in [0, 16, 32, 40, 48, 56]:
            header.append(dec_u32(raw_header[i:i+8]))

        else:
            header.append(decode(raw_header[i:i+8], 'ascii'))

    return header


# Print the 8 fields in the WAD header.


def print_header(header):
    print(("\nHeader size:\t\t{} bytes\n"
           "WAD type:\t\t0x{}\n"
           "Cert chain size:\t{} bytes\n"
           "Reserved:\t\t0x{}\n"
           "Ticket size:\t\t{} bytes\n"
           "TMD size:\t\t{} bytes\n"
           "Data size:\t\t{} bytes\n"
           "Footer size:\t\t{} bytes\n").format(*header))

# Find the offsets of the start and end points of the 5 main WAD segments


def find_offsets(header_size, cert_size, tik_size,
                 tmd_size, data_size, footer_size):
    # Find start and end of certificate chain
    cert_start = align_64(header_size)
    cert_end = cert_start + cert_size - 1
    # Ticket
    tik_start = align_64(cert_end + 1)
    tik_end = tik_start + tik_size - 1
    # Title metadata
    tmd_start = align_64(tik_end + 1)
    tmd_end = tmd_start + tmd_size - 1
    # Data
    data_start = align_64(tmd_end + 1)
    data_end = data_start + data_size - 1
    # Footer
    footer_start = align_64(data_end + 1)
    footer_end = footer_start + footer_size - 1

    # Although the end points are returned by find_offsets,
    # they are not currently used.
    return [
        [cert_start, cert_end],
        [tik_start, tik_end],
        [tmd_start, tmd_end],
        [data_start, data_end],
        [footer_start, footer_end]]


def csv_dump(offsets, file, filename):
    file.seek(offsets[2][0] + 396)
    title_id = encode(file.read(8), 'hex').decode('ascii')

    file.seek(offsets[1][0] + 447)
    titlekey_enc = encode(file.read(16), 'hex').decode('ascii')

    file.seek(offsets[2][0] + 476)
    title_ver = str(dec_u16(encode(file.read(2), 'hex')
                            .decode('ascii'))).zfill(4)

    print("{},{},{},\"{}\"".format(title_id, title_ver,
                                   titlekey_enc, filename))


def print_info(show_csv, show_header, file, filename):
    if encode(file.read(6), 'hex') != b'000000204973':
        print("Error: invalid WAD file")

    else:
        header = read_header(file)

        if show_header:
            print(filename)
            print_header(header)

        if show_csv:
            offsets = find_offsets(header[0], header[2], *header[4:])
            csv_dump(offsets, file, filename)


def batch_mode(show_csv, show_header, path):
    for filename in glob(path+"*.[wW][aA][dD]"):
        file = open(filename, "rb")
        print_info(show_csv, show_header, file, filename)


def main(show_csv, show_header, batch, filename, path):
    if batch:
        batch_mode(show_csv, show_header, path)

    else:
        file = open(filename, "rb")
        print_info(show_csv, show_header, file, filename)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-i', action="store", default="")
    parser.add_argument('--batch', action="store_true", default=False)
    parser.add_argument('--csv', action="store_true", default=False)
    parser.add_argument('--header', action="store_true", default=False)
    parser.add_argument('--path', action="store", default="")

    arguments = parser.parse_args()

    if not (arguments.i or arguments.batch):
        parser.error("Either -i <filename> or --batch must be used.\n")

    if arguments.i and not (arguments.csv or arguments.header):
        parser.error("-i <filename> requires --csv and/or --header\n")

    if arguments.path and not arguments.batch:
        parser.error("--path can only be used with --batch\n")

    if arguments.i and arguments.batch:
        parser.error("-i <filename> cannot be used with --batch")

    main(arguments.csv, arguments.header, arguments.batch,
         arguments.i, arguments.path)
