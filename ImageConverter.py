from pathlib import Path
from PIL import Image

# Constants
CM_TO_INCH = 1/2.54
DEFAULT_WIDTH_CM = 9
DEFAULT_DPI = 300

class ImageConverter:
    def __init__(self, input_path: str, width_cm: float = DEFAULT_WIDTH_CM, dpi: int = DEFAULT_DPI, output_format: str = 'original'):
        self.input_path = Path(input_path)
        self.width_cm = width_cm
        self.dpi = dpi
        self.output_format = output_format.lower()
        self.output_folder = self._get_output_folder()

    def _get_output_folder(self) -> Path:
        if self.input_path.is_file():
            return self.input_path.parent / "converted"
        else:
            return self.input_path / "converted"

    def _cm_to_pixels(self, cm: float) -> int:
        return int(cm * self.dpi / 2.54)

    def _resize_image(self, image_path: Path, relative_path: Path) -> None:
        try:
            img = Image.open(image_path)
            target_width_px = self._cm_to_pixels(self.width_cm)
            scale = target_width_px / img.width
            target_height_px = int(img.height * scale)

            resized = img.resize((target_width_px, target_height_px), Image.Resampling.LANCZOS)

            # Output path
            final_output_dir = self.output_folder /relative_path
            final_output_dir.mkdir(parents=True, exist_ok=True)

            # Change extension if specified
            if self.output_format != "original":
                output_name = image_path.stem + "." + self.output_format
                output_path = final_output_dir / output_name
            else:
                output_path = final_output_dir / image_path.name

            # Save image
            save_kwargs = {"dpi": (self.dpi, self.dpi)}
            if self.output_format != "original":
                save_kwargs["format"] = self.output_format.upper()

            resized.save(output_path, **save_kwargs)
            print(f"[OK] {image_path.name} -> {output_path}")
        except Exception as e:
            print(f"[ERROR] No se pudo procesar {image_path.name}: {e}")

    def process(self) -> None:
        if not self.input_path.exists():
            print("The path doesn't exist.")
            return
        
        self.output_folder.mkdir(exist_ok=True)

        if self.input_path.is_file():
            if self.input_path.suffix.lower in [".png", ".jpg", ".jpeg", ".tif"]:
                self._resize_image(self.input_path, Path()) # empty relative path
        elif self.input_path.is_dir():
            for img in self.input_path.rglob("*"):
                if (
                    img.is_file() 
                    and img.suffix.lower() in [".png", ".jpg", ".jpeg", ".tif"] 
                    and not self.output_folder in img.parents
                ):
                    relative_path = img.relative_to(self.input_path).parent
                    self._resize_image(img, relative_path)
        else:
            print("Not valid path.")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Resize images for LaTeX with fixed width and DPI.")
    parser.add_argument("input_path", help="Path to image file or folder")
    parser.add_argument("--width", type=float, default=DEFAULT_WIDTH_CM, help=f"Target width in centimeters (default: {DEFAULT_WIDTH_CM})")
    parser.add_argument("--dpi", type=int, default=DEFAULT_DPI, help=f"Output DPI (default: {DEFAULT_DPI})")
    parser.add_argument("--format", default="original", help="Output format: jpg, png, etc. (default: keep original)")

    args = parser.parse_args()

    converter = ImageConverter(
        input_path=args.input_path,
        width_cm=args.width,
        dpi=args.dpi,
        output_format=args.format
    )
    converter.process()