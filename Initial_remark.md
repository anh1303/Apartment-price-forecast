# Đánh giá sơ bộ dữ liệu và hướng tiếp cận dự án dự đoán giá căn hộ chung cư

## 1. Tên đề tài đề xuất

**Phân tích các yếu tố ảnh hưởng và dự đoán giá căn hộ chung cư tại Việt Nam từ dữ liệu tin đăng bất động sản**

Tên đề tài này phù hợp vì không giới hạn phương pháp ở học máy. Dự án có thể triển khai bằng các mô hình thống kê, hồi quy, mô hình cây quyết định, mô hình boosting hoặc các phương pháp kết hợp dữ liệu văn bản.

---

## 2. Mục tiêu dự án

Dự án hướng đến việc xây dựng mô hình dự đoán **giá căn hộ chung cư** dựa trên dữ liệu tin đăng bất động sản tại Việt Nam.

- **Biến mục tiêu:** `price`
- **Đối tượng phân tích:** các bản ghi có `property_type_name = "Căn hộ chung cư"`
- **Dữ liệu đầu vào tiềm năng:** diện tích, vị trí địa lý, tên dự án, số phòng, hướng, thời gian đăng tin, tiêu đề và mô tả tin đăng.

Mục tiêu không chỉ là dự đoán giá, mà còn phân tích xem các nhóm đặc trưng như **diện tích**, **vị trí**, **dự án** và **nội dung mô tả** ảnh hưởng như thế nào đến giá căn hộ.

---

## 3. Mô tả nguồn dữ liệu

Dataset được lấy từ **Tinix Vietnam Real Estate Listings (2025-2026)** trên Hugging Face.

Sau khi lọc riêng nhóm **căn hộ chung cư**, dữ liệu có:

| Tiêu chí | Giá trị |
|---|---:|
| Số dòng ban đầu sau lọc căn hộ chung cư | 762,800 |
| Số dòng có `price` và `area` hợp lệ | 677,895 |
| Tỷ lệ giữ lại sau lọc `price > 0` và `area > 0` | 88.87% |
| Số tỉnh/thành | 53 |
| Số quận/huyện | 198 |
| Số dòng sau làm sạch sơ bộ theo outlier | 654,217 |
| Tỷ lệ giữ lại sau làm sạch sơ bộ | 96.51% so với tập hợp lệ |

Nhìn chung, quy mô dữ liệu đủ lớn để triển khai cả mô hình thống kê và mô hình dự đoán phức tạp hơn.

---

## 4. Đánh giá chất lượng dữ liệu

### 4.1. Các cột có chất lượng tốt

Một số cột quan trọng có mức độ đầy đủ cao và nên được ưu tiên sử dụng:

| Cột | Tỷ lệ thiếu | Đánh giá |
|---|---:|---|
| `area` | 0.00% | Rất quan trọng, nên dùng |
| `province_name` | 0.00% | Rất quan trọng, nên dùng |
| `name` | 0.00% | Có thể trích đặc trưng văn bản |
| `description` | 0.00% | Rất có giá trị để trích đặc trưng văn bản |
| `district_name` | 5.72% | Nên dùng |
| `bedroom_count` | 6.94% | Nên dùng sau xử lý thiếu/outlier |
| `price` | 8.26% | Là biến mục tiêu, dòng thiếu giá không dùng để train supervised model |
| `bathroom_count` | 10.52% | Nên dùng sau xử lý thiếu |
| `project_name` | 12.54% | Nên dùng, nhưng cần xử lý missing và high-cardinality |
| `ward_name` | 20.86% | Có thể dùng, nhưng cần xử lý missing |

### 4.2. Các cột cần thận trọng hoặc không nên dùng trực tiếp

Một số cột có tỷ lệ thiếu quá cao:

| Cột | Tỷ lệ thiếu | Đánh giá |
|---|---:|---|
| `floor_count` | 99.87% | Không nên dùng trong mô hình chính |
| `frontage_width` | 99.85% | Không phù hợp với căn hộ, nên loại |
| `house_depth` | 99.93% | Không phù hợp với căn hộ, nên loại |
| `road_width` | 99.96% | Không nên dùng trong mô hình chính |
| `house_direction` | 56.72% | Có thể thử nghiệm, nhưng không nên phụ thuộc |
| `balcony_direction` | 57.96% | Có thể thử nghiệm, nhưng không nên phụ thuộc |
| `street_name` | 47.71% | Có giá trị nhưng thiếu nhiều, cần xử lý cẩn thận |

