from pathlib import Path
from willow.image import Image
from ssimulacra2 import compute_ssimulacra2
from statistics import median, mean
import csv

# =============================================================================
# CONFIGURATION - Adjust these ranges as needed
# =============================================================================

# Quality ranges: (start, end) inclusive, will generate evenly spaced values
# The number of test points is determined by the range size + 1
JPEG_QUALITY_RANGE = (84, 85)
WEBP_QUALITY_RANGE = (85, 95)
AVIF_QUALITY_RANGE = (73, 74)

# =============================================================================


def get_quality_values(quality_range):
    """Generate quality values from a range tuple."""
    start, end = quality_range
    if start > end:
        start, end = end, start
    return list(range(start, end + 1))


def get_output_filename(base_name, fmt, quality):
    """Generate output filename for a given format and quality."""
    extensions = {"jpeg": "jpg", "webp": "webp", "avif": "avif"}
    return f"{base_name}.q{quality}.{extensions[fmt]}"


def encode_image(image, output_path, fmt, quality):
    """Encode image to specified format and quality."""
    with open(output_path, "wb") as f:
        if fmt == "jpeg":
            image.save_as_jpeg(f, quality=quality)
        elif fmt == "webp":
            image.save_as_webp(f, quality=quality)
        elif fmt == "avif":
            image.save_as_avif(f, quality=quality)


