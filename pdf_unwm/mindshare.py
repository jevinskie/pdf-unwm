#!/usr/bin/env python3

from time import process_time

import pikepdf
from path import Path
from tap import Tap
from tqdm import tqdm


class Args(Tap):
    in_pdf: Path  # Input watermarked MindShare PDF path
    out_pdf: Path  # Output cleaned MindShare PDF path

    def __init__(self, *args, **kwargs):
        super().__init__(*args, underscores_to_dashes=True, **kwargs)

    def configure(self):
        self.add_argument("-i", "--in_pdf")
        self.add_argument("-o", "--out_pdf")


def unwm_mindshare(in_path, out_path):
    print(f"Input size: {in_path.size:_} bytes")
    start_clean_time = process_time()
    with pikepdf.Pdf.open(in_path, inherit_page_attributes=False) as pdf:
        end_pdf_open_time = process_time()
        print(f"Opening PDF took {end_pdf_open_time - start_clean_time:.3f} CPU seconds.")
        for pg in tqdm(
            pdf.pages,
            desc="Clearing watermarks...",
            dynamic_ncols=True,
            unit=" pages",
            unit_scale=True,
        ):
            try:
                for key, obj in pg.resources["/XObject"].as_dict().items():
                    try:
                        if obj["/PieceInfo"]["/ADBE_CompoundType"]["/Private"] == pikepdf.Name("/Watermark"):
                            del pg.resources["/XObject"][key]
                    except KeyError:
                        continue
            except KeyError:
                continue
        print("Removing unreferenced content...")
        start_remove_unref_time = process_time()
        pdf.remove_unreferenced_resources()
        end_remove_unref_time = process_time()
        print(f"Removing unreferenced content took {end_remove_unref_time - start_remove_unref_time:.3f} CPU seconds.")
        end_clean_time = process_time()
        print(f"Cleaning took {end_clean_time - start_clean_time:.3f} CPU seconds.")
        print("Saving cleaned PDF...")
        save_start_time = process_time()
        pdf.save(
            out_path,
            object_stream_mode=pikepdf.ObjectStreamMode.generate,
            stream_decode_level=pikepdf.StreamDecodeLevel.specialized,
            recompress_flate=True,
            deterministic_id=True,
        )
        save_end_time = process_time()
        print(f"Saving took {save_end_time - save_start_time:.3f} CPU seconds.")
    print(f"Output size: {out_path.size:_} bytes")
    print(f"Size ratio: {out_path.size / in_path.size * 100:.3f} %")
    print(f"Overall cleaning took {process_time():.3f} CPU seconds.")
    print(f"Done! Cleaned PDF is at {out_path}")


def main() -> None:
    args = Args().parse_args()
    unwm_mindshare(args.in_pdf, args.out_pdf)


if __name__ == "__main__":
    main()