Các cột như `frontage_width`, `house_depth`, `road_width` phù hợp hơn với nhà đất hoặc nhà mặt phố, không phù hợp để làm đặc trưng chính cho căn hộ chung cư.

---

## 5. Phân tích sơ bộ biến mục tiêu và biến quan trọng

### 5.1. Giá bán `price`

Thống kê trên tập có `price` và `area` hợp lệ:

| Thống kê | Giá trị |
|---|---:|
| Trung vị | 4,900,000,000 |
| 5% | 1,750,000,000 |
| 95% | 16,500,000,000 |
| 99% | 37,000,000,000 |
| Giá trị lớn nhất | 999,910,000,000,000 |

Dữ liệu giá có phân phối lệch mạnh và tồn tại giá trị cực trị rất lớn. Do đó, không nên dự đoán trực tiếp `price` bằng mô hình tuyến tính thông thường mà không biến đổi. Nên cân nhắc dùng:

```text
target = log1p(price)
```

Sau khi dự đoán, có thể chuyển ngược về giá trị tiền tệ bằng `expm1`.

### 5.2. Diện tích `area`

| Thống kê | Giá trị |
|---|---:|
| Trung vị | 73 m² |
| 5% | 42 m² |
| 95% | 143 m² |
| 99% | 235 m² |
| Giá trị lớn nhất | 82,000,000 m² |

Diện tích có một số giá trị bất thường rất lớn. Vì vậy cần xử lý outlier trước khi huấn luyện mô hình.

### 5.3. Giá trên mỗi mét vuông `price_per_m2`

`price_per_m2` được tạo để phân tích:

```text
price_per_m2 = price / area
```

| Thống kê | Giá trị |
|---|---:|
| Trung vị | 68,000,000 |
| 5% | 30,882,352.94 |
| 95% | 144,736,842.11 |
| 99% | 261,864,406.78 |

Biến này rất hữu ích để phân tích thị trường, phát hiện outlier và xây dựng baseline, nhưng **không nên dùng trực tiếp làm input nếu mục tiêu là dự đoán `price`**, vì nó được tính từ chính biến mục tiêu.

---

## 6. Outlier và vấn đề dữ liệu bất thường

EDA cho thấy có nhiều dòng bất thường, ví dụ:

- `price` chỉ vài nghìn đồng.
- `price` lên đến hàng nghìn tỷ hoặc lớn hơn.
- `area` lên đến hàng chục triệu m².
- `price_per_m2` quá thấp hoặc quá cao so với mặt bằng thông thường.

Notebook đã gợi ý ngưỡng lọc sơ bộ theo percentile:

| Biến | Ngưỡng thấp | Ngưỡng cao |
|---|---:|---:|
| `area` | 30 m² | 235 m² |
| `price_per_m2` | 21,142,857 | 261,864,406.78 |

Số dòng bị đánh dấu outlier sơ bộ là **23,678 dòng**, chiếm khoảng **3.49%** tập hợp lệ. Sau khi lọc sơ bộ, dữ liệu còn **654,217 dòng**, vẫn đủ lớn để tiếp tục xây dựng mô hình.

---

## 7. Phân tích địa lý

Dữ liệu có độ phủ địa lý rộng với **53 tỉnh/thành** và **198 quận/huyện**, nhưng tập trung mạnh ở một số khu vực lớn.

### 7.1. Top tỉnh/thành theo số lượng tin

| Tỉnh/thành | Số lượng tin | Giá trung vị | Giá/m² trung vị |
|---|---:|---:|---:|
| Hồ Chí Minh | 265,059 | 5,000,000,000 | 66,216,216 |
| Hà Nội | 257,639 | 6,500,000,000 | 80,357,142 |
| Bình Dương | 51,883 | 2,390,000,000 | 39,583,333 |
| Đà Nẵng | 23,000 | 4,400,000,000 | 68,493,150 |
| Hưng Yên | 21,696 | 4,200,000,000 | 66,666,666 |
| Khánh Hòa | 14,249 | 3,200,000,000 | 49,319,727 |

Nhận xét:

- Dữ liệu tập trung chủ yếu ở **TP.HCM** và **Hà Nội**.
- Giá/m² trung vị tại Hà Nội cao hơn TP.HCM trong tập dữ liệu này.
- Các tỉnh như Bình Dương, Hưng Yên, Đà Nẵng, Khánh Hòa cũng có số lượng tin đáng kể.

### 7.2. Top quận/huyện theo số lượng tin

Một số khu vực có nhiều tin:

- Thủ Đức
- Quận 7
- Nam Từ Liêm
- Cầu Giấy
- Hoàng Mai
- Hà Đông
- Thanh Xuân
- Dĩ An
- Thuận An
- Văn Giang
- Gia Lâm

Vị trí địa lý là nhóm đặc trưng rất quan trọng và nên được đưa vào mô hình.

---

## 8. Phân tích thông tin dự án

`project_name` là biến quan trọng với căn hộ chung cư.

- Tỷ lệ thiếu: **12.54%**
- Số lượng dự án khác nhau: **2,857**

Một số dự án có nhiều tin:

| Dự án | Số lượng tin |
|---|---:|
| Vinhomes Ocean Park | 8,208 |
| The Origami – Vinhomes Grand Park | 3,999 |
| Masteri Trinity Square | 3,520 |
| Sun Urban City Hà Nam | 3,481 |
| MT Eastmark City | 3,090 |
| Mizuki Park | 2,948 |
| Vinhomes Central Park | 2,937 |
| Masteri Waterfront | 2,932 |
| The Sun Avenue | 2,916 |

Nhận xét:

- `project_name` nên được sử dụng vì có ý nghĩa lớn với giá căn hộ.
- Tuy nhiên đây là biến phân loại có nhiều giá trị, cần xử lý bằng kỹ thuật phù hợp.
- Không nên one-hot encoding toàn bộ dự án nếu số lượng quá lớn.
- Có thể gộp các dự án ít xuất hiện thành nhóm `Other`.
- Có thể dùng target encoding nhưng phải tránh rò rỉ dữ liệu.

---

## 9. Phân tích đặc điểm căn hộ

### 9.1. Số phòng ngủ `bedroom_count`

Phân phối chính:

| Số phòng ngủ | Số lượng |
|---:|---:|
| 1 | 79,377 |
| 2 | 350,677 |
| 3 | 182,183 |
| 4 | 19,285 |
| Thiếu | 43,214 |

Nhận xét:

- Căn hộ 2 phòng ngủ chiếm nhiều nhất.
- Căn hộ 3 phòng ngủ đứng thứ hai.
- Có một số giá trị bất thường như 20, 30, 73 phòng ngủ, cần xử lý outlier.

### 9.2. Số phòng tắm `bathroom_count`

Phân phối chính:

| Số phòng tắm | Số lượng |
|---:|---:|
| 1 | 137,370 |
| 2 | 438,011 |
| 3 | 28,583 |
| 4 | 5,924 |
| Thiếu | 66,459 |

Nhận xét:

- Căn hộ 2 phòng tắm chiếm nhiều nhất.
- Cần xử lý thiếu và loại các giá trị bất thường quá lớn.

### 9.3. Số tầng `floor_count`

`floor_count` thiếu khoảng **99.87%**, chỉ có 864 dòng hợp lệ trong tập đã lọc `price` và `area`. Do đó không nên dùng biến này trong mô hình chính.

---

## 10. Phân tích hướng nhà và hướng ban công

### 10.1. `house_direction`

- Tỷ lệ thiếu: **56.59%**
- Một số hướng phổ biến: Đông Nam, Tây Bắc, Đông Bắc, Nam, Đông, Tây Nam.

### 10.2. `balcony_direction`

- Tỷ lệ thiếu: **57.90%**
- Một số hướng phổ biến: Đông Nam, Nam, Đông Bắc, Tây Bắc, Tây Nam.

Nhận xét:

- Hai biến này có thể có giá trị, nhưng tỷ lệ thiếu cao.
- Nên xem đây là biến thử nghiệm, không nên là biến chính.
- Có thể mã hóa missing thành nhóm `Unknown`.

---

## 11. Phân tích thời gian đăng tin

`published_at` có dữ liệu chủ yếu trong giai đoạn:

- Từ: **2025-06-01**
- Đến: **2026-03-30**

Phân bố theo năm:

| Năm | Số lượng |
|---:|---:|
| 2025 | 484,134 |
| 2026 | 189,127 |
| Thiếu/không parse được | 4,634 |