def main():
    # Define paths
    input_dir = Path("dataset/CID22_original_set")
    output_dir = Path("output")

    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)

    # Get quality values for each format
    jpeg_qualities = get_quality_values(JPEG_QUALITY_RANGE)
    webp_qualities = get_quality_values(WEBP_QUALITY_RANGE)
    avif_qualities = get_quality_values(AVIF_QUALITY_RANGE)

    print("=" * 80)
    print("IMAGE QUALITY BENCHMARK")
    print("=" * 80)
    print(f"\nJPEG qualities: {jpeg_qualities}")
    print(f"WebP qualities: {webp_qualities}")
    print(f"AVIF qualities: {avif_qualities}")
    print()

    # Get all image files
    image_files = list(input_dir.glob("*"))
    image_files = [f for f in image_files if f.is_file()]
    image_files.sort()

    print(f"Found {len(image_files)} images to process\n")

    # Data structure to store all results
    # scores[fmt][quality] = list of scores
    scores = {
        "jpeg": {q: [] for q in jpeg_qualities},
        "webp": {q: [] for q in webp_qualities},
        "avif": {q: [] for q in avif_qualities},
    }

    # Per-image data for CSV export
    processed_images = []

    # Process each image
    for idx, image_path in enumerate(image_files, 1):
        try:
            print(f"Processing [{idx}/{len(image_files)}]: {image_path.name}")

            # Open image with Willow
            image = Image.open(open(image_path, "rb"))
            base_name = image_path.stem
            png_size = image_path.stat().st_size

            # Store per-image data
            img_data = {
                "name": image_path.name,
                "png_size": png_size,
            }

            # Process each format and quality
            for fmt, qualities in [
                ("jpeg", jpeg_qualities),
                ("webp", webp_qualities),
                ("avif", avif_qualities),
            ]:
                for quality in qualities:
                    output_filename = get_output_filename(base_name, fmt, quality)
                    output_path = output_dir / output_filename

                    # Encode if file doesn't exist
                    if not output_path.exists():
                        encode_image(image, output_path, fmt, quality)

                    # Get file size
                    file_size = output_path.stat().st_size

                    # Calculate SSIMULACRA2 score
                    score = compute_ssimulacra2(str(image_path), str(output_path))

                    # Store results
                    scores[fmt][quality].append(score)
                    img_data[f"{fmt}_q{quality}_size"] = file_size
                    img_data[f"{fmt}_q{quality}_score"] = score

            processed_images.append(img_data)

        except Exception as e:
            print(f"  Error processing {image_path.name}: {e}")
            continue

    # Export CSV
    csv_path = output_dir / "results.csv"
    print(f"\nExporting results to {csv_path}...")

    # Build CSV fieldnames
    fieldnames = ["File", "PNG file size"]
    for fmt, qualities in [
        ("jpeg", jpeg_qualities),
        ("webp", webp_qualities),
        ("avif", avif_qualities),
    ]:
        for quality in qualities:
            fieldnames.append(f"{fmt.upper()} Q{quality} file size")
            fieldnames.append(f"{fmt.upper()} Q{quality} ssimulacra2")

    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for img_data in processed_images:
            row = {
                "File": img_data["name"],
                "PNG file size": img_data["png_size"],
            }
            for fmt, qualities in [
                ("jpeg", jpeg_qualities),
                ("webp", webp_qualities),
                ("avif", avif_qualities),
            ]:
                for quality in qualities:
                    row[f"{fmt.upper()} Q{quality} file size"] = img_data[
                        f"{fmt}_q{quality}_size"
                    ]
                    row[f"{fmt.upper()} Q{quality} ssimulacra2"] = img_data[
                        f"{fmt}_q{quality}_score"
                    ]
            writer.writerow(row)

    print(f"CSV export complete: {csv_path}")

    # Display summary statistics
    print("\n" + "=" * 80)
    print("SSIMULACRA2 SCORE SUMMARY (Median values)")
    print("=" * 80)

    if not processed_images:
        print("No images processed.")
        return

    print(f"\nProcessed {len(processed_images)} images\n")

    # Find reference JPEG quality (highest in range) for comparison
    reference_jpeg_quality = max(jpeg_qualities)
    reference_jpeg_median = median(scores["jpeg"][reference_jpeg_quality])

    print(
        f"Reference: JPEG Q{reference_jpeg_quality} (median: {reference_jpeg_median:.4f})"
    )
    print("-" * 80)

    # JPEG results
    print("\nJPEG Quality Settings:")
    print(
        f"{'Quality':<10} {'Median':<12} {'Mean':<12} {'Min':<12} {'Max':<12} {'vs Ref JPEG':<12}"
    )
    print("-" * 70)
    for quality in jpeg_qualities:
        q_scores = scores["jpeg"][quality]
        med = median(q_scores)
        avg = mean(q_scores)
        diff_pct = (
            ((med - reference_jpeg_median) / reference_jpeg_median * 100)
            if reference_jpeg_median
            else 0
        )
        print(
            f"Q{quality:<9} {med:<12.4f} {avg:<12.4f} {min(q_scores):<12.4f} {max(q_scores):<12.4f} {diff_pct:+.2f}%"
        )

    # WebP results
    print("\nWebP Quality Settings:")
    print(
        f"{'Quality':<10} {'Median':<12} {'Mean':<12} {'Min':<12} {'Max':<12} {'vs Ref JPEG':<12}"
    )
    print("-" * 70)
    for quality in webp_qualities:
        q_scores = scores["webp"][quality]
        med = median(q_scores)
        avg = mean(q_scores)
        diff_pct = (
            ((med - reference_jpeg_median) / reference_jpeg_median * 100)
            if reference_jpeg_median
            else 0
        )
        print(
            f"Q{quality:<9} {med:<12.4f} {avg:<12.4f} {min(q_scores):<12.4f} {max(q_scores):<12.4f} {diff_pct:+.2f}%"
        )

    # AVIF results
    print("\nAVIF Quality Settings:")
    print(
        f"{'Quality':<10} {'Median':<12} {'Mean':<12} {'Min':<12} {'Max':<12} {'vs Ref JPEG':<12}"
    )
    print("-" * 70)
    for quality in avif_qualities:
        q_scores = scores["avif"][quality]
        med = median(q_scores)
        avg = mean(q_scores)
        diff_pct = (
            ((med - reference_jpeg_median) / reference_jpeg_median * 100)
            if reference_jpeg_median
            else 0
        )
        print(
            f"Q{quality:<9} {med:<12.4f} {avg:<12.4f} {min(q_scores):<12.4f} {max(q_scores):<12.4f} {diff_pct:+.2f}%"
        )

    print("\n" + "=" * 80)
    print(f"Processing complete! Results saved to {csv_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
