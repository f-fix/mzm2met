#!/usr/bin/env python3
"""
Extract original 8-bit console ROM image from MZM.
Thanks to Liam for finding a bunch of the compressed data regions!
Also Liam realized the formats were already known ones: SZS and LZSS.
See: https://problemkaputt.de/gbatek-lz-decompression-functions.htm
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
"""

import os
import sys

debug_szs = False
debug_lzss = False


def apply_lzss_ofss(mzm, obuf, lzss_ofsss):
    """
    Decode graphics patch blocks which appear to use LZSS, with a header.
    """
    for lzss_ofss in lzss_ofsss:
        lzss_mzm_ofs = lzss_ofss["mzm_ofs"]
        lzss_prg_ofs1 = lzss_ofss["prg_ofs1"]
        lzss_prg_ofs2 = lzss_ofss["prg_ofs2"]
        assert lzss_mzm_ofs in range(  # starting offset must be within MZM image
            len(mzm)
        )
        lzss_hdr = mzm[lzss_mzm_ofs : 4 + lzss_mzm_ofs]
        blk_typ = lzss_hdr[0]
        lzss_len = int.from_bytes(lzss_hdr[1:], "little")
        if blk_typ == 0x10:
            print(
                f"MZM 0x{lzss_mzm_ofs:07X}: LZSS header type 0x{blk_typ:02X} length 0x{lzss_len:06X}"
            )
            print(f"supplied output range: 0x{lzss_prg_ofs1:05X}-0x{lzss_prg_ofs2:05X}")
            print(
                f"computed output range: 0x{lzss_prg_ofs1:05X}-0x{lzss_prg_ofs1 + lzss_len - 1:05X}"
            )
            assert (
                lzss_prg_ofs2 == lzss_prg_ofs1 + lzss_len - 1
            ), f"...-0x{lzss_prg_ofs2:05X} vs ...-0x{lzss_prg_ofs1 + lzss_len - 1:05X}"
        else:
            assert (
                False
            ), f"MZM 0x{lzss_mzm_ofs:07X}: !!! UNKNOWN HEADER TYPE 0x{blk_typ:02X}"
        lzss_mzm_ofs += 4
        assert lzss_prg_ofs1 in range(  # 8-bit PRG overwrite must be within 8-bit PRG
            len(obuf)
        )
        assert (  # 8-bit PRG overwrite range must be positive and within 8-bit PRG
            lzss_prg_ofs2 in range(lzss_prg_ofs1 + 1, len(obuf))
        )
        print(
            f"reading MZM data starting at 0x{lzss_mzm_ofs:07X} and updating 8-bit PRG in range 0x{lzss_prg_ofs1:05X}-0x{lzss_prg_ofs2:05X}"
        )
        lzss_prg_ofs = lzss_prg_ofs1
        while (
            (lzss_prg_ofs in range(lzss_prg_ofs1, 1 + lzss_prg_ofs2))
            and (lzss_prg_ofs2 in range(len(obuf)))
            and (lzss_mzm_ofs in range(len(mzm)))
        ):
            lzss_mask = mzm[lzss_mzm_ofs]
            lzss_mzm_ofs += 1
            if debug_lzss:
                print(f"                 LZSS_MASK 0x{lzss_mask:02X}")
            pos = 0x80
            while (
                pos
                and (lzss_prg_ofs in range(lzss_prg_ofs1, 1 + lzss_prg_ofs2))
                and (lzss_mzm_ofs in range(len(mzm)))
            ):
                if lzss_mask & pos:
                    lzss_r1 = mzm[lzss_mzm_ofs]
                    lzss_mzm_ofs += 1
                    lzss_r2 = mzm[lzss_mzm_ofs]
                    lzss_mzm_ofs += 1
                    lzss_reps = (lzss_r1 >> 4) + 2 + 1
                    lzss_r3 = None
                    lzss_deflection = -1 - (lzss_r2 + ((lzss_r1 & 0xF) << 8))
                    if debug_lzss:
                        print(
                            f"                 LZSS_REP 0x{lzss_r1:02X} 0x{lzss_r2:02X} => lzss_reps {lzss_reps}, lzss_deflection {lzss_deflection} to 0x{lzss_prg_ofs + lzss_deflection:05X}"
                        )
                    while lzss_reps and (
                        lzss_prg_ofs in range(lzss_prg_ofs1, 1 + lzss_prg_ofs2)
                    ):
                        lzss_rbyt = obuf[lzss_prg_ofs + lzss_deflection :][:1]
                        if debug_lzss:
                            print(
                                f"0x{lzss_prg_ofs:05X}: 0x{lzss_rbyt[0]:02X} # {lzss_rbyt}"
                            )
                            assert (
                                obuf[lzss_prg_ofs] == 0x00
                            ), f"PRG 0x{lzss_prg_ofs:05X}: Overwriting non-zero byte 0x{obuf[lzss_prg_ofs]:02X} {obuf[lzss_prg_ofs:1+lzss_prg_ofs]}"
                        obuf = (
                            obuf[:lzss_prg_ofs] + lzss_rbyt + obuf[lzss_prg_ofs + 1 :]
                        )
                        lzss_prg_ofs += 1
                        lzss_reps -= 1

                else:
                    lzss_byt = mzm[lzss_mzm_ofs : 1 + lzss_mzm_ofs]
                    lzss_mzm_ofs += 1
                    if debug_lzss:
                        print(f"0x{lzss_prg_ofs:05X}: 0x{lzss_byt[0]:02X} ! {lzss_byt}")
                    assert (
                        obuf[lzss_prg_ofs] == 0x00
                    ), f"PRG 0x{lzss_prg_ofs:05X}: Overwriting non-zero byte 0x{obuf[lzss_prg_ofs]:02X} {obuf[lzss_prg_ofs:1+lzss_prg_ofs]}"
                    obuf = obuf[:lzss_prg_ofs] + lzss_byt + obuf[1 + lzss_prg_ofs :]
                    lzss_prg_ofs += 1
                pos >>= 1
        print("decompressing updated 8-bit PRG ended at MZM address", hex(lzss_mzm_ofs))
    return obuf