Hướng sử dụng:

- Tạo đặc trưng `year`, `month`, `quarter`.
- Có thể chia train/test theo thời gian để đánh giá thực tế hơn.
- Không nên chỉ chia random nếu muốn mô phỏng khả năng dự đoán trên tin đăng mới.

---

## 12. Phân tích văn bản tin đăng

Dữ liệu có hai cột văn bản quan trọng:

- `name`
- `description`

### 12.1. Độ dài văn bản

| Cột | Trung bình | Trung vị | 95% | Max |
|---|---:|---:|---:|---:|
| `name_length` | 80.13 | 84 | 99 | 120 |
| `description_length` | 652.62 | 545 | 1,529 | 4,865 |

Nhận xét:

- `description` có độ dài đủ lớn để trích đặc trưng.
- Có thể dùng keyword thủ công, TF-IDF hoặc embedding văn bản.

### 12.2. Một số keyword đáng chú ý

| Keyword | Số lượng | Tỷ lệ | Giá/m² trung vị |
|---|---:|---:|---:|
| nội thất | 385,038 | 56.80% | 71,022,727 |
| pháp lý | 225,699 | 33.29% | 67,600,000 |
| ban công | 210,714 | 31.08% | 71,739,130 |
| trung tâm | 196,114 | 28.93% | 66,666,666 |
| cao cấp | 157,016 | 23.16% | 75,485,837 |
| sổ hồng | 121,237 | 17.88% | 58,490,566 |
| full nội thất | 105,206 | 15.52% | 72,468,831 |
| view sông | 36,848 | 5.44% | 80,851,063 |
| metro | 36,774 | 5.42% | 61,810,961 |
| duplex | 21,635 | 3.19% | 83,646,938 |
| penthouse | 18,683 | 2.76% | 90,909,090 |
| luxury | 3,044 | 0.45% | 86,334,876 |

Nhận xét:

- Văn bản mô tả có nhiều thông tin có khả năng liên quan đến giá.
- Các từ như `cao cấp`, `view sông`, `duplex`, `penthouse`, `luxury` có giá/m² trung vị cao hơn mặt bằng chung.
- Đây là lý do nên thử mô hình có thêm đặc trưng văn bản.

---

## 13. Các biến nên sử dụng trong mô hình

### 13.1. Nhóm biến nên dùng chính

| Nhóm | Biến |
|---|---|
| Biến vật lý | `area`, `bedroom_count`, `bathroom_count` |
| Vị trí | `province_name`, `district_name`, `ward_name` |
| Dự án | `project_name` |
| Thời gian | `published_at`, `year`, `month`, `quarter` |
| Văn bản cơ bản | `name_length`, `description_length` |
| Keyword văn bản | `has_noi_that`, `has_full_noi_that`, `has_view_song`, `has_ban_cong`, `has_cao_cap`, `has_so_hong`, `has_metro`, `has_duplex`, `has_penthouse` |

### 13.2. Nhóm biến có thể thử nghiệm

| Nhóm | Biến | Ghi chú |
|---|---|---|
| Đường/phố | `street_name` | Thiếu 47.71%, cần mã hóa missing |
| Hướng | `house_direction`, `balcony_direction` | Thiếu hơn 56%, chỉ nên dùng thử |
| Văn bản nâng cao | TF-IDF từ `name` và `description` | Có thể cải thiện dự đoán |

### 13.3. Nhóm biến nên loại khỏi mô hình chính

| Biến | Lý do |
|---|---|
| `floor_count` | Thiếu 99.87% |
| `frontage_width` | Thiếu 99.85%, không phù hợp với căn hộ |
| `house_depth` | Thiếu 99.93%, không phù hợp với căn hộ |
| `road_width` | Thiếu 99.96%, không phù hợp với căn hộ |
| `price_per_m2` | Không dùng làm input vì được tính từ `price`, có nguy cơ leakage |

---

## 14. Hướng tiền xử lý dữ liệu

### 14.1. Làm sạch dữ liệu

Các bước nên thực hiện:

1. Giữ các dòng có `price > 0` và `area > 0`.
2. Loại hoặc xử lý các dòng có `area` và `price_per_m2` quá bất thường.
3. Có thể dùng ngưỡng percentile:
   - `area` trong khoảng 1% đến 99%.
   - `price_per_m2` trong khoảng 1% đến 99%.
