#!/usr/bin/env python3

import sys

import pikepdf


def unwm_mindshare(in_path, out_path):
    pdf = pikepdf.Pdf.open(in_path)
    for pg in pdf.pages:
        try:
            for key, obj in pg.resources["/XObject"].as_dict().items():
                try:
                    if obj["/PieceInfo"]["/ADBE_CompoundType"]["/Private"] == pikepdf.Name("/Watermark"):
                        del pg.resources["/XObject"][key]
                except KeyError:
                    continue
        except KeyError:
            continue
    pdf.save(out_path)


def main() -> None:
    assert len(sys.argv) == 3
    unwm_mindshare(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()
