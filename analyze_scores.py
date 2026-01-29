#!/usr/bin/env python3

import duckdb
import pandas as pd


def main():
    # Connect to DuckDB in-memory database
    con = duckdb.connect(database=":memory:")

    # Read the CSV file
    print("Loading CSV data...")
    df = pd.read_csv("jpeg-webp-avif-scores.csv")

    # Show column info for debugging
    print(f"Number of columns: {len(df.columns)}")
    print("First few column names:", df.columns[:10].tolist())

    # Process ssimulacra2 data
    # Extract JPEG ssimulacra2 data
    jpeg_ssim_cols = [
        col for col in df.columns if "JPEG Q" in col and "ssimulacra2" in col
    ]
    jpeg_ssim_data = []

    for col in jpeg_ssim_cols:
        # Extract quality number from column name like 'JPEG Q40 ssimulacra2'
        parts = col.split(" ")
        quality_part = parts[1]  # This should be 'Q40'
        quality = int(quality_part.replace("Q", ""))  # Remove 'Q' and convert to int
        temp_df = df[["File", col]].copy()
        temp_df.columns = ["File", "ssimulacra2"]
        temp_df["format"] = "JPEG"
        temp_df["quality"] = quality
        jpeg_ssim_data.append(temp_df)

    # Extract WebP ssimulacra2 data
    webp_ssim_cols = [
        col for col in df.columns if "WEBP Q" in col and "ssimulacra2" in col
    ]
    webp_ssim_data = []

    for col in webp_ssim_cols:
        # Extract quality number from column name like 'WEBP Q40 ssimulacra2'
        parts = col.split(" ")
        quality_part = parts[1]  # This should be 'Q40'
        quality = int(quality_part.replace("Q", ""))  # Remove 'Q' and convert to int
        temp_df = df[["File", col]].copy()
        temp_df.columns = ["File", "ssimulacra2"]
        temp_df["format"] = "WEBP"
        temp_df["quality"] = quality
        webp_ssim_data.append(temp_df)

    # Extract AVIF ssimulacra2 data
    avif_ssim_cols = [
        col for col in df.columns if "AVIF Q" in col and "ssimulacra2" in col
    ]
    avif_ssim_data = []

    for col in avif_ssim_cols:
        # Extract quality number from column name like 'AVIF Q40 ssimulacra2'
        parts = col.split(" ")
        quality_part = parts[1]  # This should be 'Q40'
        quality = int(quality_part.replace("Q", ""))  # Remove 'Q' and convert to int
        temp_df = df[["File", col]].copy()
        temp_df.columns = ["File", "ssimulacra2"]
        temp_df["format"] = "AVIF"
        temp_df["quality"] = quality
        avif_ssim_data.append(temp_df)

    # Process file size data
    # Extract JPEG file size data
    jpeg_size_cols = [
        col for col in df.columns if "JPEG Q" in col and "file size" in col
    ]
    jpeg_size_data = []

    for col in jpeg_size_cols:
        # Extract quality number from column name like 'JPEG Q40 file size'
        parts = col.split(" ")
        quality_part = parts[1]  # This should be 'Q40'
        quality = int(quality_part.replace("Q", ""))  # Remove 'Q' and convert to int
        temp_df = df[["File", col]].copy()
        temp_df.columns = ["File", "file_size"]
        temp_df["format"] = "JPEG"
        temp_df["quality"] = quality
        jpeg_size_data.append(temp_df)

    # Extract WebP file size data
    webp_size_cols = [
        col for col in df.columns if "WEBP Q" in col and "file size" in col
    ]
    webp_size_data = []

    for col in webp_size_cols:
        # Extract quality number from column name like 'WEBP Q40 file size'
        parts = col.split(" ")
        quality_part = parts[1]  # This should be 'Q40'
        quality = int(quality_part.replace("Q", ""))  # Remove 'Q' and convert to int
        temp_df = df[["File", col]].copy()
        temp_df.columns = ["File", "file_size"]
        temp_df["format"] = "WEBP"
        temp_df["quality"] = quality
        webp_size_data.append(temp_df)

    # Extract AVIF file size data
    avif_size_cols = [
        col for col in df.columns if "AVIF Q" in col and "file size" in col
    ]
    avif_size_data = []

    for col in avif_size_cols:
        # Extract quality number from column name like 'AVIF Q40 file size'
        parts = col.split(" ")
        quality_part = parts[1]  # This should be 'Q40'
        quality = int(quality_part.replace("Q", ""))  # Remove 'Q' and convert to int
        temp_df = df[["File", col]].copy()
        temp_df.columns = ["File", "file_size"]
        temp_df["format"] = "AVIF"
        temp_df["quality"] = quality
        avif_size_data.append(temp_df)

    # Combine all data
    print(
        f"SSIMULACRA2 - JPEG columns: {len(jpeg_ssim_cols)}, WEBP columns: {len(webp_ssim_cols)}, AVIF columns: {len(avif_ssim_cols)}"
    )
    print(
        f"File Size - JPEG columns: {len(jpeg_size_cols)}, WEBP columns: {len(webp_size_cols)}, AVIF columns: {len(avif_size_cols)}"
    )

    all_ssim_data = pd.concat(
        jpeg_ssim_data + webp_ssim_data + avif_ssim_data, ignore_index=True
    )
    all_size_data = pd.concat(
        jpeg_size_data + webp_size_data + avif_size_data, ignore_index=True
    )

    # Create tables in DuckDB
    con.execute("CREATE TABLE scores_long AS SELECT * FROM all_ssim_data")
    con.execute("CREATE TABLE sizes_long AS SELECT * FROM all_size_data")

    # Calculate median scores for each format and quality setting
    print("Calculating median scores...")
    con.execute("""
        CREATE TABLE median_scores AS
        SELECT
            format,
            quality,
            MEDIAN(ssimulacra2) as median_ssimulacra2
        FROM scores_long
        GROUP BY format, quality
        ORDER BY format, quality
    """)

    # Calculate median file sizes for each format and quality setting
    print("Calculating median file sizes...")
    con.execute("""
        CREATE TABLE median_sizes AS
        SELECT
            format,
            quality,
            MEDIAN(file_size) as median_file_size
        FROM sizes_long
        GROUP BY format, quality
        ORDER BY format, quality
    """)

    # Display some sample median scores and sizes
    sample_scores = con.execute("""
        SELECT
            s.format,
            s.quality,
            ROUND(s.median_ssimulacra2, 2) as median_ssimulacra2,
            sz.median_file_size
        FROM median_scores s
        JOIN median_sizes sz ON s.format = sz.format AND s.quality = sz.quality
        WHERE s.quality IN (40, 50, 60, 70, 80, 90)
        ORDER BY s.format, s.quality
    """).fetchdf()
    print("\nSample median scores and file sizes:")
    print(sample_scores)

    # Find closest match WebP and AVIF quality for each JPEG quality from 40 to 90
    print("Finding closest matches...")
    con.execute("""
        CREATE TABLE closest_matches AS
        WITH jpeg_medians AS (
            SELECT
                ms.quality as jpeg_quality,
                ms.median_ssimulacra2 as jpeg_score,
                mz.median_file_size as jpeg_size
            FROM median_scores ms
            JOIN median_sizes mz ON ms.format = mz.format AND ms.quality = mz.quality
            WHERE ms.format = 'JPEG' AND ms.quality BETWEEN 40 AND 90
        ),
        webp_medians AS (
            SELECT
                ms.quality as webp_quality,
                ms.median_ssimulacra2 as webp_score,
                mz.median_file_size as webp_size
            FROM median_scores ms
            JOIN median_sizes mz ON ms.format = mz.format AND ms.quality = mz.quality
            WHERE ms.format = 'WEBP'
        ),
        avif_medians AS (
            SELECT
                ms.quality as avif_quality,
                ms.median_ssimulacra2 as avif_score,
                mz.median_file_size as avif_size
            FROM median_scores ms
            JOIN median_sizes mz ON ms.format = mz.format AND ms.quality = mz.quality
            WHERE ms.format = 'AVIF'
        ),
        jpeg_webp_combinations AS (
            SELECT
                j.jpeg_quality,
                j.jpeg_score,
                j.jpeg_size,
                w.webp_quality,
                w.webp_score,
                w.webp_size,
                ABS(j.jpeg_score - w.webp_score) as webp_diff
            FROM jpeg_medians j
            CROSS JOIN webp_medians w
        ),
        jpeg_avif_combinations AS (
            SELECT
                j.jpeg_quality,
                j.jpeg_score,
                j.jpeg_size,
                a.avif_quality,
                a.avif_score,
                a.avif_size,
                ABS(j.jpeg_score - a.avif_score) as avif_diff
            FROM jpeg_medians j
            CROSS JOIN avif_medians a
        ),
        best_webp_matches AS (
            SELECT
                jpeg_quality,
                jpeg_score,
                jpeg_size,
                webp_quality,
                webp_score,
                webp_size
            FROM (
                SELECT *,
                    ROW_NUMBER() OVER (PARTITION BY jpeg_quality ORDER BY webp_diff ASC) as rn
                FROM jpeg_webp_combinations
            ) ranked
            WHERE rn = 1
        ),
        best_avif_matches AS (
            SELECT
                jpeg_quality,
                jpeg_score,
                jpeg_size,
                avif_quality,
                avif_score,
                avif_size
            FROM (
                SELECT *,
                    ROW_NUMBER() OVER (PARTITION BY jpeg_quality ORDER BY avif_diff ASC) as rn
                FROM jpeg_avif_combinations
            ) ranked
            WHERE rn = 1
        )
        SELECT
            bwm.jpeg_quality,
            ROUND(bwm.jpeg_score, 2) as jpeg_score,
            bwm.jpeg_size,
            bwm.webp_quality,
            ROUND(bwm.webp_score, 2) as webp_score,
            bwm.webp_size,
            bam.avif_quality,
            ROUND(bam.avif_score, 2) as avif_score,
            bam.avif_size
        FROM best_webp_matches bwm
        JOIN best_avif_matches bam ON bwm.jpeg_quality = bam.jpeg_quality
        ORDER BY bwm.jpeg_quality
    """)

    # Export results to CSV
    print("Exporting results to CSV...")
    con.execute("""
        COPY closest_matches TO 'closest_matches.csv' (HEADER TRUE, DELIMITER ',')
    """)

    # Display results
    result = con.execute(
        "SELECT * FROM closest_matches ORDER BY jpeg_quality"
    ).fetchdf()
    print("\nClosest matches for JPEG qualities 40-90 (with file sizes):")
    print(result.to_string(index=False))

    print("\nResults have been saved to 'closest_matches.csv'")

    con.close()


if __name__ == "__main__":
    main()