4. Chuẩn hóa các cột phân loại bị thiếu bằng giá trị `Unknown`.
5. Loại các cột thiếu quá nhiều và không phù hợp với căn hộ.
6. Kiểm tra trùng lặp tin đăng nếu cần.

### 14.2. Xử lý biến mục tiêu

Nên dùng:

```python
y = np.log1p(price)
```

Lý do:

- Giá bất động sản lệch phải rất mạnh.
- Giảm ảnh hưởng của outlier.
- Giúp mô hình hồi quy tuyến tính hoạt động ổn định hơn.

### 14.3. Xử lý biến phân loại

Các cột như `province_name`, `district_name`, `ward_name`, `project_name`, `street_name` là biến phân loại.

Có thể xử lý bằng:

- One-hot encoding cho biến có ít giá trị.
- Frequency encoding.
- Target encoding có kiểm soát.
- CatBoost encoding nếu dùng CatBoost.
- Gộp nhóm hiếm thành `Other`.

Với `project_name`, nên tránh one-hot toàn bộ nếu số lượng dự án lớn. Có thể giữ top dự án phổ biến và gộp phần còn lại.

### 14.4. Xử lý văn bản

Có thể đi theo 3 mức:

**Mức 1: đặc trưng thủ công**

Tạo các biến nhị phân:

```text
has_noi_that
has_view_song
has_view_bien
has_ban_cong
has_so_hong
has_phap_ly
has_metro
has_duplex
has_penthouse
has_luxury
```

**Mức 2: TF-IDF**

Dùng TF-IDF cho `name` và `description`, sau đó kết hợp với mô hình hồi quy hoặc mô hình cây.

**Mức 3: Embedding**

Dùng sentence embedding tiếng Việt hoặc multilingual embedding để biểu diễn mô tả tin đăng. Cách này phức tạp hơn nhưng có thể cho kết quả tốt hơn.

---

## 15. Hướng tiếp cận mô hình

Nên triển khai theo nhiều mức để dễ so sánh và giải thích.

### 15.1. Baseline 1: Dự đoán bằng giá trung vị

Mô hình đơn giản nhất:

```text
Dự đoán mọi căn hộ bằng giá trung vị của tập train
```

Mục đích:

- Làm mốc so sánh tối thiểu.
- Nếu mô hình phức tạp không vượt qua baseline này thì mô hình chưa có giá trị.

### 15.2. Baseline 2: Giá/m² trung vị theo khu vực

Công thức:

```text
predicted_price = area × median_price_per_m2_by_location
```

Có thể thử theo các cấp:

1. Trung vị giá/m² toàn quốc.
2. Trung vị giá/m² theo tỉnh/thành.
3. Trung vị giá/m² theo quận/huyện.
4. Trung vị giá/m² theo phường/xã.
5. Trung vị giá/m² theo dự án.

Khi không có dữ liệu ở cấp nhỏ, dùng fallback:

```text
project → ward → district → province → global
```

Baseline này rất quan trọng vì phản ánh cách định giá bất động sản thực tế.

### 15.3. Mô hình thống kê

Các mô hình nên thử:

| Mô hình | Vai trò |
|---|---|
| Linear Regression | Baseline thống kê dễ hiểu |
| Ridge Regression | Giảm overfit khi có nhiều biến |
| Lasso Regression | Có khả năng chọn biến |
| Elastic Net | Kết hợp Ridge và Lasso |
| Quantile Regression | Hữu ích nếu muốn dự đoán khoảng giá hoặc trung vị |
| GAM - Generalized Additive Model | Có thể mô hình hóa quan hệ phi tuyến giữa giá và diện tích |

Với các mô hình này, nên dùng target `log1p(price)` và encode biến phân loại phù hợp.

### 15.4. Mô hình cây và ensemble

Các mô hình nên thử:

| Mô hình | Vai trò |
|---|---|
| Decision Tree Regressor | Dễ giải thích nhưng dễ overfit |
| Random Forest Regressor | Ổn định hơn cây đơn |
| Extra Trees Regressor | Có thể dùng làm mô hình so sánh |
| Gradient Boosting | Mạnh hơn hồi quy tuyến tính |
| XGBoost | Mạnh với dữ liệu bảng |
| LightGBM | Tốt cho dữ liệu lớn |
| CatBoost | Rất phù hợp với nhiều biến categorical |

