from pathlib import Path
from willow.image import Image
from ssimulacra2 import compute_ssimulacra2
from statistics import mean
import csv


def main():
    # Define paths
    input_dir = Path("dataset/CID22_original_set")
    output_dir = Path("output")

    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)

    # Get all image files
    image_files = list(input_dir.glob("*"))
    image_files = [f for f in image_files if f.is_file()]

    print(f"Found {len(image_files)} images to process\n")

    # Track scores
    jpeg_scores = []
    jpeg_wip_scores = []
    webp_scores = []
    avif_80_scores = []
    avif_wip_scores = []
    processed_images = []

    # Process each image
    for image_path in image_files:
        try:
            print(f"Processing: {image_path.name}")

            # Open image with Willow
            image = Image.open(open(image_path, "rb"))

            # Get base filename without extension
            base_name = image_path.stem

            # Save as JPEG with quality 85
            jpeg_path = output_dir / f"{base_name}.jpg"
            with open(jpeg_path, "wb") as f:
                image.save_as_jpeg(f, quality=85)

            # Save as JPEG with quality (WIP)
            jpeg_wip_path = output_dir / f"{base_name}.wip.jpg"
            with open(jpeg_wip_path, "wb") as f:
                image.save_as_jpeg(f, quality=76)

            # Save as WebP
            webp_path = output_dir / f"{base_name}.webp"
            with open(webp_path, "wb") as f:
                image.save_as_webp(f, quality=80)

            # Save as AVIF with quality 80
            avif_80_path = output_dir / f"{base_name}.avif"
            with open(avif_80_path, "wb") as f:
                image.save_as_avif(f, quality=80)

            # Save as AVIF with lower quality (WIP)
            avif_wip_path = output_dir / f"{base_name}.wip.avif"
            with open(avif_wip_path, "wb") as f:
                # TODO: Change this value for different tests
                image.save_as_avif(f, quality=73)

            # Get file sizes
            png_size = image_path.stat().st_size
            jpeg_size = jpeg_path.stat().st_size
            jpeg_wip_size = jpeg_wip_path.stat().st_size
            webp_size = webp_path.stat().st_size
            avif_80_size = avif_80_path.stat().st_size
            avif_wip_size = avif_wip_path.stat().st_size

            # Calculate SSIMULACRA2 scores
            print("  Calculating quality scores...")

            # PNG vs JPEG
            jpeg_score = compute_ssimulacra2(str(image_path), str(jpeg_path))
            jpeg_scores.append(jpeg_score)
            print(f"    PNG vs JPEG: {jpeg_score:.4f}")
            print(f"    JPEG size: {jpeg_size / 1024:.2f} KB")

            # PNG vs JPEG WIP
            jpeg_wip_score = compute_ssimulacra2(str(image_path), str(jpeg_wip_path))
            jpeg_wip_scores.append(jpeg_wip_score)
            print(f"    PNG vs JPEG (WIP): {jpeg_wip_score:.4f}")
            print(f"    JPEG (WIP) size: {jpeg_wip_size / 1024:.2f} KB")

            webp_score = compute_ssimulacra2(str(image_path), str(webp_path))
            webp_scores.append(webp_score)
            print(f"    PNG vs WebP: {webp_score:.4f}")
            print(f"    WebP size: {webp_size / 1024:.2f} KB")
            # PNG vs AVIF 80
            avif_80_score = compute_ssimulacra2(str(image_path), str(avif_80_path))
            avif_80_scores.append(avif_80_score)
            print(f"    PNG vs AVIF (Q80): {avif_80_score:.4f}")
            print(f"    AVIF (Q80) size: {avif_80_size / 1024:.2f} KB")
            # PNG vs AVIF wip (WIP)
            avif_wip_score = compute_ssimulacra2(str(image_path), str(avif_wip_path))
            avif_wip_scores.append(avif_wip_score)
            print(f"    PNG vs AVIF (Q-WIP): {avif_wip_score:.4f}")
            print(f"    AVIF (Q-WIP) size: {avif_wip_size / 1024:.2f} KB")

            processed_images.append(
                {
                    "name": image_path.name,
                    "png_size": png_size,
                    "jpeg_size": jpeg_size,
                    "jpeg_wip_size": jpeg_wip_size,
                    "webp_size": webp_size,
                    "avif_80_size": avif_80_size,
                    "avif_wip_size": avif_wip_size,
                    "jpeg_score": jpeg_score,
                    "jpeg_wip_score": jpeg_wip_score,
                    "webp_score": webp_score,
                    "avif_80_score": avif_80_score,
                    "avif_wip_score": avif_wip_score,
                }
            )

        except Exception as e:
            print(f"  Error processing {image_path.name}: {e}")
            continue

    # Export CSV
    csv_path = output_dir / "results.csv"
    print(f"\nExporting results to {csv_path}...")
    with open(csv_path, "w", newline="") as csvfile:
        fieldnames = [
            "File",
            "PNG file size",
            "JPEG file size",
            "JPEG (WIP) file size",
            "AVIF (Q80) file size",
            "AVIF (WIP) file size",
            "WebP file size",
            "JPEG ssimulacra2 score",
            "JPEG (WIP) ssimulacra2 score",
            "AVIF (Q80) ssimulacra2 score",
            "AVIF (WIP) ssimulacra2 score",
            "WebP ssimulacra2 score",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for img_data in processed_images:
            writer.writerow(
                {
                    "File": img_data["name"],
                    "PNG file size": img_data["png_size"],
                    "JPEG file size": img_data["jpeg_size"],
                    "JPEG (WIP) file size": img_data["jpeg_wip_size"],
                    "AVIF (Q80) file size": img_data["avif_80_size"],
                    "AVIF (WIP) file size": img_data["avif_wip_size"],
                    "WebP file size": img_data["webp_size"],
                    "JPEG ssimulacra2 score": img_data["jpeg_score"],
                    "JPEG (WIP) ssimulacra2 score": img_data["jpeg_wip_score"],
                    "AVIF (Q80) ssimulacra2 score": img_data["avif_80_score"],
                    "AVIF (WIP) ssimulacra2 score": img_data["avif_wip_score"],
                    "WebP ssimulacra2 score": img_data["webp_score"],
                }
            )
    print(f"CSV export complete: {csv_path}")

    # Display summary
    print("\n" + "=" * 80)
    print("QUALITY SCORE SUMMARY")
    print("=" * 80)

    if jpeg_scores and jpeg_wip_scores and avif_80_scores and avif_wip_scores:
        print(f"\nProcessed {len(processed_images)} images\n")

        # Overall statistics
        print("Overall Statistics:")
        print("-" * 80)
        print("PNG vs JPEG:")
        print(f"  Mean:   {mean(jpeg_scores):.4f}")
        print(f"  Min:    {min(jpeg_scores):.4f}")
        print(f"  Max:    {max(jpeg_scores):.4f}")

        print("\nPNG vs JPEG (WIP):")
        print(f"  Mean:   {mean(jpeg_wip_scores):.4f}")
        print(f"  Min:    {min(jpeg_wip_scores):.4f}")
        print(f"  Max:    {max(jpeg_wip_scores):.4f}")

        print("\nPNG vs WebP:")
        print(f"  Mean:   {mean(webp_scores):.4f}")
        print(f"  Min:    {min(webp_scores):.4f}")
        print(f"  Max:    {max(webp_scores):.4f}")

        print("\nPNG vs AVIF (Q80):")
        print(f"  Mean:   {mean(avif_80_scores):.4f}")
        print(f"  Min:    {min(avif_80_scores):.4f}")
        print(f"  Max:    {max(avif_80_scores):.4f}")

        print("\nPNG vs AVIF (Q-WIP):")
        print(f"  Mean:   {mean(avif_wip_scores):.4f}")
        print(f"  Min:    {min(avif_wip_scores):.4f}")
        print(f"  Max:    {max(avif_wip_scores):.4f}")

        # Comparison
        avg_jpeg = mean(jpeg_scores)
        avg_jpeg_wip = mean(jpeg_wip_scores)
        avg_webp = mean(webp_scores)
        avg_avif_80 = mean(avif_80_scores)
        avg_avif_wip = mean(avif_wip_scores)
        print("\nComparison:")
        print(
            f"  WebP is {((avg_webp - avg_jpeg) / avg_jpeg * 100):+.2f}% {'better' if avg_webp > avg_jpeg else 'worse'} than JPEG on average"
        )
        print(
            f"  JPEG (WIP) is {((avg_jpeg_wip - avg_jpeg) / avg_jpeg * 100):+.2f}% {'better' if avg_jpeg_wip > avg_jpeg else 'worse'} than JPEG on average"
        )
        print(
            f"  AVIF (Q80) is {((avg_avif_80 - avg_jpeg) / avg_jpeg * 100):+.2f}% {'better' if avg_avif_80 > avg_jpeg else 'worse'} than JPEG on average"
        )
        print(
            f"  AVIF (Q-WIP) is {((avg_avif_wip - avg_jpeg) / avg_jpeg * 100):+.2f}% {'better' if avg_avif_wip > avg_jpeg else 'worse'} than JPEG on average"
        )
        print(
            f"  AVIF (Q-WIP) is {((avg_avif_wip - avg_avif_80) / avg_avif_80 * 100):+.2f}% {'better' if avg_avif_wip > avg_avif_80 else 'worse'} than AVIF (Q80) on average"
        )

        # Size statistics
        print("\n" + "=" * 80)
        print("FILE SIZE STATISTICS")
        print("=" * 80)

        # Calculate average sizes
        avg_png_size = mean([img["png_size"] for img in processed_images])
        avg_jpeg_size = mean([img["jpeg_size"] for img in processed_images])
        avg_jpeg_wip_size = mean([img["jpeg_wip_size"] for img in processed_images])
        avg_webp_size = mean([img["webp_size"] for img in processed_images])
        avg_avif_80_size = mean([img["avif_80_size"] for img in processed_images])
        avg_avif_wip_size = mean([img["avif_wip_size"] for img in processed_images])

        print("\nAverage File Sizes:")
        print("-" * 80)
        print(f"PNG (original):     {avg_png_size / 1024:.2f} KB")
        print(f"JPEG:                {avg_jpeg_size / 1024:.2f} KB")
        print(f"JPEG (WIP):          {avg_jpeg_wip_size / 1024:.2f} KB")
        print(f"WebP:                {avg_webp_size / 1024:.2f} KB")
        print(f"AVIF (Q80):          {avg_avif_80_size / 1024:.2f} KB")
        print(f"AVIF (Q-WIP):        {avg_avif_wip_size / 1024:.2f} KB")

        print("\nSize Savings vs JPEG:")
        print("-" * 80)
        webp_savings = (avg_jpeg_size - avg_webp_size) / avg_jpeg_size * 100
        jpeg_wip_savings = (avg_jpeg_size - avg_jpeg_wip_size) / avg_jpeg_size * 100
        avif_80_savings = (avg_jpeg_size - avg_avif_80_size) / avg_jpeg_size * 100
        avif_wip_savings = (avg_jpeg_size - avg_avif_wip_size) / avg_jpeg_size * 100
        print(
            f"WebP:                {webp_savings:+.2f}% ({avg_webp_size / avg_jpeg_size:.2%} of JPEG size)"
        )
        print(
            f"JPEG (WIP):          {jpeg_wip_savings:+.2f}% ({avg_jpeg_wip_size / avg_jpeg_size:.2%} of JPEG size)"
        )
        print(
            f"AVIF (Q80):          {avif_80_savings:+.2f}% ({avg_avif_80_size / avg_jpeg_size:.2%} of JPEG size)"
        )
        print(
            f"AVIF (Q-WIP):        {avif_wip_savings:+.2f}% ({avg_avif_wip_size / avg_jpeg_size:.2%} of JPEG size)"
        )

        print("\nSize Savings vs PNG:")
        print("-" * 80)
        jpeg_savings_vs_png = (avg_png_size - avg_jpeg_size) / avg_png_size * 100
        jpeg_wip_savings_vs_png = (
            (avg_png_size - avg_jpeg_wip_size) / avg_png_size * 100
        )
        webp_savings_vs_png = (avg_png_size - avg_webp_size) / avg_png_size * 100
        avif_80_savings_vs_png = (avg_png_size - avg_avif_80_size) / avg_png_size * 100
        avif_wip_savings_vs_png = (
            (avg_png_size - avg_avif_wip_size) / avg_png_size * 100
        )
        print(
            f"JPEG:                {jpeg_savings_vs_png:+.2f}% ({avg_jpeg_size / avg_png_size:.2%} of PNG size)"
        )
        print(
            f"JPEG (WIP):          {jpeg_wip_savings_vs_png:+.2f}% ({avg_jpeg_wip_size / avg_png_size:.2%} of PNG size)"
        )
        print(
            f"WebP:                {webp_savings_vs_png:+.2f}% ({avg_webp_size / avg_png_size:.2%} of PNG size)"
        )
        print(
            f"AVIF (Q80):          {avif_80_savings_vs_png:+.2f}% ({avg_avif_80_size / avg_png_size:.2%} of PNG size)"
        )
        print(
            f"AVIF (Q-WIP):        {avif_wip_savings_vs_png:+.2f}% ({avg_avif_wip_size / avg_png_size:.2%} of PNG size)"
        )

        # Per-image breakdown
        print("\n" + "=" * 80)
        print("PER-IMAGE BREAKDOWN")
        print("=" * 80)
        print("\nQuality Scores:")
        print("-" * 80)
        print(
            f"{'Image':<40} {'JPEG':<10} {'JPwip':<10} {'WebP':<10} {'AVIF Q80':<10} {'AVIF Qwip':<10} {'Diff JPw':<10} {'Diff WebP':<10} {'Diff Q80':<10} {'Diff Qwip':<10}"
        )
        print("-" * 80)

        for img_data in processed_images:
            diff_80 = img_data["avif_80_score"] - img_data["jpeg_score"]
            diff_wip = img_data["avif_wip_score"] - img_data["jpeg_score"]
            diff_jpeg_wip = img_data["jpeg_wip_score"] - img_data["jpeg_score"]
            diff_webp = img_data["webp_score"] - img_data["jpeg_score"]
            diff_webp_pct = (
                (diff_webp / img_data["jpeg_score"] * 100)
                if img_data["jpeg_score"] > 0
                else 0
            )
            diff_80_pct = (
                (diff_80 / img_data["jpeg_score"] * 100)
                if img_data["jpeg_score"] > 0
                else 0
            )
            diff_wip_pct = (
                (diff_wip / img_data["jpeg_score"] * 100)
                if img_data["jpeg_score"] > 0
                else 0
            )
            diff_jpeg_wip_pct = (
                (diff_jpeg_wip / img_data["jpeg_score"] * 100)
                if img_data["jpeg_score"] > 0
                else 0
            )
            print(
                f"{img_data['name']:<40} {img_data['jpeg_score']:<10.4f} {img_data['jpeg_wip_score']:<10.4f} {img_data['webp_score']:<10.4f} {img_data['avif_80_score']:<10.4f} {img_data['avif_wip_score']:<10.4f} {diff_jpeg_wip_pct:+.2f}%{'':<4} {diff_webp_pct:+.2f}%{'':<4} {diff_80_pct:+.2f}%{'':<4} {diff_wip_pct:+.2f}%"
            )

        print("\nFile Sizes (KB) and Savings vs JPEG:")
        print("-" * 80)
        print(
            f"{'Image':<35} {'PNG':<10} {'JPEG':<10} {'JPwip':<10} {'WebP':<10} {'AVIF80':<10} {'AVIFwip':<10} {'JPwip%':<8} {'WebP%':<8} {'AVIF80%':<8} {'AVIFwip%':<8}"
        )
        print("-" * 80)

        for img_data in processed_images:
            webp_savings = (
                (
                    (img_data["jpeg_size"] - img_data["webp_size"])
                    / img_data["jpeg_size"]
                    * 100
                )
                if img_data["jpeg_size"] > 0
                else 0
            )
            avif_80_savings = (
                (
                    (img_data["jpeg_size"] - img_data["avif_80_size"])
                    / img_data["jpeg_size"]
                    * 100
                )
                if img_data["jpeg_size"] > 0
                else 0
            )
            avif_wip_savings = (
                (
                    (img_data["jpeg_size"] - img_data["avif_wip_size"])
                    / img_data["jpeg_size"]
                    * 100
                )
                if img_data["jpeg_size"] > 0
                else 0
            )
            jpeg_wip_savings = (
                (
                    (img_data["jpeg_size"] - img_data["jpeg_wip_size"])
                    / img_data["jpeg_size"]
                    * 100
                )
                if img_data["jpeg_size"] > 0
                else 0
            )
            print(
                f"{img_data['name']:<35} {img_data['png_size'] / 1024:<10.1f} {img_data['jpeg_size'] / 1024:<10.1f} {img_data['jpeg_wip_size'] / 1024:<10.1f} {img_data['webp_size'] / 1024:<10.1f} {img_data['avif_80_size'] / 1024:<10.1f} {img_data['avif_wip_size'] / 1024:<10.1f} {jpeg_wip_savings:+.1f}%{'':<2} {webp_savings:+.1f}%{'':<2} {avif_80_savings:+.1f}%{'':<2} {avif_wip_savings:+.1f}%"
            )

    print("\n" + "=" * 80)
    print(f"Processing complete! Output saved to {output_dir}")
    print("=" * 80)


if __name__ == "__main__":
    main()