def mzm2met(mzm, ofss):
    """
    The main PRG data appears to be compressed using headerless SZS.
    """
    ofs = ofss[0]["mzm_ofs"]
    assert ofss[0]["prg_ofs1"] == 0  # PRG must start at address 0
    sz = ofss[0]["prg_ofs2"] + 1
    assert sz > 0  # PRG size must be non-zero
    assert ofs in range(len(mzm))  # starting offset must be within MZM image
    buf = mzm[ofs:]
    print("decompressing 8-bit PRG starting at MZM address", hex(ofs))
    obuf = b""
    final = ofs + len(buf)
    npages = sz // (16 * 1024)
    assert sz == npages * 16 * 1024  # PRG size must be a multiple of 16 * 1024 bytes
    hdr = (
        bytes([0x4E, 0x45, 0x53, 0x1A])
        + npages.to_bytes(1, "little")
        + bytes([0x00, 0x10])
        + 9 * b"\0"
    )
    assert len(hdr) == 16
    while buf and (len(obuf) < sz):
        szs_mask, buf = buf[0], buf[1:]
        if debug_szs:
            print(f"                 SZS_MASK 0x{szs_mask:02X}")
        pos = 0x80
        while pos and buf and (len(obuf) < sz):
            if szs_mask & pos:
                szs_lbyt, buf = buf[:1], buf[1:]
                if debug_szs:
                    print(f"0x{len(obuf):05X}: 0x{szs_lbyt[0]:02X}   {szs_lbyt}")
                obuf += szs_lbyt
            else:
                szs_r1, szs_r2, buf = buf[0], buf[1], buf[2:]
                szs_reps = (szs_r1 >> 4) + 2
                szs_r3 = None
                if szs_reps == 2:
                    szs_reps += 16
                    szs_r3, buf = buf[0], buf[1:]
                    szs_reps += szs_r3
                szs_deflection = -1 - (szs_r2 + ((szs_r1 & 0xF) << 8))
                if szs_r3 is None:
                    if debug_szs:
                        print(
                            f"                 SZS_REP 0x{szs_r1:02X} 0x{szs_r2:02X} -- => szs_reps {szs_reps}, szs_deflection {szs_deflection} to 0x{len(obuf) + szs_deflection:05X}"
                        )
                else:
                    if debug_szs:
                        print(
                            f"                 SZS_REP 0x{szs_r1:02X} 0x{szs_r2:02X} 0x{szs_r3:02X} => szs_reps {szs_reps}, szs_deflection {szs_deflection} to 0x{len(obuf) + szs_deflection:05X}"
                        )
                while szs_reps and (len(obuf) < sz):
                    szs_rbyt = obuf[len(obuf) + szs_deflection :][:1]
                    if debug_szs:
                        print(f"0x{len(obuf):05X}: 0x{szs_rbyt[0]:02X} * {szs_rbyt}")
                    obuf += szs_rbyt
                    szs_reps -= 1
            pos >>= 1
    print("decompressing 8-bit PRG ended at MZM address", hex(final - len(buf)))
    obuf = apply_lzss_ofss(mzm, obuf, ofss[1:])

    return hdr + obuf


def main():
    (  # usage: python3 mzm2met IN MZM_OFS:0-PRG_MAXADDR+MZM_OFS:PRG_OFS1-PRG_OFS2+... OUT
        _,
        infn,
        ofss,
        outfn,
    ) = sys.argv
    ofss = [ofseg.split(":") for ofseg in ofss.split("+")]
    ofss = [
        (
            int(  # usage: python3 mzm2met IN MZM_OFS:0-PRG_MAXADDR+MZM_OFS:PRG_OFS1-PRG_OFS2+... OUT
                mzm_ofs, 0
            ),
            *(
                int(  # usage: python3 mzm2met IN MZM_OFS:0-PRG_MAXADDR+MZM_OFS:PRG_OFS1-PRG_OFS2+... OUT
                    prg_ofs, 0
                )
                for prg_ofs in prg_ofss.split("-")
            ),
        )
        for mzm_ofs, prg_ofss in ofss  # usage: python3 mzm2met IN MZM_OFS:0-PRG_MAXADDR+MZM_OFS:PRG_OFS1-PRG_OFS2+... OUT
    ]
    ofss = [
        dict(mzm_ofs=mzm_ofs, prg_ofs1=prg_ofs1, prg_ofs2=prg_ofs2)
        for mzm_ofs, prg_ofs1, prg_ofs2 in ofss  # usage: python3 mzm2met IN MZM_OFS:0-PRG_MAXADDR+MZM_OFS:PRG_OFS1-PRG_OFS2+... OUT.NES
    ]
    mzm = open(infn, "rb").read()
    print(f"read {infn!r}")
    nes = mzm2met(mzm, ofss)
    if os.path.exists(outfn):
        print(f"removing old {outfn!r}")
        os.unlink(outfn)
    open(outfn, "wb").write(nes)
    print(f"wrote {outfn!r}")


if __name__ == "__main__":
    main()
