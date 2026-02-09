# mzm2met
Extract original 8-bit console ROM image from MZM

Thanks to Liam for finding a bunch of the compressed data regions!

Also Liam realized the formats were already known ones: SZS and LZSS.

See: https://problemkaputt.de/gbatek-lz-decompression-functions.htm

## Usage
Example usage:
```bash
python3 mzm2met.py \
    mzm.in \
      0x07dcf60:0x00000-0x1ffff` : \
    `+0x07f6d98:0x04d60-0x0515f` : \
    `+0x07f4828:0x05160-0x0555f` : \
    `+0x07f4540:0x08d60-0x0915f` : \
    `+0x07f524c:0x09160-0x0955f` : \
    `+0x07f4b88:0x0cd60-0x0d15f` : \
    `+0x07f4f18:0x0d160-0x0d55f` : \
    `+0x07f4248:0x10d60-0x1127f` : \
    `+0x07f6068:0x11360-0x1155f` : \
    `+0x07f6760:0x14d60-0x151af` : \
    `+0x07f3a08:0x18000-0x1899f` : \
    `+0x07f7344:0x189a0-0x18a9f` : \
    `+0x07f7028:0x18be0-0x190df` : \
    `+0x07f33fc:0x190e0-0x1988f` : \
    `+0x07f7018:0x19890-0x1989f` : \
    `+0x07f7544:0x19980-0x199bf` : \
    `+0x07f73f8:0x19da0-0x19eef` : \
    `+0x07f5a8c:0x19ef0-0x1a6ef` : \
    `+0x07f6520:0x1a6f0-0x1a94f` : \
    `+0x07f6b18:0x1a950-0x1a9bf` : \
    `+0x07f6268:0x1a9c0-0x1ac9f` : \
    `+0x07f5574:0x1aca0-0x1b29f` : \
    `+0x07f59fc:0x1b2a0-0x1b32f` : \
    `+0x07f61b4:0x1b330-0x1b3ef` : \
    `+0x07f5fa8:0x1b3f0-0x1b4af` : \
    `+0x07f6b94:0x1b4c0-0x1b8bf \
    met.out
```
MZM this was developed for:
```
8.0M mzm.in crc32:5c61a844 md5:ebbce58109988b6da61ebb06c7a432d5 sha1:5de8536afe1f0078ee6fe1089f890e8c7aa0a6e8 sha256:fc94f65380b65b870a30b9b04b39cca1dc63d6e46a4a373d3904adc0912ebc37 size:8388608

8.0M mzm-eur.in crc32:f1d92e63 md5:07930e72d4824bd63827a1a823cc8829 sha1:0fd107445a42e6f3a3e5ce8c865f412583179903 sha256:0d061ff36c62ebbf2220e106ea34abdb8d813943515b35007fd8fdba3ed019b0 size:8388608
```