Trong dự án này, **CatBoost** là lựa chọn rất đáng thử vì dữ liệu có nhiều biến phân loại như tỉnh, quận, phường, đường, dự án, hướng nhà và hướng ban công.

### 15.5. Mô hình có văn bản

Có thể xây dựng các phiên bản:

| Phiên bản | Input |
|---|---|
| Model A | Chỉ dùng biến số và vị trí |
| Model B | Biến số + vị trí + project_name |
| Model C | Model B + keyword thủ công |
| Model D | Model B + TF-IDF từ `name` và `description` |

Cách này giúp đánh giá xem văn bản mô tả có thật sự cải thiện dự đoán giá hay không.

---

## 16. Cách chia tập train/test

Không nên chỉ dùng random split nếu muốn đánh giá sát thực tế.

Đề xuất:

### Cách 1: Chia theo thời gian

- Train: tin đăng cũ hơn.
- Test: tin đăng mới hơn.

Ưu điểm:

- Mô phỏng tình huống thực tế: dùng dữ liệu quá khứ để dự đoán dữ liệu tương lai.
- Tránh kết quả quá lạc quan.

### Cách 2: Random split có kiểm soát

Có thể dùng để so sánh ban đầu, nhưng cần ghi rõ hạn chế.

### Cách 3: Group split theo dự án

Dùng để kiểm tra khả năng tổng quát hóa với dự án chưa xuất hiện trong train.

Ví dụ:

- Train trên một nhóm dự án.
- Test trên các dự án khác.

Cách này khó hơn nhưng có giá trị nghiên cứu cao.

---

## 17. Chỉ số đánh giá mô hình

Nên dùng nhiều chỉ số thay vì chỉ một chỉ số.

| Chỉ số | Ý nghĩa |
|---|---|
| MAE | Sai số tuyệt đối trung bình, dễ hiểu theo đơn vị VND |
| RMSE | Phạt mạnh lỗi lớn |
| RMSLE | Phù hợp khi target lệch mạnh và dùng log |
| MAPE | Sai số phần trăm, dễ diễn giải |
| Median Absolute Error | Ít bị ảnh hưởng bởi outlier hơn MAE |

Khuyến nghị:

- Dùng `MAE` và `Median Absolute Error` để giải thích thực tế.
- Dùng `RMSE` để đánh giá lỗi lớn.
- Dùng `RMSLE` nếu mô hình dự đoán trên thang log.

---

## 18. Khả năng giải thích mô hình

Để dự án có giá trị nghiên cứu, không nên chỉ báo cáo độ chính xác. Cần phân tích yếu tố ảnh hưởng đến giá.

Có thể dùng:

- Hệ số hồi quy với Linear/Ridge/Lasso.
- Feature importance với Random Forest, LightGBM, CatBoost.
- SHAP values để giải thích đóng góp của từng đặc trưng.
- So sánh giá/m² trung vị theo tỉnh, quận, dự án.
- Phân tích keyword trong mô tả và sự khác biệt giá/m².

Các câu hỏi nên trả lời:

1. Diện tích ảnh hưởng thế nào đến giá?
2. Vị trí địa lý ảnh hưởng mạnh đến mức nào?
3. `project_name` có làm tăng độ chính xác không?
4. Văn bản mô tả có giúp mô hình tốt hơn không?
5. Các từ khóa như `cao cấp`, `view sông`, `duplex`, `penthouse` có liên quan đến giá cao hơn không?
6. Mô hình thống kê có đủ tốt không, hay cần mô hình phi tuyến?

---

## 19. Đánh giá sơ bộ về tính phù hợp của đề tài

Dựa trên kết quả EDA, đề tài **nên tiếp tục triển khai**.

### Điểm mạnh

- Dữ liệu có quy mô lớn: hơn 760 nghìn tin căn hộ.
- Sau lọc `price` và `area`, vẫn còn hơn 677 nghìn dòng hợp lệ.
- `area`, `province_name`, `name`, `description` gần như đầy đủ.
- `project_name` có tỷ lệ thiếu chấp nhận được với bài toán căn hộ.
- Dữ liệu có độ phủ trên nhiều tỉnh/thành.
- Mô tả văn bản giàu thông tin, phù hợp để khai thác thêm.
- Có thể kết hợp phân tích thống kê và mô hình dự đoán.

### Hạn chế

