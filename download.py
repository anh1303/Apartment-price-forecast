from datasets import load_dataset
import pandas as pd
from tqdm import tqdm
import os
import re

# =========================
# CẤU HÌNH
# =========================

DATASET_NAME = "tinixai/vietnam-real-estates"
SPLIT = "train"

OUTPUT_DIR = "data"
OUTPUT_PARQUET = os.path.join(OUTPUT_DIR, "vietnam_apartments.parquet")
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "vietnam_apartments.csv")

BATCH_SIZE = 10_000

os.makedirs(OUTPUT_DIR, exist_ok=True)


# =========================
# HÀM KIỂM TRA LOẠI BĐS
# =========================

def normalize_text(text):
    """
    Chuẩn hóa text để so khớp dễ hơn.
    """
    if text is None:
        return ""

    text = str(text).lower().strip()

    # Chuẩn hóa khoảng trắng
    text = re.sub(r"\s+", " ", text)

    return text


def is_apartment_type(property_type):
    """
    Lọc các loại liên quan đến căn hộ/chung cư.
    Có thể mở rộng thêm nếu dataset có nhãn khác.
    """
    text = normalize_text(property_type)

    apartment_keywords = [
        "căn hộ chung cư",
        "chung cư",
        "căn hộ",
        "apartment",
        "condo",
        "condominium"
    ]

    return any(keyword in text for keyword in apartment_keywords)


# =========================
# TẢI DATASET DẠNG STREAMING
# =========================

print("Đang tải dataset từ Hugging Face...")
print(f"Dataset: {DATASET_NAME}")

dataset = load_dataset(
    DATASET_NAME,
    split=SPLIT,
    streaming=True
)

filtered_rows = []
total_rows = 0
matched_rows = 0
part_id = 0
temp_files = []

print("Đang lọc các dòng thuộc nhóm căn hộ/chung cư...")

for row in tqdm(dataset):
    total_rows += 1

    property_type = row.get("property_type_name")

    if is_apartment_type(property_type):
        filtered_rows.append(row)
        matched_rows += 1

    # Ghi tạm theo batch để tránh đầy RAM
    if len(filtered_rows) >= BATCH_SIZE:
        df_part = pd.DataFrame(filtered_rows)

        temp_path = os.path.join(OUTPUT_DIR, f"apartments_part_{part_id}.parquet")
        df_part.to_parquet(temp_path, index=False)

        temp_files.append(temp_path)

        print(f"Đã lưu batch {part_id}: {len(df_part)} dòng")

        filtered_rows = []
        part_id += 1


# Lưu phần còn lại
if filtered_rows:
    df_part = pd.DataFrame(filtered_rows)

    temp_path = os.path.join(OUTPUT_DIR, f"apartments_part_{part_id}.parquet")
    df_part.to_parquet(temp_path, index=False)

    temp_files.append(temp_path)

    print(f"Đã lưu batch cuối {part_id}: {len(df_part)} dòng")


# =========================
# GỘP CÁC FILE PARQUET
# =========================

print("Đang gộp các file tạm...")

if len(temp_files) == 0:
    print("Không tìm thấy dòng nào thuộc nhóm căn hộ/chung cư.")
else:
    df_all = pd.concat(
        [pd.read_parquet(file) for file in temp_files],
        ignore_index=True
    )

    print("Tổng số dòng đã đọc:", total_rows)
    print("Tổng số dòng căn hộ/chung cư:", matched_rows)
    print("Các giá trị property_type_name tìm thấy:")
    print(df_all["property_type_name"].value_counts(dropna=False))

    # Lưu file chính
    df_all.to_parquet(OUTPUT_PARQUET, index=False)
    df_all.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    print(f"Đã lưu file Parquet: {OUTPUT_PARQUET}")
    print(f"Đã lưu file CSV: {OUTPUT_CSV}")

    # Xóa file tạm
    for file in temp_files:
        os.remove(file)

    print("Hoàn tất.")