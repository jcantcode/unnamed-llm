# Havn't tested this, but it should work for xoring weights to be compatible with distribution licenses.
import os
import click
import gzip
import numpy
from pathlib import Path
import shutil

@click.command()
@click.argument('dst')
@click.argument('src_payload')
@click.argument('src_base')
@click.option('--encode', is_flag=True, help='Enable encoding mode.')
@click.option('--compress', is_flag=True, help='Enable compression mode.')
def xor_dir(dst, src_payload, src_base, encode, compress):
    """Performs XOR operations on binary files."""
    decode = not encode

    def xor_files(dst, src_payload, src_base, block_size=4096, compress=False, decode=False):
        open_func = gzip.open if (compress and decode) or (not compress and not decode) else open
        mode = 'rb' if decode else 'wb'

        with open_func(src_payload, 'rb') as fp_payload, open_func(src_base, 'rb') as fp_base, gzip.open(dst, mode) as fp:
            while True:
                buf1 = numpy.array(bytearray(fp_payload.read(block_size)), dtype=numpy.uint8)
                buf2 = numpy.array(bytearray(fp_base.read(block_size)), dtype=numpy.uint8)
                padding = len(buf1) - len(buf2)
                if padding > 0:
                    buf2 = numpy.pad(buf2, (0, padding), 'constant', constant_values=(0,))
                if padding < 0:
                    buf2 = buf2[:len(buf1)]
                buf = numpy.bitwise_xor(buf1, buf2)
                fp.write(buf)
                if len(buf1) < block_size:
                    break

    xor = xor_files
    Path(dst).mkdir(parents=True, exist_ok=True)
    shutil.copy(Path(src_payload) / "added_tokens.json", Path(dst) / "added_tokens.json")
    for path in os.listdir(src_payload):
        click.echo(f"[*] Processing '{path}'")
        try:
            xor(os.path.join(dst, path), os.path.join(src_payload, path), os.path.join(src_base, path), compress=compress, decode=decode)
        except Exception as e:
            click.echo(f"Exception when processing '{path}'")

if __name__ == "__main__":
    xor_dir()