- Có nhiều outlier ở `price`, `area`, `price_per_m2`.
- Một số giá có khả năng sai đơn vị, ví dụ giá vài nghìn đồng hoặc hàng nghìn tỷ.
- Dữ liệu tập trung mạnh ở Hà Nội và TP.HCM.
- Một số cột vật lý như tầng, mặt tiền, độ rộng đường thiếu quá nhiều.
- `project_name` là biến nhiều giá trị, cần xử lý cẩn thận để tránh overfit.
- Giá trong dataset là giá rao bán, không chắc là giá giao dịch thực tế.

### Kết luận

Đề tài có tính khả thi cao nếu tập trung vào các nhóm đặc trưng chính:

```text
diện tích + vị trí địa lý + dự án + số phòng + thời gian + văn bản mô tả
```

Không nên xây dựng đề tài dựa trên các cột thiếu nhiều như tầng, mặt tiền, độ rộng đường hay chiều sâu nhà. Cần có bước làm sạch outlier rõ ràng trước khi huấn luyện mô hình.

---

## 20. Lộ trình triển khai đề xuất

### Giai đoạn 1: Chuẩn bị dữ liệu

1. Tải dataset từ Hugging Face.
2. Lọc `property_type_name = "Căn hộ chung cư"`.
3. Giữ các dòng có `price > 0` và `area > 0`.
4. Tạo `price_per_m2` để phân tích.
5. Lọc outlier theo `area` và `price_per_m2`.
6. Lưu dữ liệu sạch sơ bộ.

### Giai đoạn 2: Phân tích dữ liệu

1. Phân tích phân phối giá, diện tích, giá/m².
2. Phân tích theo tỉnh/thành, quận/huyện, phường/xã.
3. Phân tích theo dự án.
4. Phân tích số phòng ngủ, phòng tắm.
5. Phân tích keyword trong mô tả.
6. Đánh giá dữ liệu thiếu và outlier.

### Giai đoạn 3: Xây dựng baseline

1. Baseline giá trung vị.
2. Baseline giá/m² trung vị toàn quốc.
3. Baseline giá/m² theo tỉnh.
4. Baseline giá/m² theo quận.
5. Baseline giá/m² theo dự án có fallback.

### Giai đoạn 4: Xây dựng mô hình

1. Linear Regression/Ridge/Lasso với `log1p(price)`.
2. Random Forest hoặc Extra Trees.
3. LightGBM/XGBoost.
4. CatBoost cho dữ liệu categorical.
5. Mô hình có thêm keyword hoặc TF-IDF.

### Giai đoạn 5: Đánh giá và giải thích

1. So sánh MAE, RMSE, RMSLE, MAPE.
2. So sánh mô hình có/không có `project_name`.
3. So sánh mô hình có/không có văn bản.
4. Phân tích feature importance/SHAP.
5. Viết kết luận về các yếu tố ảnh hưởng đến giá.

---

## 21. Cấu trúc thư mục gợi ý

```text
project/
├── data/
│   ├── vietnam_apartments.parquet
│   ├── vietnam_apartments_clean_eda.parquet
│   └── processed/
├── notebooks/
│   ├── 01_eda_vietnam_apartments.ipynb
│   ├── 02_preprocessing.ipynb
│   ├── 03_baseline_models.ipynb
│   └── 04_modeling_and_evaluation.ipynb
├── src/
│   ├── data_loader.py
│   ├── preprocessing.py
│   ├── features.py
│   ├── train.py
│   └── evaluate.py
├── reports/
│   ├── figures/
│   └── model_results.md
└── README.md
```

---

## 22. Kết luận chung

Dựa trên notebook EDA, bộ dữ liệu căn hộ chung cư là lựa chọn phù hợp để tiếp tục dự án. Dữ liệu có quy mô lớn, nhiều biến có giá trị dự đoán và có đủ thông tin để vừa xây dựng mô hình vừa phân tích các yếu tố ảnh hưởng đến giá.

Hướng tiếp cận phù hợp nhất là bắt đầu từ các mô hình thống kê đơn giản, sau đó so sánh với các mô hình phi tuyến và mô hình boosting. Phần văn bản từ `name` và `description` nên được khai thác vì có nhiều keyword liên quan đến giá. Kết quả cuối cùng nên tập trung vào cả hai mục tiêu: **dự đoán giá** và **giải thích yếu tố ảnh hưởng đến giá căn hộ chung cư tại Việt Nam**.
